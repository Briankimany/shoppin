from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP 
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
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
    tracking_id = Column(String ,default = None) 
    cart_id = Column(Integer, ForeignKey(Cart.id), nullable=False)  
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    orderitems = relationship('OrderItem',backref='order')
    @hybrid_property
    def payment_type(self):
        return "M-pesa"
    def __repr__(self):
        return (
        f"<Order(id={self.id}, session='{self.session}', user_id={self.user_id}, "
        f"phone_number='{self.phone_number}', total_amount={self.total_amount}, "
        f"status='{self.status}', cart_id={self.cart_id})>"
    )
    
    def __str__(self):
        return self.__repr__()
