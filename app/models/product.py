# product.py
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime
from datetime import datetime
from .base import Base
from .vendor import Vendor

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey(Vendor.id), nullable=False)
    name = Column(String, nullable=False)
    product_type = Column(Integer, nullable=False, default=0)  # 0 = Physical, 1 = Service
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0 , nullable=True)
    category = Column(String)
    image_url = Column(String)
    preview_url = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def __repr__(self):
        return (
        f"<Product(id={self.id}, name='{self.name}', vendor_id={self.vendor_id}, "
        f"type={'Service' if self.product_type == 1 else 'Physical'}, "
        f"price={self.price}, stock={self.stock}, category='{self.category}')>"
    )

    def __str__(self):
        return self.__repr__()
