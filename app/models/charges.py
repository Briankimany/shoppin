from sqlalchemy import Column , Integer , Numeric ,Enum ,String ,ForeignKey,tuple_
from sqlalchemy.orm import relationship 
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from decimal import Decimal

from .base import TimeStampedBase
from .model_utils import ChargeType
import json
from .charges_utils import Payee

class Charge(TimeStampedBase):
    __tablename__ = 'charges'
    
    id = Column(Integer, primary_key=True)
    type = Column(Enum(ChargeType),nullable=False)
    _payee_type = Column('payee_type', String(20))  
    _payee_id = Column('payee_id', Integer)       
    percentage = Column(Numeric(5, 2))
    recipient_id = Column(Integer)
    
    @hybrid_property
    def payee(self):
        """Instance access - returns Payee object"""
        if None in (self._payee_type, self._payee_id):
            return None
        return Payee(self._payee_type, self._payee_id)

    @payee.expression
    def payee(cls):
        """Database query - returns comparable tuple"""
        return tuple_(cls._payee_type, cls._payee_id)

    @payee.setter
    def payee(self, value):
        """Setter handles both Payee objects and tuples"""
        if value is None:
            self._payee_type = self._payee_id = None
        elif isinstance(value, Payee):
            self._payee_type, self._payee_id = value.entity_type, value.entity_id
        else:  
            self._payee_type, self._payee_id = value
       
    def apply_charge(self, base_amount):
        """Calculate charge amount from base amount"""
        if not self.percentage:
            return Decimal('0.00')
        return (base_amount * self.percentage / 100).quantize(Decimal('0.00001'))
    
    def __str__(self):
        return f"<Charge {self.id}: Type={self.type.name}, Percentage={self.percentage}%, Recipient={self.recipient_id}, Payee={self.payee}>"

    def __repr__(self):
        return (
            f"Charge(id={self.id}, "
            f"type={self.type.name}, "
            f"percentage={self.percentage}, "
            f"recipient_id={self.recipient_id}, "
            f"payee_id={self.payee})"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.name,
            "percentage": float(self.percentage) if self.percentage is not None else None,
            "recipient_id": self.recipient_id,
            "payee_id": self.payee,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def to_json(self):
        return json.dumps(self.to_dict())

class ChildCharge(TimeStampedBase):
    __abstract__ = True

    id  = Column(Integer , autoincrement = True , primary_key=True)
    
    charge_id = Column(Integer,ForeignKey('charges.id') ,nullable=False)
    product_id = Column(Integer,ForeignKey('products.id') ,nullable=False)


    @declared_attr
    def charge(cls):
        return relationship('Charge', uselist=False)

    def apply_charge(self,base_amount):
        return self.charge.apply_charge(base_amount)
    
    @hybrid_property
    def payee(self):
        return self.charge.payee
    
    @hybrid_property
    def percentage(self):
        return self.charge.percentage

    @hybrid_property
    def recipient(self):
        return self.charge.recipient
    

class ProductCharge(ChildCharge):
    __tablename__ = "products_charges"
    product = relationship("Product" ,back_populates='charge',uselist=False)

class VendorCharge(ChildCharge):
    __tablename__ = "vendors_charges"
    vendor_id = Column(Integer, ForeignKey('vendors.id'), nullable=False)

    product = relationship("Product" ,back_populates='vendor_cover',uselist=False)
    vendor = relationship('Vendor',back_populates='charges')
