# vendor.py
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime ,ForeignKey ,TIMESTAMP ,DECIMAL ,Enum as SQLENUM
from datetime import datetime
from sqlalchemy.sql import func
from .base import Base
from .model_utils import PaymentMethod



class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(ForeignKey("user_table.id"), primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    store_name = Column(String, unique=True, nullable=False)
    store_logo = Column(String , unique=False , nullable=False)
    payment_type = Column(String ,nullable = False)
    store_description = Column(Text)
    verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return (
            f"<Vendor(id={self.id}, name='{self.name}', email='{self.email}', phone='{self.phone}', "
            f"store_name='{self.store_name}', payment_type='{self.payment_type}', verified={self.verified})>"
        )

    def __str__(self):
        return self.__repr__()


class VendorPayout(Base):
    __tablename__ = "vendor_payouts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey(Vendor.id), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), nullable=False)  # pending,  completed, failed
    method = Column(SQLENUM(PaymentMethod) , nullable=False)  # eg m-pesa ,bank , airtel-money
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return (
            f"<VendorPayout(id={self.id}, vendor_id={self.vendor_id}, amount={self.amount}, "
            f"status='{self.status}', method='{self.method})>"
        )

    def __str__(self):
        return self.__repr__()



