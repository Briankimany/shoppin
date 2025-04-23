from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from datetime import datetime, timedelta ,timezone
from .base import Base
from .user_profile import UserProfile
from .cart import Cart

class SessionTracking(Base):
    __tablename__ = 'session_tracking'
    token = Column(String, primary_key=True, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(hours=12))
    cart_id = Column(Integer, ForeignKey(Cart.id), nullable=False)
    user_id = Column(Integer, ForeignKey(UserProfile.id), nullable=True)

    def __repr__(self):
        return (
        f"<SessionTracking(token='{self.token}', expires_at='{self.expires_at}', cart_id={self.cart_id})> "
    )

    def __str__(self):
        return self.__repr__()
