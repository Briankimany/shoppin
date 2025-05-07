
from .base import TimeStampedBase  ,VendorRequestStatus

from sqlalchemy import Integer , String ,Column,ForeignKey,Text ,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import Enum


class VendorSubmit(TimeStampedBase):

    __tablename__ = "vendors_submits"

    id = Column(Integer , primary_key=True,autoincrement=True)
    
    name = Column(String ,unique=True,nullable=False)
    first_name = Column(String , nullable=False)
    second_name = Column(String ,nullable=False)
    agreed_terms = Column(Boolean , default = False)

    email = Column(String ,unique=True,nullable=False)
    phone = Column(String , nullable=False)
    
    store_name = Column(String, unique=True, nullable=False)
    payment_type = Column(String ,nullable = False) 
    store_description = Column(Text)

    plan_id = Column(Integer , ForeignKey("vendor_plans.id") ,nullable=False)

    status = Column(Enum(VendorRequestStatus), nullable=False, 
                    default=VendorRequestStatus.PENDING)
    
    plan = relationship("VendorPlan" ,back_populates='vendorrequest')

    def __repr__(self):
        return f"<VendorSubmit(id={self.id}, name='{self.name}', email='{self.email}', status='{self.status.value}')>"

    def __str__(self):
        return f"Vendor Application: {self.name} ({self.store_name}) - {self.status.value.capitalize()}"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "first_name": self.first_name,
            "second_name": self.second_name,
            "email": self.email,
            "phone": self.phone,
            "store_name": self.store_name,
            "payment_type": self.payment_type,
            "store_description": self.store_description,
            "status": self.status.value,
            "plan_id": self.plan_id,
            "created_at": self.created_at.isoformat(' ','hours') if self.created_at else None,
            "updated_at": self.updated_at.isoformat(' ' ,'hours') if self.updated_at else None
        }


