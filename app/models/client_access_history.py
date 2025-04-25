from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime
from typing import Dict, Any

from .base import Base ,get_time

class ClientAccessLog(Base):
    __tablename__ = 'client_access_logs'

    id = Column(Integer, primary_key=True)

    ip_address = Column(String(45), nullable=False) 
    proxy = Column(Boolean, default=False)
    
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    isp = Column(String(100), nullable=True)

    user_agent = Column(String(500), nullable=True)  
    browser = Column(String(100), nullable=True)
    device = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)

    consent_given = Column(Boolean, default=False)
    accessed_at = Column(DateTime, default=get_time(), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the model instance to a dictionary.
        
        Returns:
            Dictionary representation of the model with all column values.
            Datetime objects are converted to ISO format strings.
        """
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'proxy': self.proxy,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'isp': self.isp,
            'user_agent': self.user_agent,
            'browser': self.browser,
            'device': self.device,
            'os': self.os,
            'accessed_at': self.accessed_at.isoformat() if self.accessed_at else None
        }

    def __repr__(self) -> str:
        return f"<ClientAccessLog(id={self.id}, ip='{self.ip_address}', accessed_at={self.accessed_at})>"


