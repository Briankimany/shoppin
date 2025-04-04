from .database_index import Database , PayoutModel , OrderModel , ProductModel  
from app.models.order_item import OrderItem , VendorOrder
from sqlalchemy import func
from sqlalchemy.orm import Session
import requests
from config.config import JSONConfig
import json
import time
from app.models.vendor import Vendor
from app.routes.logger import LOG
from app.models.session_tracking import SessionTracking
from datetime import datetime
import humanize

from datetime import timedelta

class VendorObj:
    """
    Manages vendor-related operations, including updating details, verifying vendors, 
    adding/viewing products, tracking orders, and managing payouts.
    """

    def __init__(self, vendor_id, db_session:Session):
        """
        Initializes the Vendor instance.

        Args:
            vendor_id (int): The unique identifier of the vendor.
            db_session (Session): The database session instance.
        """
        self.vendor_id = vendor_id
        self.db_session = db_session
        self.db = Database(session=db_session)
        self.vendor_table = self.db.get_vendor(vendor_id=vendor_id)
        self.config = JSONConfig(json_path="config.json")
        

    @staticmethod
    def get_all_vendors(db_session:Session):
        return Database(db_session).get_all_vendors()
    @staticmethod
    def get_vendor_by(db_session: Session ,key , value):
        vendor = db_session.query(Vendor).filter(getattr(Vendor , key) == value).first()
        return vendor
    
    @staticmethod
    def register_vendor(db_session:Session , data={}):
        LOG.VENDOR_LOGGER.info(f"Creating/updating a new vendor data: {data}")
        try:
            vendor =VendorObj.get_vendor_by(db_session ,'name' , data.get('name'))
            if vendor:
                vendorobj = VendorObj(vendor_id=vendor.id , db_session=db_session)
            
                vendorobj.update_details(data)
                return vendorobj
            else:
                new_vendor = Vendor(**data)
                db_session.add(new_vendor)
                db_session.commit()
                LOG.VENDOR_LOGGER.info("Done...")
            return VendorObj(new_vendor.id ,db_session)
        except Exception as e:
            LOG.VENDOR_LOGGER.error(f"error during creation of new vendor E: {e}")
            return None
        
    def reload(self):
        self.vendor_table = self.db.get_vendor(vendor_id=self.vendor_id)

    def update_details(self,update_data):
        """
        Updates vendor details.

        Args:
            name (str, optional): Vendor's name.
            email (str, optional): Vendor's email address.
            phone (str, optional): Vendor's contact number.
            address (str, optional): Vendor's physical or business address.
            verified (bool, optional): Vendor verification status (True = verified, False = unverified).

        Returns:
            str: Confirmation message indicating update success.
        """
        self.db.update_vendor(self.vendor_id, update_data)
        return "Vendor details updated."

    def verify(self):
        """
        Verifies the vendor if not already verified.

        Returns:
            bool: True if verification is successful, False if already verified.
        """
        vendor = self.db.get_vendor(self.vendor_id)
        if vendor and vendor.verified:
            return False  # Already verified
        return self.db.verify_vendor(self.vendor_id)

    def add_product(self, name, price, product_type, description=None, stock=None, category=None, image_url=None, preview_url=None):
        """
        Adds a new product for the vendor.

        Args:
            name (str): Name of the product.
            price (float): Price of the product.
            product_type (int): Type of product (0 for Physical, 1 for Service).
            description (str, optional): Brief description of the product.
            stock (int, optional): Quantity available (only for physical products).
            category (str, optional): Category or classification of the product.
            image_url (str, optional): URL of the product image.
            preview_url (str, optional): URL for product preview (if applicable).

        Returns:
            int: The ID of the newly added product.
        """
        product = {k: v for k, v in locals().items() if k != "self" and v is not None}
        product["vendor_id"] = self.vendor_id  # Ensure vendor association
        return self.db.add_product(product)
    def modify_products(self, products_data:list[dict]):
        """
        Modifies multiple products based on provided data.

        Args:
            products_data (list[dict]): A list of dictionaries, where each dictionary contains:
                - id (int): The unique identifier of the product to be modified.
                - data (dict): Key-value pairs representing the product attributes to update.
                Allowed keys include:
                    - name (str, optional): Updated name of the product.
                    - price (float, optional): Updated price of the product.
                    - product_type (int, optional): Updated product type (0 for Physical, 1 for Service).
                    - description (str, optional): Updated product description.
                    - stock (int, optional): Updated stock quantity (only for physical products).
                    - category (str, optional): Updated product category.
                    - image_url (str, optional): Updated URL of the product image.
                    - preview_url (str, optional): Updated URL for product preview.

        Returns:
            list: A list containing the results of each product modification operation.
        """
        results = []
        for product_data in products_data:
            product_id = product_data['id']
            data = product_data['data']
            results.append(self.db.modify_product(product_id , data))
        return results
        
    def view_products(self):
        """
        Retrieves all products listed by the vendor.

        Returns:
            list: A list of product objects associated with the vendor.
        """
        return self.db.get_vendor_products(self.vendor_id)
    def get_product(self, product_key, value, occurrence="first"):
        """
        Retrieve a product based on a specified key-value pair.

        This method queries the database to fetch a product where the specified 
        column (key) matches the given value. The occurrence parameter determines 
        whether to return the first matching result or all occurrences.

        Args:
            product_key (str): The column name to filter by (e.g., 'id', 'name').
            value (Any): The value to match in the specified column.
            occurrence (str, optional): Determines which result to return. 
                - 'first': Returns the first matching product.
                - 'all': Returns all matching products as a list.
                Defaults to 'first'.

        Returns:
            ProductModel or list[ProductModel] or None: 
                - A single product object if 'first' and a match is found.
                - A list of matching product objects if 'all'.
                - None if no match is found.
        """
        return self.db.get_product_by_key_val(key=product_key, val=value, occurrence=occurrence)


    def track_orders(self):
        """
        Retrieves all orders associated with the vendor.

        Returns:
            list: A list of order objects.
        """
        return self.db.get_vendor_orders(self.vendor_id)

    def manage_payouts(self):
        """
        Retrieves all payout requests made by the vendor.

        Returns:
            list: A list of payout objects.
        """
        return self.db.get_payouts(self.vendor_id)


    


    def get_dashboard_data(self):
        return VendorObj.get_vendor_dashboard_data(db_session=self.db_session , 
                                           vendor_id=self.vendor_id)

   

    def get_recent_orders(self, limit=5):
        """Fetch recent orders."""
        vendor_id = self.vendor_id
        return (
            self.db.session.query(OrderModel)
                        .filter_by(vendor_id=vendor_id)
                        .order_by(OrderModel.created_at.desc())
                        .limit(limit)
                        .all()
        )

    def get_low_stock_products(self , threshold=5):
        """Fetch low-stock products."""
        vendor_id = self.vendor_id
        return (
            self.db.session.query(ProductModel.name, ProductModel.stock)
            .filter( ProductModel.stock != None ,ProductModel.vendor_id == vendor_id, ProductModel.stock <= threshold).all()
    )
    
    def collect_payment(self ,phone , amount ,orderid):
        try:
            url = self.config.payment_url
            AUTHKEY = self.config.authkey
            headers = {"Authorization": f"Bearer {AUTHKEY}" ,
                    "Content-Type": "application/json"}
            payload = json.dumps({'phone':phone , "amount":amount , 'orderid':orderid})
        
            response = requests.post(url=url +"/pay" , data=payload , headers = headers , timeout=7)
    
            data = {'code':response.status_code , 'invoiceid':response.json().get("response")}
            in_voice_id = data["invoiceid"]["invoice"]["invoice_id"]
            # print(data)
            # print(in_voice_id)
            print("Giving time for request to reach server")
            time.sleep(5)
            print("Done starting the status check loop")
            if response.status_code != 200:
                print("Got invalid response" , response.content)
                return False
            for i in range(5):
                response = requests.get(url=url +f'/check-status/{in_voice_id}' , 
                                        headers = headers , data=json.dumps({"SIMULATE":True , "MAXRETRIES":2}))

                code = response.status_code
                status = response.json().get('MESSAGE')
                print("response from checking status")
                print (code , status)
                if status ==  "COMPLETE":
                    return 'paid'
                elif status == "FAILED":
                    return 'canceled'
                else:
                    time.sleep(2)
            return 'pending'
        except Exception as e:
            print(e)
            return None
        
    @staticmethod
    def get_vendor_product_categories(db_session:Session , vendor_id:int):
        categories = (db_session.query(ProductModel.category).
                      filter(ProductModel.vendor_id == vendor_id)
                      .distinct()
                      .all()
        )
        if categories:
            categories = [i[0] for i in categories]
        return categories
    
    @staticmethod
    def get_vendor_dashboard_data(vendor_id, db_session:Session , stock_threshold=10):
        # Initialize response structure
        dashboard_data = {
            "active_products":10,
            "out_of_stock":3,
            'total_products': 0,
            'total_revenue': 0.0,
            'daily_revenue': {
                'dates': [],
                'amounts': []
            },
            'recent_orders': [],
            'low_stock_items': []
        }

        # 1. Get total products count
        dashboard_data['total_products'] = db_session.query(func.count(ProductModel.id)) \
            .filter(ProductModel.vendor_id == vendor_id) \
            .scalar()

        # 2. Calculate total revenue and daily breakdown (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        revenue_data = db_session.query(
        OrderModel.created_at.label('date'),
            func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('daily_total')
        ) \
        .join(VendorOrder, VendorOrder.orderid == OrderModel.id) \
        .join(OrderItem, VendorOrder.orderitem == OrderItem.id) \
        .filter(
            VendorOrder.vendorid == vendor_id,
            OrderModel.created_at >= seven_days_ago
        ) \
        .group_by(func.date(OrderModel.created_at)) \
        .order_by(func.date(OrderModel.created_at)) \
        .all()


    
        # Format daily revenue data
        for day in revenue_data:
            dashboard_data['daily_revenue']['dates'].append(day.date.strftime('%m-%d'))
            dashboard_data['daily_revenue']['amounts'].append(float(day.daily_total or 0))
        
        # Fill missing days with 0
        all_dates = [(datetime.now() - timedelta(days=i)).strftime('%m-%d') for i in range(7)]
        for date in all_dates:
            if date not in dashboard_data['daily_revenue']['dates']:
                dashboard_data['daily_revenue']['dates'].append(date)
                dashboard_data['daily_revenue']['amounts'].append(0.0)
        
        # Sort by date
        sorted_data = sorted(zip(dashboard_data['daily_revenue']['dates'], 
                                dashboard_data['daily_revenue']['amounts']),
                            key=lambda x: x[0])
        dashboard_data['daily_revenue']['dates'] = [d[0] for d in sorted_data]
        dashboard_data['daily_revenue']['amounts'] = [d[1] for d in sorted_data]

        # 3. Get recent orders (last 3)
        recent_orders = db_session.query(
            OrderModel,
            func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('order_total'),
            SessionTracking.token.label('customer_name')
        ) \
        .join(VendorOrder, VendorOrder.orderid == OrderModel.id) \
        .join(OrderItem, VendorOrder.orderitem == OrderItem.id) \
        .join(SessionTracking, OrderModel.session == SessionTracking.token) \
        .filter(VendorOrder.vendorid == vendor_id) \
        .group_by(OrderModel.id, SessionTracking.token) \
        .order_by(OrderModel.created_at.desc()) \
        .limit(3) \
        .all()

        for order, total, customer in recent_orders:
            dashboard_data['recent_orders'].append({
                'id': f"ORD-{order.id}",
                'total': float(total),
                'status': order.status,
                'time_ago': humanize.naturaltime(datetime.now() - order.created_at),
                'customer': customer
            })
            dashboard_data['total_revenue'] += float(total)

        # 4. Get low stock items (stock < 5)
        low_stock_items = db_session.query(ProductModel) \
            .filter(
                ProductModel.vendor_id == vendor_id,
                ProductModel.stock < stock_threshold
            ) \
            .order_by(ProductModel.stock.asc()) \
            .all()

        for product in low_stock_items:
            dashboard_data['low_stock_items'].append({
                'id': product.id,
                'name': product.name,
                'stock': product.stock,
                'threshold': stock_threshold
            })
     

        out_of_stocks = db_session.query(func.count(ProductModel.id)).filter(
            ProductModel.vendor_id == vendor_id,
            ProductModel.stock == 0
        ).scalar()

        dashboard_data['out_of_stock'] = out_of_stocks
        dashboard_data['active_products'] = dashboard_data['total_products'] - dashboard_data['out_of_stock']
        dashboard_data['today_revenue'] = 788
        return dashboard_data

