# payment.py
from sqlalchemy import Column, Integer, ForeignKey, String, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func
from .order import Order
from .base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey(Order.id), nullable=False)
    phone_number = Column(String(20), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), nullable=False)  # pending, successful, failed
    transaction_ref = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
