# vendor.py
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime ,ForeignKey ,TIMESTAMP ,DECIMAL
from datetime import datetime
from sqlalchemy.sql import func

from .base import Base



class Vendor(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True, autoincrement=True)
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


class VendorPayout(Base):
    __tablename__ = "vendor_payouts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey(Vendor.id), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), nullable=False)  # pending, processing, completed, failed
    method = Column(String(30) , nullable=False)  # eg m-pesa ,bank , airtel-money
    transaction_ref = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


