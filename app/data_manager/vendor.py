from .database_index import Database  , OrderModel , ProductModel  
from sqlalchemy import func
from sqlalchemy.orm import Session
import requests

from config.config import JSONConfig
import json
import time

from app.models.vendor import Vendor
from app.routes.logger import LOG ,bp_error_logger

from .vendor_transaction import VendorTransactionSystem
from app.models.vendor import Vendor , VendorPayout
from app.models.model_utils import PaymentMethod
from app.models.user_profile import UserBalance

from config.envrion_variables import StatusCodes ,StatusNames
from data_manager.vendor_transaction import VendorTransactionSystem

from contextlib import contextmanager
from config.envrion_variables import Session as ManagedSession

class VendorObj:

    @classmethod
    @contextmanager
    def _scoped_session(cls):
        db_session = ManagedSession()
        try:
            yield db_session
        except Exception as e:
            LOG.VENDOR_LOGGER.error(f"[DB-ERROR] exception from scopped session {e}")
        finally:
            db_session.close()

    """
    Manages vendor-related operations, including updating details, verifying vendors, 
    adding/viewing products, tracking orders, and managing payouts.
    """

    config = JSONConfig("config.json")

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
    
    def withdraw(self , amount:float , phone,**kwargs):
        """
        Initiates a withdrawal request for the vendor.

        Args:
            amount (float): Amount to withdraw.
            payment_method (PaymentMethod): Payment method for the withdrawal.

        Returns:
            dict: Response from the withdrawal initiation request.
        """
        return VendorObj.initiate_withdraw( self.vendor_table.name,  amount, phone, **kwargs )
    
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
            elif vendor_pay.status == 'pending':
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


    @classmethod
    def is_allowed_withdraw(cls ,db_session:Session ,vendor_id ,needed_amount:float):

        pending_withdraws = db_session.query(VendorPayout).filter(
            VendorPayout.vendor_id == vendor_id,
            VendorPayout.status == 'pending'
        ).all()

    
        total_amount = float(sum([withdrawal.amount for withdrawal in pending_withdraws])) +needed_amount
        vendor_balance = db_session.query(UserBalance).filter(UserBalance.id == vendor_id).first().balance

        tomany_withdraws = len(pending_withdraws) >= cls.config.MAX_NUM_PENDING_WITHDRAWs 
        amount_exceeds_balance = total_amount >= vendor_balance

        if tomany_withdraws:
            LOG.VENDOR_LOGGER.info(f"Vendor {vendor_id} has too many pending withdrawals.")
            return {"message": "Too many pending withdrawals. Please resolve existing requests before submitting a new one."}

        if amount_exceeds_balance:
            LOG.VENDOR_LOGGER.info(f"Vendor {vendor_id} has insufficient balance for withdrawal.")
            return {"message": "Withdrawal amount exceeds available balance."}

        
        return {"success": True}   

    @staticmethod
    def create_vendor_payout_record(db_session:Session ,amount:float ,
                                    payment_method:PaymentMethod ,
                                    vendor_id:int,
                                    batch_id:str,
                                    tracking_id:str,
                                    status:str = 'pending'):
        
 

        payout = VendorPayout(
            vendor_id= vendor_id,
            method = payment_method,
            amount=amount,
            status = status,
            batch_id = batch_id,
            tracking_id = tracking_id
        )
       
        db_session.add(payout)
        db_session.commit()
        LOG.VENDOR_LOGGER.info(f"withdrwal record initiated {payout}")
        return {"success": True, "payout_id": payout.id}
    
    

    @classmethod
    def initiate_withdraw(cls,vendor_name:int , amount:float , phone:str ,**kwargs):
        """
        Initiates a withdrawal request for a vendor.
        Args:
            vendor_name (str): Name of the vendor.
            amount (float): Amount to withdraw.
            phone (str): Phone number associated with the vendor.
        Returns:
            tuple: Response from the withdrawal initiation request , True/None
        Example:
            >>> response = initiate_withdraw("John Doe", 100.0, "+123456789")
        """
        
        if not cls.config.payment_url or not cls.config.authkey:
            LOG.VENDOR_LOGGER.error("Payment URL or Auth Key not set in config.json")
            return None

        url = cls.config.payment_url+"/transfers/initiate/single"

        headers = {"Authorization":"Bearer " +cls.config.authkey ,
                    "Content-Type":"application/json"
                   }

        payload = {
            "records": {
                "name":vendor_name,
                'phone':phone,
                "amount":amount
            },
            "requires_approval": "YES"
        }

        payload.update(kwargs)
       
        LOG.VENDOR_LOGGER.info("-"*30)
        LOG.VENDOR_LOGGER.info(f"Initiating withdrawal for {vendor_name} of amount {amount} to {phone}")
        LOG.VENDOR_LOGGER.info(f"Payload: {payload}")

        response = requests.post(url=url , headers=headers , data=json.dumps(payload))
        
        if response.status_code == 200:
            return response.json() ,True
        else:
            LOG.VENDOR_LOGGER.error(f"Failed to initiate withdrawal: {response.content}")
            return None , None
    
    @classmethod
    def check_update_withdraw_status(cls, db_session,withdraw_id):
        """
        Check the status of a withdrawal request.

        Args:
            db_session (Session): SQLAlchemy database session for querying data.
            withdraw_id (int): Unique identifier of the withdrawal request.

        """
        
        url = cls.config.payment_url +"/transfers/transfer-status"

        headers = {"Authorization": "Bearer " + cls.config.authkey,
                   "Content-Type": "application/json"}
        payload = {
            "reference_id": withdraw_id
        }

        response = requests.get(url=url, headers=headers, data=json.dumps(payload))

        LOG.VENDOR_LOGGER.info(f"In the check_update_withdraw_status method")
        LOG.VENDOR_LOGGER.info(f"Checking withdrawal status for {withdraw_id}")
        LOG.VENDOR_LOGGER.info(f"Payload: {payload}")
        LOG.VENDOR_LOGGER.info(f"Response: {response.status_code}")

        if response.status_code == 200:
            data = response.json().get('data')[0]

            status = data.get("status_code")
            LOG.VENDOR_LOGGER.info(f"checking status for {withdraw_id} : response {status ,data.keys()}")

            if status in StatusCodes.SUCCESS:
                cls.update_withdraw_status(db_session, withdraw_id, StatusNames.COMPLETED)

            elif status in StatusCodes.CANCELED:
                cls.update_withdraw_status(db_session, withdraw_id, StatusNames.FAILED)

            else:
                LOG.VENDOR_LOGGER.info(f"Withdrawal {withdraw_id} is still pending.")
            
            if status in StatusCodes.CONTACT_ADMIN:
                cls.update_withdraw_status(db_session, withdraw_id, "contact_admin")
                LOG.VENDOR_LOGGER.info(f"Withdrawal {withdraw_id} requires admin contact.")

        else:
            LOG.VENDOR_LOGGER.error(f"Failed to check withdrawal status: {response.content}") 

        return response.json()
      

    @classmethod
    def update_withdraw_status(cls,hh,withdraw_id, status):

        """
        Update the status of a withdrawal request in the database.

        Args:
            db_session (Session): SQLAlchemy database session for querying data.
            withdraw_id (int): Unique identifier of the withdrawal request.
            status (str): New status to set for the withdrawal request.
        """
        with cls._scoped_session() as db_session:
            withdrawal = db_session.query(VendorPayout).filter(VendorPayout.tracking_id == withdraw_id).first()
            if withdrawal:
                withdrawal.status = status

                if status == StatusNames.COMPLETED and not withdrawal.updated_user_balance:
                    amount  = (float(withdrawal.amount) *-1)
                    print("amount to be updated" , amount ,type(amount))
                    VendorTransactionSystem.update_vendor_balance(
                       vendor_id = withdrawal.vendor_id,
                          amount = amount,
                          db_session=db_session 
                    )

                    withdrawal.updated_user_balance = True
                    db_session.commit()

                else:
                    LOG.VENDOR_LOGGER.info(f"Withdrawal {withdraw_id} status is not completed, user balance not updated.")
                
               
                LOG.VENDOR_LOGGER.info(f"Withdrawal {withdraw_id} status updated to {status}.")
            else:
                LOG.VENDOR_LOGGER.error(f"Withdrawal {withdraw_id} not found.")
   
    @classmethod
    def get_pending_withdrawals(cls,db_session:Session ,vendor_id):

        pending = db_session.query(VendorPayout.tracking_id).filter(
            VendorPayout.status == StatusNames.PENDING,
            VendorPayout.vendor_id == vendor_id,
        ).all()
        pending = [i[0] for i in pending]

        print(f"all waiting {pending}")

        if pending:
            return  pending
        return None
    
    
