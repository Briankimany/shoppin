
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text ,Enum ,text
from sqlalchemy.orm import relationship
from .base import Base ,TimeStampedBase
from .model_utils import PayoutFrequency
from decimal import Decimal

class VendorPlan(Base):
    __tablename__ = 'vendor_plans'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    product_commission_percent = Column(Float, nullable=False)
    products_flat_fee = Column(Integer, nullable=False)
    products_min_price_threshold = Column(Integer)

    payout_frequency = Column(Enum(PayoutFrequency) , nullable=False) 
    min_payout_threshold = Column(Integer,nullable = False)

    unscheduled_withdrawal_percentage = Column(Float, nullable=False)
    unscheduled_withdrawal_flat_fee = Column(Integer, nullable=False )
    max_unscheduled_withdrawal_fee = Column(Integer, nullable=False)

    scheduled_withdrawal_percentage = Column(Float, nullable=False)
    scheduled_withdrawal_flat_fee = Column(Integer, nullable=False )
    max_scheduled_withdrawal_fee = Column(Integer, nullable=False)

    marketing_grace_period = Column(Boolean, default=True)
    description = Column(Text)

    features = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")
    vendors = relationship("Vendor",back_populates='_plan',lazy='dynamic')
    vendorrequest=relationship("VendorSubmit" ,back_populates='plan',uselist=False)
    
    def product_commission(self,base_price):
         if base_price >=self.products_min_price_threshold:
              return (Decimal(self.product_commission_percent)/100)*base_price
         return self.products_flat_fee
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Convert model to dictionary representation.
        
        Args:
            include_relationships: Whether to include related objects
            
        Returns:
            Dictionary representation of the model
        """
        data = {
            'id': self.id,
            'name': self.name,
            'product_commission_percent': self.product_commission_percent,
            'products_flat_fee': self.products_flat_fee,
            'products_min_price_threshold': self.products_min_price_threshold,
            'payout_frequency': self.payout_frequency.value if self.payout_frequency else None,
            'min_payout_threshold': self.min_payout_threshold,
            'unscheduled_withdrawal_percentage': self.unscheduled_withdrawal_percentage,
            'unscheduled_withdrawal_flat_fee': self.unscheduled_withdrawal_flat_fee,
            'max_unscheduled_withdrawal_fee': self.max_unscheduled_withdrawal_fee,
            'scheduled_withdrawal_percentage': self.scheduled_withdrawal_percentage,
            'scheduled_withdrawal_flat_fee': self.scheduled_withdrawal_flat_fee,
            'max_scheduled_withdrawal_fee': self.max_scheduled_withdrawal_fee,
            'marketing_grace_period': self.marketing_grace_period,
            'description': self.description
        }
        
        if include_relationships:
            data['features'] = [feature.to_dict() for feature in self.features]
            # Don't include vendors/vendorrequest to avoid circular references
            
        return data

    def __repr__(self) -> str:
        """Unambiguous string representation for debugging."""
        return (
            f"<VendorPlan(id={self.id}, name='{self.name}', "
            f"commission={self.product_commission_percent}%, flat_fee={self.products_flat_fee}, "
            f"min_price={self.products_min_price_threshold}, payout={self.payout_frequency.name}, "
            f"min_payout={self.min_payout_threshold})>"
        )


    def __str__(self) -> str:
        """Readable string representation."""
        return self.__repr__()

class PlanFeature(Base):
    __tablename__ = 'plan_features'

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('vendor_plans.id'))
    custom_plan_id = Column(Integer, ForeignKey('custom_vendor_plans.id'))
    
    feature_text = Column(Text, nullable=False)

    plan = relationship("VendorPlan", back_populates="features")
    custom_plan = relationship("CustomVendorPlan",back_populates='custom_features')
    
    def to_dict(self, include_plan: bool = False) -> dict:
        """Convert model to dictionary representation.
        
        Args:
            include_plan: Whether to include the related plan object
            
        Returns:
            Dictionary representation of the model
        """
        data = {
            'id': self.id,
            'plan_id': self.plan_id,
            'feature_text': self.feature_text
        }
        
        if include_plan and self.plan:
            data['plan'] = self.plan.to_dict()
            
        return data

    def __repr__(self) -> str:
            """Unambiguous string representation for debugging."""
            return (
                f"<PlanFeature(id={self.id}, plan_id={self.plan_id}, "
                f"feature_text='{self.feature_text[:20]}...')>"
            )

    def __str__(self) -> str:
            """Readable string representation."""
            return f"PlanFeature {self.id} (Plan: {self.plan_id}) - {self.feature_text[:50]}..."