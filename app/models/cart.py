
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Boolean , String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .product import Product
from .user_profile import UserProfile
from .base import Base

class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(UserProfile.id), nullable=True)  
    session_tkn = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)  
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship with CartItems
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


    
class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey(Cart.id, ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id, ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
