from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func

from .base import Base
from .user_profile import UserProfile 
from .session_tracking import SessionTracking
from .cart import Cart

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session = Column(String , ForeignKey(SessionTracking.token),nullable = False)
    user_id = Column(Integer, ForeignKey(UserProfile.id), nullable=True)
    phone_number = Column(String, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default='pending')  # pending, paid, canceled
    payment_type = Column(String)  
    cart_id = Column(Integer, ForeignKey(Cart.id), nullable=False)  
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
