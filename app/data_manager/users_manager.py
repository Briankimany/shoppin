
from app.models.user_profile import UserProfile 
from app.models.session_tracking import SessionTracking
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.routes.logger import LOG
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from .vendor import VendorObj

class UserManager:
    def __init__(self , db_session:Session , user = None):
        self.db_session = db_session
        self.user = self.get_user(user=user)
        self.session_tkn = None
    def __str__(self):
        return f"<UserManager(user_id={self.user.id if self.user else 'None'}, name={self.user.name if self.user else 'None'}, email={self.user.email if self.user else 'None'}, session_tkn={self.session_tkn}, db_session_active={self.db_session.is_active})>"


    def reload_object(self , user , token= None):

        self.user = self.get_user(user=user)
        if token:
            self.session_tkn = token
        return self.user
    
    def update_details(self, data:dict):
        if not self.user:
            return "Invalid mode of operation"
        for k , v in data.items():
            if hasattr(self.user , k):
                setattr(self.user ,k , v)
            else:
                print("INVALID USER INPUT PARAMS")
        self.db_session.commit()

    def get_user(self, user):
        
        user_obj = UserManager.get_user_(self.db_session , user)
        if user_obj:
            self.user = user_obj
        return user_obj
    

    def verify_password(self , password , user):
        if not isinstance(user,UserProfile):
            user = self.db_session.query(UserProfile).filter(
                or_(
                    UserProfile.id == user,
                    UserProfile.name == user,
                    UserProfile.phone == user,
                    UserProfile.email == user
                )
            ).first()
        else:
            user = user

        if not isinstance(user,UserProfile):
            return None
        return user.password_hash == password
    
    def self_update_session(self ,data):
        if not self.session_tkn:
            return "NO SELF TOKEN"
        return UserManager.update_session_value(db_session=self.db_session , session_tkn=self.session_tkn , data=data)

    def get_tkn_from_user_id(self):
        session = self.db_session.query(SessionTracking).filter(SessionTracking.user_id == self.user.id).first()
        return session
    def self_register(self , data:dict):
        self.user = UserManager.register_user(self.db_session , user_details= data)
        return self.user
    
    def update_data(self , data):
        for k , v in data.items():
            LOG.USER_LOGGER.info(f" attribute {k}: {v} for user {self.user.name}")
            if hasattr(self.user , k):
                setattr(self.user , k , v)
            else:
                LOG.USER_LOGGER.info(f"invalid attribute {k}: {v} for user {self.user.name}")
                return False
        self.db_session.commit()
        return True
    
    def get_order_from_session_tkn(self , session_tkn:str , status='pending' , num_orders=3):
        if status == "pending":
            orders = self.db_session.query(Order).filter(Order.session == session_tkn , Order.status == status ).all()
        elif status == "all":
          
            orders = UserManager.get_k_latest_orders(db_session=self.db_session , k = num_orders , 
                                                    user_id=self.user.id if self.user else None ,session_tkn=session_tkn)
        return orders
    
    def get_my_previous_order_items(self , order_id):
        """
        {
            "order_date": "2023-01-01T00:00:00",
            "status": "completed",
            "payment_type": "pre-delivery",
            "total_amount": 99.99,
            "items": [
                {
                    "product_id": 123,
                    "product_name": "Product Name",
                    "image_url": "/path/to/image.jpg",
                    "quantity": 2,
                    "price_at_purchase": 49.99
                }
            ]
        }
        """

        items = UserManager.get_order_items_for_order_id(db_session=self.db_session ,
                                                         order_id=order_id)
        
        order = self.db_session.query(Order).filter(Order.id == order_id).first()
        data = {"order_date":order.created_at.strftime("%Y-%m-%dT%H:%M:%S") , "status":order.status,
            "payment_type":order.payment_type ,"total_amount":float(order.total_amount)}
        data['items'] = items
        
        return data
    
    def is_vendor(self):
        if self.user:
            return UserManager.verify_is_vendor(self.db_session ,user_name=self.user.id)
        

    @staticmethod
    def verify_is_vendor(db_session,user_name:int):
        vendor = VendorObj.get_vendor_by(db_session=db_session ,key='id' , value=user_name)
        return vendor
    
    
    @staticmethod
    def register_user(db_session:Session , user_details:dict , return_self_instance = False):
        user = UserProfile(**user_details)
        db_session.add(user)
        db_session.commit()
        if return_self_instance:
            return UserManager(db_session=db_session , user=user)
        else:
            return user
        
    @staticmethod
    def verify_unique_name(db_session : Session , suggested_name:str):
        names = db_session.query(UserProfile).all()
        names = [i.name for i in names]
        names = [i.lower()for i in names]
        return suggested_name.lower() not in names , names
    @staticmethod
    def update_session_value(db_session:Session , session_tkn ,data:dict):
        session = db_session.query(SessionTracking).filter(SessionTracking.token == session_tkn).first()
        if session:
            for k , v in data.items():
                if hasattr(session , k):
                    setattr(session , k , v)
           
        else:
            return "no session found"

        db_session.commit()
        return "Done"
    
    @staticmethod
    def get_k_latest_orders(db_session: Session, k: int, user_id=None, session_tkn: str=None):
        orders = db_session.query(Order).filter(
            or_(
                Order.user_id == user_id if user_id else False,
                Order.session == session_tkn if session_tkn else False
            )
        ).order_by(Order.created_at.desc()).limit(k).all()

        return orders if orders else None
    @staticmethod
    def get_order_items_for_order_id(db_session:Session , order_id:int):

        order_items = (
            db_session.query(OrderItem, Product)
            .join(Product, OrderItem.product_id == Product.id)
            .filter(OrderItem.order_id == order_id)
            .all()
        )
        
        items = [
            {
                "product_id": product.id,
                "product_name": product.name,
                "image_url":product.image_url if product.image_url else "/static/images/placeholder.png",
                "quantity": order_item.quantity,
                "price_at_purchase": str(order_item.price_at_purchase),
            }
            for order_item, product in order_items
        ]
        return items
    
    @staticmethod
    def get_user_(db_session, user):
        
        if isinstance(user, UserProfile):
            return user

        query = None
        if isinstance(user, int): 
            query = db_session.query(UserProfile).filter(UserProfile.id == user)
        elif isinstance(user, str):  
            query = db_session.query(UserProfile).filter(
                or_(
                    UserProfile.name == user,
                    UserProfile.email == user,
                    UserProfile.phone == user
                )
            )

        user_obj = query.first() if query else None
        return user_obj
    
    
    

