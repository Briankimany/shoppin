from .model_utils import PaymentCategory , PaymentMethod
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, Enum as SQLAlchemyEnum
from .base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_ref = Column(String(8), unique=True, nullable=False)

    source = Column(String(50), nullable=False)
    recipient = Column(String(50), nullable=False) 
    amount = Column(Numeric(10, 2), nullable=False)

    
    method = Column(SQLAlchemyEnum(PaymentMethod), nullable=False)
    category = Column(SQLAlchemyEnum(PaymentCategory), nullable=False)

    description = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now()) 


    def __repr__(self):
        return (
            f"<Payment(id={self.id}, "
            f"transaction_ref='{self.transaction_ref}', "
            f"source='{self.source}', recipient='{self.recipient}', "
            f"amount={self.amount}, method='{self.method}', "
            f"category='{self.category}', created_at='{self.created_at}')>"
        )

    def __str__(self):
        return self.__repr__()