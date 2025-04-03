
from .base import Base
from .vendor import Vendor

from sqlalchemy import String , ForeignKey ,Column , TIMESTAMP , func ,Integer

from pathlib import Path
from config.config import JSONConfig

class ImageUpload(Base):
    __tablename__ = "uploaded_images"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  
    vendorid = Column(ForeignKey('vendors.id'), nullable=False)
    uniqueid = Column(String(64), nullable=False, unique=True)  
    filename = Column(String(255), nullable=False)
    imageurl = Column(String(512), nullable=False)  
    uploaded_at = Column(TIMESTAMP, server_default=func.now())  

 
    def __remove_local_file__(self):
        """Safely removes the local file associated with this image upload."""
        try:
            config = JSONConfig('config.json')
            file_path = Path(config.TEMP_UPLOAD_IMAGE_DIR) / self.filename
            
            if file_path.exists():
                file_path.unlink()  
                return True
            return False
        except Exception as e:
            print(f"Error removing file {self.filename}: {str(e)}")
            return False

    
    def __repr__(self):
       
        return (
            f"<ImageUpload(id={self.id}, "
            f"vendorid={self.vendorid}, "
            f"filename='{self.filename}', "
            f"uploaded_at={self.uploaded_at})>"
        )
    def to_dict (self):
        return {
            'vendorid': self.vendorid,
            'uniqueid': self.uniqueid,
            'filename': self.filename,
            'imageurl': self.imageurl
        }

    def __str__(self):
        return self.__repr__()
    
        

