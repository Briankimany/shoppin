# vendor.py
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime ,ForeignKey ,TIMESTAMP ,DECIMAL ,Enum as SQLENUM
from datetime import datetime ,timezone
from sqlalchemy.sql import func
from .base import Base
from .model_utils import PaymentMethod
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from .vendor_plans import VendorPlan 
from .custom_vendor_plans import CustomVendorPlan

class Vendor(Base):

    __tablename__ = 'vendors'
    id = Column(Integer ,ForeignKey("users_table.id"), primary_key=True ,autoincrement=False)
 
    store_name = Column(String, unique=True, nullable=False)
    store_logo = Column(String , unique=False , nullable=False)
    payment_type = Column(String ,nullable = False) # post/pre delivery
    store_description = Column(Text)
    verified = Column(Boolean, default=False)

    plan_id = Column(Integer , ForeignKey("vendor_plans.id") ,nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    user = relationship("UserProfile", back_populates="vendor")
    _plan = relationship("VendorPlan" ,back_populates='vendors')
    custom_plan = relationship("CustomVendorPlan",backref='vendor',uselist=False)
    
    products = relationship("Product" ,back_populates='vendor',lazy='dynamic',cascade='all,delete')
    charges = relationship("VendorCharge", back_populates="vendor")

    @hybrid_property
    def plan(self):
        if self.custom_plan:
            return self.custom_plan
        return self._plan
    @plan.setter
    def plan(self, value):
        if isinstance(value ,VendorPlan):
            self._plan =value
        elif isinstance(value , CustomVendorPlan):
            self.custom_plan = value 
        else:
            raise Exception("Invalid value for vendor.plan")
    
    @hybrid_property
    def name(self):
        return self.user.name
    @name.setter
    def name(self ,value):
        self.user.name = value

    @hybrid_property
    def email(self):
        return self.user.email
    @email.setter
    def email(self ,value):
        self.user.email = value

    @hybrid_property
    def phone(self):
        return self.user.phone
    @phone.setter
    def phone(self ,value):
        self.user.phone = value
    

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
    batch_id = Column(String, nullable=False)
    tracking_id = Column(String(50), unique=True, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)

    status = Column(String(20), nullable=False) 
    method = Column(SQLENUM(PaymentMethod) , nullable=False) 
    updated_user_balance= Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return (
            f"<VendorPayout(id={self.id}, vendor_id={self.vendor_id}, amount={self.amount}, "
            f"status='{self.status}', method='{self.method})>"
        )

    def __str__(self):
        return self.__repr__()



