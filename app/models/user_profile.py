from sqlalchemy import Column, Integer, String, TIMESTAMP  , ForeignKey ,DateTime
from datetime import datetime
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

    def __repr__(self):
        return (
            f"<UserProfile(id={self.id}, name='{self.name}', email='{self.email}', "
            f"phone='{self.phone}')>"
        )

    def __str__(self):
        return self.__repr__()



class ResetToken(Base):
    __tablename__ = 'reset_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_token = Column(String(255))
    reset_token = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('user_table.id'), nullable=False)
    expires_at = Column(TIMESTAMP )

class UserBalance(Base):
    __tablename__ = "users_balance"
    id = Column(Integer ,ForeignKey('user_table.id') , primary_key=True,nullable= False)
    balance = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)