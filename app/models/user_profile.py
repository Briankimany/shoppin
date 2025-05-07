from sqlalchemy import Column, Integer, String, TIMESTAMP,DECIMAL  , ForeignKey ,DateTime ,Boolean ,text
from sqlalchemy.orm import relationship
from datetime import datetime ,timezone
from sqlalchemy.sql import func
from .utils import Base 

class UserProfile(Base):
    __tablename__ = 'users_table'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True , unique = True)
    first_name = Column(String , nullable = True ,unique=False)
    second_name = Column(String , nullable = True , unique = False)  
    email = Column(String, unique=True, nullable=True) 
    phone = Column(String, unique=False, nullable=True) 
    password_hash = Column(String, nullable=True)  

    clearance_id = Column(Integer,ForeignKey("clearance_levels.id"),nullable=False)
    
    activated = Column(Boolean , server_default = text("FALSE") ,nullable = False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    vendor = relationship("Vendor", back_populates="user", uselist=False)
    clearance = relationship("ClearanceLevel" ,back_populates='users')
    balance = relationship("UserBalance",backref='user',uselist=False)

    @property
    def is_admin(self):
        return self.clearance.level == 1

    @property
    def is_staff(self):
        return self.clearance.level <= 2

    def __repr__(self):
        return (
            f"<UserProfile(id={self.id}, name='{self.name}', email='{self.email}', "
            f"phone='{self.phone}') clearance='{self.clearance}'>"
        )
    

    def __str__(self):
        return self.__repr__()


class TokenBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users_table.id'), nullable=False)
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
    id = Column(Integer ,ForeignKey('users_table.id') , primary_key=True,nullable= False)
    balance = Column(DECIMAL)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))