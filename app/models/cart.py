
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

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<Cart(id={self.id}, user_id={self.user_id}, session_tkn='{self.session_tkn}', "
            f"is_active={self.is_active}, items_count={len(self.items)})>"
        )

    def __str__(self):
        return self.__repr__()



    
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

    def __repr__(self):
        return (
            f"<CartItem(id={self.id}, cart_id={self.cart_id}, product_id={self.product_id}, "
            f"quantity={self.quantity})>"
        )

    def __str__(self):
        return self.__repr__()

