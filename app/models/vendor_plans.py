
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base

class VendorPlan(Base):
    __tablename__ = 'vendor_plans'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    commission_percent = Column(Float, nullable=False)
    flat_fee = Column(Integer, nullable=False)
    min_price_threshold = Column(Integer, default=0)
    payout_frequency = Column(String(50))  # e.g., 'monthly', 'bi-weekly'
    marketing_grace_period = Column(Boolean, default=True)
    description = Column(Text)

    features = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")
    vendors = relationship("Vendor",back_populates='plan',lazy='dynamic')
    vendorrequest=relationship("VendorSubmit" ,back_populates='plan')
    
    def to_dict(self):
        return {
            "commision_percent":self.commission_percent,
            "flat_fee":self.flat_fee,
            "min_price":self.min_price_threshold,
        }

class PlanFeature(Base):
    __tablename__ = 'plan_features'

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('vendor_plans.id'), nullable=False)
    feature_text = Column(Text, nullable=False)

    plan = relationship("VendorPlan", back_populates="features")
 