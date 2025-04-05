from app.models.payment import Payment , PaymentCategory ,PaymentMethod
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.config import JSONConfig
import os
import uuid


def generate_transaction_ref(length: int = 8):
    return str(uuid.uuid4())[:length]

JSON_PATH = os.getenv('JSON_CONFIG_PATH') or 'config.json'
config = JSONConfig(JSON_PATH)
engine = create_engine(config.SQLITE_DATABASE_URL)
Session = sessionmaker(bind=engine)


from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, Optional, List

class PaymentManager:

    @classmethod
    @contextmanager
    def _session_scope(cls,commit=True):
        """Provide a transactional scope around a series of operations."""
       
        session = Session()
        session.expire_on_commit = False
        try:
            yield session
            if commit:
                session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def record_payment(
        cls,
        source: str,
        recipient: str,
        amount: float,
        method: PaymentMethod,
        category: PaymentCategory,
        description: Optional[str] = None
    ) -> Payment:
        """record a new payment with transaction handling."""
        try:
            payment_record = Payment(
                transaction_ref=generate_transaction_ref(10),
                source=source,
                recipient=recipient,
                amount=amount,
                method=method,
                category=category,
                description=description
            )
            
            with cls._session_scope() as session:
                session.add(payment_record)
                session.flush()  
                return payment_record
                
        except ValueError as e:
            raise ValueError(f"Invalid payment data: {str(e)}")
        except SQLAlchemyError as e:
            raise Exception(f"Database error: {str(e)}")

    @classmethod
    def get_records(cls, filters: Dict[str, Any]) -> List[Payment]:
            """
            Retrieve payment records matching the given filters.
            
            Allowed filter parameters:
                id (int): 
                    Filter by payment ID (exact match)
                    Example: {"id": 123}
                    
                transaction_ref (str): 
                    Filter by exact transaction reference (8-character string)
                    Example: {"transaction_ref": "ABCD1234"}
                    
                source (str): 
                    Filter by source identifier (exact match, case-sensitive)
                    Example: {"source": "customer_123"}
                    
                recipient (str): 
                    Filter by recipient identifier (exact match, case-sensitive)
                    Example: {"recipient": "merchant_456"}
                    
                amount (float/decimal): 
                    Filter by exact amount (numeric match)
                    Example: {"amount": 100.50}
                    
                method (PaymentMethod enum): 
                    Filter by payment method (Bank/M-pesa/Airtel-money)
                    Example: {"method": PaymentMethod.MPESA}
                    
                category (PaymentCategory enum): 
                    Filter by payment category (Product sale/Vendor fee/Hosting Fee)
                    Example: {"category": PaymentCategory.PRODUCT_SALE}
                    
                description (str): 
                    Filter by exact description match (case-sensitive)
                    Example: {"description": "Monthly subscription"}
                    
                created_at (datetime/str): 
                    Filter by creation timestamp (supports date ranges)
                    Examples: 
                        {"created_at": "2023-05-20"} (whole day)
                        {"created_at": ("2023-05-01", "2023-05-31")} (date range)
                        {"created_at": datetime(2023,5,20,14,30)} (exact timestamp)
            
            Returns:
                List[Payment]: List of matching Payment objects
                
            Raises:
                ValueError: If invalid filter keys or values are provided
                DatabaseError: If query execution fails
            """
            if not filters:
                raise ValueError("At least one filter condition required")
            try:
                with cls._session_scope(False) as session:
                    conditions = [
                        getattr(Payment, key) == value 
                        for key, value in filters.items()
                        if hasattr(Payment, key)  
                    ]
                    return session.query(Payment).filter(*conditions).all()
            except SQLAlchemyError as e:
                raise Exception(f"Query failed: {str(e)}")
            


if __name__ == "__main__":
    new_payment = PaymentManager.record_payment(
        source="client_1234@example.com",
        recipient="merchant_456@store.com",
        amount=2499.99,
        method=PaymentMethod.BANK, 
        category=PaymentCategory.PRODUCT_SALE,
        description="Premium annual subscription"
    )

    print(f"Recorded Payment ID: {new_payment.id}")
    rec = PaymentManager.get_records({"method":PaymentMethod.BANK})
    print(rec)
