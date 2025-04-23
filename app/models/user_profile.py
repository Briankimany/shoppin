from sqlalchemy import Column, Integer, String, TIMESTAMP  , ForeignKey ,DateTime ,Boolean ,text 
from datetime import datetime
from sqlalchemy.sql import func
from .base import Base

class UserProfile(Base):
    __tablename__ = 'user_table'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True , unique = True)
    first_name = Column(String , nullable = True ,unique=False)
    second_name = Column(String , nullable = True , unique = False)  
    email = Column(String, unique=True, nullable=True) 
    phone = Column(String, unique=False, nullable=True) 
    password_hash = Column(String, nullable=True)  
    activated = Column(Boolean , server_default = text("FALSE") ,nullable = False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
   
    def __repr__(self):
        return (
            f"<UserProfile(id={self.id}, name='{self.name}', email='{self.email}', "
            f"phone='{self.phone}')>"
        )

    def __str__(self):
        return self.__repr__()


class TokenBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_table.id'), nullable=False)
    session_token = Column(String(255) )
    expires_at = Column(TIMESTAMP )


class ResetToken(TokenBase):
    __tablename__ = 'reset_tokens'
    reset_token = Column(String(255), unique=True ,nullable = False)

class AccountActivation(TokenBase):
    __tablename__ = "account_activations"
    token = Column(String(255),unique = True,nullable = False)



class UserBalance(Base):
    __tablename__ = "users_balance"
    id = Column(Integer ,ForeignKey('user_table.id') , primary_key=True,nullable= False)
    balance = Column(Integer)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)