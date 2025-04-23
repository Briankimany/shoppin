
from sqlalchemy.orm import Session
from app.models.session_tracking import SessionTracking
from app.models.cart import Cart as CartModel ,CartItem
from app.models.cart import Cart
from app.models.product import Product as ProductModel
from app.models.order import Order

import uuid
from datetime import datetime, timedelta , timezone
import requests
from app.models.user_profile import UserProfile

from .client_access_manager import session_scope
from app.routes.logger import LOG

class SessionManager:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_new_session(self,user_id=None , expire_after:int = 24):
        """Creates a new session and ensures a cart is linked to it."""
       
        new_token = SessionManager.generate_token()
        LOG.SESSIONS_LOGGER.info("-"*35)
        LOG.SESSIONS_LOGGER.info("Creating new session token..")
        with session_scope(commit=True ,raise_exception=True ,logger=LOG.SESSIONS_LOGGER) as db_session:
           
            new_cart = Cart(user_id=user_id ,session_tkn = new_token)

            LOG.SESSIONS_LOGGER.debug(f"Cart created succesfully {new_cart}")
            db_session.add(new_cart)
            db_session.commit()
            LOG.SESSIONS_LOGGER.debug(f"added cart succesfully {new_cart} ")

            new_session = SessionTracking(
                token=new_token,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=expire_after),
                cart_id=new_cart.id, 
                user_id=user_id,
            )
            LOG.SESSIONS_LOGGER.debug(f"Creating new session  {new_session}")
            db_session.add(new_session)
            LOG.SESSIONS_LOGGER.debug(f"session added {new_session}")

            return new_session.token 

    def verify_session_token(self , session_token):

        with session_scope() as db_session:
            tkn = db_session.query(SessionTracking).filter(SessionTracking.token == session_token).first()
            if tkn:
                now = datetime.now()
                expiry_time = tkn.expires_at
                is_expired = now >=expiry_time
                if is_expired:
                    return False
                else:
                    return True
            else:
                return False
            

    def create_cart(self , user_id, session_tkn):
        """Creates a new empty cart and returns its ID."""
        new_cart = CartModel(user_id=user_id ,session_tkn=session_tkn)
        self.db_session.add(new_cart)
        self.db_session.commit()
        return new_cart.id

    def get_cart(self, session_token):
        """Retrieves the cart associated with a session token."""
        session = self.db_session.query(SessionTracking).filter_by(token=session_token).first()
        if session:
            cart = self.db_session.query(CartModel).filter_by(id=session.cart_id).first()
            if cart.is_active:
                return session.cart_id
            else:
                cartid = self.create_cart(user_id=cart.user_id , session_tkn=session_token)
                session.cart_id = cartid
                self.db_session.commit()
                return cartid
        else:
            return None
        
    def verify_cart_not_Checked_out(self , cart_id):
        cart = self.db_session.query(CartModel).filter_by(id = cart_id).first()
        return cart.is_active
    
    def verify_available_stock(self , product_id ,stock):
        product = self.db_session.query(ProductModel).where(ProductModel.id == product_id).first()
        if product.category in ['Services']:
            return True
        return product.stock >=stock

    def add_to_cart(self, session_token, product_id, quantity=1):
        """Adds an item to the user's cart."""
        cart_id = self.get_cart(session_token)
      
        stock_available = self.verify_available_stock(product_id , quantity)
        if not stock_available:
            return {"status":"error" ,"reason":"Max stock exceded"}
     
        if cart_id:
            existing_item = self.db_session.query(CartItem).filter_by(cart_id=cart_id, product_id=product_id).first()
            if existing_item:
                existing_item.quantity += quantity
            else:
                new_item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
                self.db_session.add(new_item)
            self.db_session.commit()
        return {"status":"added" ,"reason":None}

    def remove_from_cart(self, session_token, product_id):
        """Removes an item from the user's cart."""
        cart_id = self.get_cart(session_token)
        self.db_session.query(CartItem).where(CartItem.cart_id == cart_id , CartItem.product_id == product_id).delete()
        self.db_session.commit()
        
    def clear_cart(self, session_token):
        """Empties the user's cart."""
        cart_id = self.get_cart(session_token)
        if cart_id:
            self.db_session.query(CartModel).filter_by(cart_id=cart_id).delete()
            self.db_session.commit()
    def get_cartitems(self , cart_id):
        return self.db_session.query(CartItem).filter_by(cart_id =cart_id).all()
    
    def get_cart_summary(self, session_token):
        """Fetches unique cart items, their quantities, and product details for checkout."""
        cartdid = self.get_cart(session_token=session_token)
        cartitems = self.get_cartitems(cart_id=cartdid)
        results = {}
        totalcost=0
        for item in cartitems:
            item_category = item.product.category
            if item_category not in results:
                results[item_category] = []
            itemprice = item.quantity*item.product.price
            itemdata = {"product_id":item.product_id,"name":item.product.name , "quantity":item.quantity , "price":itemprice}
            results[item_category].append(itemdata)

            totalcost+=itemprice
        results['TotalCost'] = totalcost
        return results
            
        
    def update_cart_item(self, cart_id, product_id, new_quantity):
        """Updates the quantity of a cart item."""
        cart_item = (
            self.db_session.query(CartItem)
            .filter_by(cart_id=cart_id, product_id=product_id)
            .first()
        )
        if cart_item:
            cart_item.quantity = new_quantity
            self.db_session.commit()

    def update_cart(self , cart_id , attribute ,new_value):
        try:
            cart = self.db_session.query(CartModel).filter_by(id = cart_id).first()
            if cart:
                setattr(cart , attribute , new_value)
                self.db_session.commit()
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            return None
    
    def get_geo_data(self, ip_address):
        """Fetches geo-location data based on IP address."""
        try:
            response = requests.get(f"https://ipinfo.io/{ip_address}/json")
            if response.status_code == 200:
                data = response.json()
                return data.get("country"), data.get("region"), data.get("city")
        except requests.RequestException:
            return None, None, None

    def update_session_geo_info(self, session_token):
        """Updates a session with geo-location data."""
        session = self.db_session.query(SessionTracking).filter_by(token=session_token).first()
        if session and session.ip_address:
            country, region, city = self.get_geo_data(session.ip_address)
            session.country = country
            session.region = region
            session.city = city
            self.db_session.commit()

    def get_phone_from_session_token(self , tkn):
        session = self.db_session.query(SessionTracking).filter(SessionTracking.token==tkn).first()
        print("Userid from getting  phpne" , session.user_id)
        if session.user_id:
            phone = self.db_session.query(UserProfile).filter(UserProfile.id == session.user_id).first()
            return phone.phone
        else:
            return None
        
    def get_order_from_session_tkn(self , session_tkn:str , status='pending'):
        orders = self.db_session.query(Order).filter(Order.session == session_tkn , Order.status == status ).all()
        return orders
        
    @staticmethod
    def generate_token():
        """Generates a unique session token."""
        return str(uuid.uuid4()) 
    @staticmethod
    def get_ip_address(request):
        """Retrieves the user's IP address."""
        return request.headers.get("X-Forwarded-For", request.remote_addr)
    @staticmethod
    def get_userid_associated_with_tkn(db_session :Session, session_token):
        session = db_session.query(SessionTracking).filter_by(token=session_token).first()
        if session:
            return session.user_id