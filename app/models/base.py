# base.py

from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy import Integer , TIMESTAMP ,Column ,ForeignKey ,Table 
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

       

# ---- Association Tables ----
product_attribute_values = Table(
    'product_attribute_values',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('attribute_value_id', Integer, ForeignKey('attribute_values.id'), primary_key=True)
)

product_attribute_link = Table(
    'product_attribute_links',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('attribute_id', Integer, ForeignKey('attributes.id'), primary_key=True)
)

attribute_value_link = Table(
    'attribute_value_links',
    Base.metadata,
    Column('attribute_id', Integer, ForeignKey('attributes.id'), primary_key=True),
    Column('value_id', Integer, ForeignKey('attribute_values.id'), primary_key=True)
)
