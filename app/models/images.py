
from .base import Base
from .vendor import Vendor

from sqlalchemy import String , ForeignKey ,Column , TIMESTAMP , func ,Integer

class ImageUpload(Base):
    __tablename__ = "uploaded_images"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  
    vendorid = Column(ForeignKey('vendors.id'), nullable=False)
    uniqueid = Column(String(64), nullable=False, unique=True)  
    filename = Column(String(255), nullable=False)
    imageurl = Column(String(512), nullable=False)  
    uploaded_at = Column(TIMESTAMP, server_default=func.now())  