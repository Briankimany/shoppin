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
from .vendor_transaction import VendorTransactionSystem
from datetime import timedelta
from app.models.vendor import Vendor , VendorPayout
from app.models.model_utils import PaymentMethod

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
        return VendorObj.get_vendor_withdrawal_records(
            db_session=self.db_session,vendor_id=self.vendor_id
        )

    def get_dashboard_data(self ,stock_threshold=10):
        return VendorObj.get_vendor_dashboard_data(db_session=self.db_session , 
                                           vendor_id=self.vendor_id,stock_threshold=stock_threshold)

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

    def record_payout(self ,payment_method,amount ,status:str = 'pending'):
        return VendorObj.create_vendor_payout_record(
            db_session=self.db_session,
            vendor_id=self.vendor_id,
            payment_method=payment_method,
            amount=amount,
            status=status
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
        return VendorTransactionSystem.get_vendor_dashboard(
            vendor_id=vendor_id,
            db_session=db_session,
            stock_threshold = stock_threshold
        )

    @staticmethod
    def get_vendor_withdrawal_records(db_session: Session, vendor_id: int) -> tuple[dict, list[dict]]:
        """Retrieves withdrawal records and balance information for a specific vendor.

        Args:
            db_session (Session): SQLAlchemy database session for querying data.
            vendor_id (int): Unique identifier of the vendor.

        Returns:
            tuple[dict, list[dict]]: A tuple containing two elements:
                - First element (dict): Vendor balance information with keys:
                    * 'available' (float): Available balance (total - withdrawn)
                    * 'pending' (float): Sum of pending withdrawals
                    * 'total' (float): Total account balance
                - Second element (list[dict]): List of withdrawal dictionaries with keys:
                    * 'amount' (float): Withdrawal amount
                    * 'method' (str): Payment method used
                    * 'status' (str): Withdrawal status ('completed' or 'pending')
                    * 'request' (datetime): When withdrawal was requested

        Example:
            >>> balance, withdrawals = get_vendor_withdrawal_records(session, 123)
            >>> print(balance)
            {'available': 850.0, 'pending': 150.0, 'total': 1000.0}
            >>> print(withdrawals[0])
            {'amount': 100.0, 'method': 'bank_transfer', 'status': 'completed', ...}
        """
        
        vendor_withdrwals = db_session.query(
            VendorPayout
            ).filter(VendorPayout.vendor_id==vendor_id
            ).order_by(VendorPayout.created_at.desc()
            ).all()
        account_data = VendorTransactionSystem.calculate_total_revenue(db_session=db_session,
                                                                       vendor_id=vendor_id)
        completed = []
        pending = []
        withdrawals = []
        for vendor_pay  in vendor_withdrwals:
            if vendor_pay.status == 'completed':
                completed.append(vendor_pay.amount)
            elif vendor_pay.status == 'pendig':
                pending.append(vendor_pay.amount)
            
            withdrawals.append({'amount':vendor_pay.amount,'method':vendor_pay.method
                                ,'status':vendor_pay.status,'request':vendor_pay.created_at})
        
        amount_withdrawn = sum(completed)
        vendor_balance = {
            "available":account_data['account_balance'] - amount_withdrawn,
            'pending': sum(pending),
            'total':amount_withdrawn
        }
        return  vendor_balance , withdrawals

    @staticmethod
    def create_vendor_payout_record(db_session:Session , amount:float ,
                                    payment_method:PaymentMethod ,
                                    vendor_id:int,
                                    status:str = 'pending'):
        payout = VendorPayout(
            vendor_id= vendor_id,
            method = payment_method,
            amount=amount,
            status = status
        )
       
        db_session.add(payout)
        db_session.commit()
        LOG.VENDOR_LOGGER.info(f"withdrwal record initiated {payout}")
        return payout
    