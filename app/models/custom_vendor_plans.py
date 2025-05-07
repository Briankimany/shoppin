from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text ,Enum ,text ,case
from sqlalchemy.orm import relationship
from .base import Base ,TimeStampedBase
from .model_utils import PayoutFrequency
from decimal import Decimal
from sqlalchemy.ext.hybrid import hybrid_property
from .vendor_plans import VendorPlan

class CustomVendorPlan(TimeStampedBase):
    __tablename__ = 'custom_vendor_plans'
    
    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey('vendors.id'), unique=True, nullable=False)
    base_plan_id = Column(Integer, ForeignKey('vendor_plans.id'), nullable=False)
    
    # All columns with underscore prefix
    _product_commission_percent = Column('product_commission_percent', Float)
    _products_flat_fee = Column('products_flat_fee', Integer)
    _products_min_price_threshold = Column('products_min_price_threshold', Integer)
    _payout_frequency = Column('payout_frequency', Enum(PayoutFrequency))
    _min_payout_threshold = Column('min_payout_threshold', Integer)
    _unscheduled_withdrawal_percentage = Column('unscheduled_withdrawal_percentage', Float)
    _unscheduled_withdrawal_flat_fee = Column('unscheduled_withdrawal_flat_fee', Integer)
    _max_unscheduled_withdrawal_fee = Column('max_unscheduled_withdrawal_fee', Integer)
    _scheduled_withdrawal_percentage = Column('scheduled_withdrawal_percentage', Float)
    _scheduled_withdrawal_flat_fee = Column('scheduled_withdrawal_flat_fee', Integer)
    _max_scheduled_withdrawal_fee = Column('max_scheduled_withdrawal_fee', Integer)
    _marketing_grace_period = Column('marketing_grace_period', Boolean)
    

    base_plan = relationship("VendorPlan")
    custom_features= relationship("PlanFeature", back_populates="custom_plan", cascade="all, delete-orphan")

    @hybrid_property
    def features(self):
        return self.base_plan.features if not self.custom_features else self.custom_features
    @hybrid_property
    def name(self):
        return self.vendor.name

    # HYBRID PROPERTIES 
    @hybrid_property
    def product_commission_percent(self):
        return self._product_commission_percent if self._product_commission_percent is not None else self.base_plan.product_commission_percent

    @hybrid_property
    def products_flat_fee(self):
        return self._products_flat_fee if self._products_flat_fee is not None else self.base_plan.products_flat_fee

    @hybrid_property
    def products_min_price_threshold(self):
        return self._products_min_price_threshold if self._products_min_price_threshold is not None else self.base_plan.products_min_price_threshold

    @hybrid_property
    def payout_frequency(self):
        return self._payout_frequency if self._payout_frequency is not None else self.base_plan.payout_frequency

    @hybrid_property
    def min_payout_threshold(self):
        return self._min_payout_threshold if self._min_payout_threshold is not None else self.base_plan.min_payout_threshold

    @hybrid_property
    def unscheduled_withdrawal_percentage(self):
        return self._unscheduled_withdrawal_percentage if self._unscheduled_withdrawal_percentage is not None else self.base_plan.unscheduled_withdrawal_percentage

    @hybrid_property
    def unscheduled_withdrawal_flat_fee(self):
        return self._unscheduled_withdrawal_flat_fee if self._unscheduled_withdrawal_flat_fee is not None else self.base_plan.unscheduled_withdrawal_flat_fee

    @hybrid_property
    def max_unscheduled_withdrawal_fee(self):
        return self._max_unscheduled_withdrawal_fee if self._max_unscheduled_withdrawal_fee is not None else self.base_plan.max_unscheduled_withdrawal_fee

    @hybrid_property
    def scheduled_withdrawal_percentage(self):
        return self._scheduled_withdrawal_percentage if self._scheduled_withdrawal_percentage is not None else self.base_plan.scheduled_withdrawal_percentage

    @hybrid_property
    def scheduled_withdrawal_flat_fee(self):
        return self._scheduled_withdrawal_flat_fee if self._scheduled_withdrawal_flat_fee is not None else self.base_plan.scheduled_withdrawal_flat_fee

    @hybrid_property
    def max_scheduled_withdrawal_fee(self):
        return self._max_scheduled_withdrawal_fee if self._max_scheduled_withdrawal_fee is not None else self.base_plan.max_scheduled_withdrawal_fee

    @hybrid_property
    def marketing_grace_period(self):
        return self._marketing_grace_period if self._marketing_grace_period is not None else self.base_plan.marketing_grace_period

    # EXPRESSION DEFINITIONS (complete set)
    @product_commission_percent.expression
    def product_commission_percent(cls):
        return case(
            [(cls._product_commission_percent != None, cls._product_commission_percent)],
            else_=VendorPlan.product_commission_percent
        )

    @products_flat_fee.expression
    def products_flat_fee(cls):
        return case(
            [(cls._products_flat_fee != None, cls._products_flat_fee)],
            else_=VendorPlan.products_flat_fee
        )

    @products_min_price_threshold.expression
    def products_min_price_threshold(cls):
        return case(
            [(cls._products_min_price_threshold != None, cls._products_min_price_threshold)],
            else_=VendorPlan.products_min_price_threshold
        )

    @payout_frequency.expression
    def payout_frequency(cls):
        return case(
            [(cls._payout_frequency != None, cls._payout_frequency)],
            else_=VendorPlan.payout_frequency
        )

    @min_payout_threshold.expression
    def min_payout_threshold(cls):
        return case(
            [(cls._min_payout_threshold != None, cls._min_payout_threshold)],
            else_=VendorPlan.min_payout_threshold
        )

    @unscheduled_withdrawal_percentage.expression
    def unscheduled_withdrawal_percentage(cls):
        return case(
            [(cls._unscheduled_withdrawal_percentage != None, cls._unscheduled_withdrawal_percentage)],
            else_=VendorPlan.unscheduled_withdrawal_percentage
        )

    @unscheduled_withdrawal_flat_fee.expression
    def unscheduled_withdrawal_flat_fee(cls):
        return case(
            [(cls._unscheduled_withdrawal_flat_fee != None, cls._unscheduled_withdrawal_flat_fee)],
            else_=VendorPlan.unscheduled_withdrawal_flat_fee
        )

    @max_unscheduled_withdrawal_fee.expression
    def max_unscheduled_withdrawal_fee(cls):
        return case(
            [(cls._max_unscheduled_withdrawal_fee != None, cls._max_unscheduled_withdrawal_fee)],
            else_=VendorPlan.max_unscheduled_withdrawal_fee
        )

    @scheduled_withdrawal_percentage.expression
    def scheduled_withdrawal_percentage(cls):
        return case(
            [(cls._scheduled_withdrawal_percentage != None, cls._scheduled_withdrawal_percentage)],
            else_=VendorPlan.scheduled_withdrawal_percentage
        )

    @scheduled_withdrawal_flat_fee.expression
    def scheduled_withdrawal_flat_fee(cls):
        return case(
            [(cls._scheduled_withdrawal_flat_fee != None, cls._scheduled_withdrawal_flat_fee)],
            else_=VendorPlan.scheduled_withdrawal_flat_fee
        )

    @max_scheduled_withdrawal_fee.expression
    def max_scheduled_withdrawal_fee(cls):
        return case(
            [(cls._max_scheduled_withdrawal_fee != None, cls._max_scheduled_withdrawal_fee)],
            else_=VendorPlan.max_scheduled_withdrawal_fee
        )

    @marketing_grace_period.expression
    def marketing_grace_period(cls):
        return case(
            [(cls._marketing_grace_period != None, cls._marketing_grace_period)],
            else_=VendorPlan.marketing_grace_period
        )


    # SETTER METHODS 
    @product_commission_percent.setter
    def product_commission_percent(self, value):
        self._product_commission_percent = value

    @products_flat_fee.setter
    def products_flat_fee(self, value):
        self._products_flat_fee = value

    @products_min_price_threshold.setter
    def products_min_price_threshold(self, value):
        self._products_min_price_threshold = value

    @payout_frequency.setter
    def payout_frequency(self, value):
        self._payout_frequency = value

    @min_payout_threshold.setter
    def min_payout_threshold(self, value):
        self._min_payout_threshold = value

    @unscheduled_withdrawal_percentage.setter
    def unscheduled_withdrawal_percentage(self, value):
        self._unscheduled_withdrawal_percentage = value

    @unscheduled_withdrawal_flat_fee.setter
    def unscheduled_withdrawal_flat_fee(self, value):
        self._unscheduled_withdrawal_flat_fee = value

    @max_unscheduled_withdrawal_fee.setter
    def max_unscheduled_withdrawal_fee(self, value):
        self._max_unscheduled_withdrawal_fee = value

    @scheduled_withdrawal_percentage.setter
    def scheduled_withdrawal_percentage(self, value):
        self._scheduled_withdrawal_percentage = value

    @scheduled_withdrawal_flat_fee.setter
    def scheduled_withdrawal_flat_fee(self, value):
        self._scheduled_withdrawal_flat_fee = value

    @max_scheduled_withdrawal_fee.setter
    def max_scheduled_withdrawal_fee(self, value):
        self._max_scheduled_withdrawal_fee = value

    @marketing_grace_period.setter
    def marketing_grace_period(self, value):
        self._marketing_grace_period = value

    
    def product_commission(self,base_price):
        if base_price >=self.products_min_price_threshold:
            return (Decimal(self.product_commission_percent)/100)*base_price
        
        return self.products_flat_fee

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