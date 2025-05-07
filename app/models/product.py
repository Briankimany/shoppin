# product.py
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime ,Boolean ,text
from datetime import datetime ,timezone
from .base import Base , product_attribute_link ,product_attribute_values
from .vendor import Vendor
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey(Vendor.id), nullable=False)
    discount_id = Column(Integer , ForeignKey('discounts.id'))
    name = Column(String, nullable=False)

    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0 , nullable=True)

    image_url = Column(String)
    preview_url = Column(String)
    _category = Column('category',String)

    is_active = Column(Boolean ,server_default=text("TRUE") ,nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    discount = relationship(
        'Discount',
        back_populates='products'
    )

    vendor = relationship(
        "Vendor" ,
        back_populates='products')
    
    charge = relationship(
        'ProductCharge',
        back_populates='product',
        uselist=False)
    
    vendor_cover = relationship(
        'VendorCharge',
        back_populates='product',
        uselist=False)

    attributes = relationship(
        "Attribute", 
        secondary=product_attribute_link,
        back_populates="products"
    )
    attributes_values = relationship(
        'AttributeValue',
        secondary=product_attribute_values,
        back_populates='products'
    )

    @hybrid_property
    def category(self):
        return self._category
    @category.setter
    def category(self ,value):
        self._category = value
    
    @hybrid_property
    def total_commission(self):
        return  self.vendor.plan.product_commission(self.price)
    @hybrid_property
    def commission(self):
        return self.charge.apply_charge(self.total_commission)
    
    @hybrid_property
    def final_price(self):
        if self.charge:
            return self.price+ self.commission
        else:
            raise Exception(f"Invalid product record {self}")
        
    @hybrid_property
    def vendor_commision(self):
        if not self.vendor_cover:
            return 0
        return self.vendor_cover.apply_charge(self.total_commission)
        

    def __repr__(self):
        return (
        f"<Product(id={self.id}, name='{self.name}', vendor_id={self.vendor_id},\n"
        f"base price = {self.price} selling price={self.final_price}, stock={self.stock}\n"
        f"total commission={self.total_commission} ,vendor charges = {self.vendor_commision} ,product charges={self.commission})>"
    )

    def __str__(self):
        return self.__repr__()
