# base.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer , TIMESTAMP ,Column ,func
from datetime import  datetime ,timezone
import enum

Base = declarative_base()

get_time = lambda :datetime.now(timezone.utc)

class VendorRequestStatus(enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"

class TimeStampedBase(Base):
       __abstract__ = True
       
       created_at = Column(TIMESTAMP ,default=get_time())
       updated_at = Column(TIMESTAMP, onupdate=get_time())

       

