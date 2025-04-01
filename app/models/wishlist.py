from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from .user_profile import UserProfile
from .product import Product
from .base import Base

class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(UserProfile.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
