from sqlalchemy import Column, Integer, String, TIMESTAMP  , ForeignKey ,DateTime
from sqlalchemy.sql import func
from .base import Base

class UserProfile(Base):
    __tablename__ = 'user_table'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True , unique = True)  
    email = Column(String, unique=True, nullable=True) 
    phone = Column(String, unique=False, nullable=True) 
    password_hash = Column(String, nullable=True)  
    created_at = Column(TIMESTAMP, server_default=func.now())


class ResetToken(Base):
    __tablename__ = 'reset_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_token = Column(String(255))
    reset_token = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user_table.id'), nullable=False)
    expires_at = Column(TIMESTAMP )
