from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from datetime import datetime, timedelta
from .base import Base
from .user_profile import UserProfile
from .cart import Cart

class SessionTracking(Base):
    __tablename__ = 'session_tracking'
    token = Column(String, primary_key=True, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(hours=12))
    cart_id = Column(Integer, ForeignKey(Cart.id), nullable=False)
    user_id = Column(Integer, ForeignKey(UserProfile.id), nullable=True)
    ip_address = Column(String, nullable=True)
    country = Column(String, nullable=True)
    region = Column(String, nullable=True)
    city = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    device = Column(String, nullable=True)
    consent_given = Column(Boolean, default=False)

