from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship

from .vendor import Vendor
from .base import Base

class Discount(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey(Vendor.id), nullable=False)
    discount_percent = Column(DECIMAL(5, 2), nullable=False)
    valid_from = Column(TIMESTAMP, nullable=False)
    valid_until = Column(TIMESTAMP, nullable=False)

    products = relationship(
        'Products',
        back_populates = 'discount'
    )
