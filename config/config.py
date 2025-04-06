# config.py

import json
import os
from pathlib import Path
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()
authkey = os.getenv("AUTHKEY")
DEFAULT_SETTINGS = {
    "database_url": "vendor_project.db",
    "log_file": "/var/logs/vendor_project.log",
    "debug": True,
    "uploads_dir_path": "uploads",
    "payment_url": "http://playpit.pythonanywhere.com",
    "DELAY_BEFORE_STATUS_CHECK":2,
    "MAX_RETIRES":3,
    "SIMULATE": True,
    "allowed_extensions":['jpg', 'jpeg', 'png', 'webp' ,'svg']
}
PATHS_LIST = ['uploads_dir_path' ,'TEMP_UPLOAD_IMAGE_DIR']

image_urls = [
    {
        "width": 1000,
        "height": 1000,
        "link": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_fill,f_auto,h_1000,q_auto,w_1000/shoes"
    },
    {
        "width": 500,
        "height": 500,
        "link": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_fill,f_auto,h_500,q_auto,w_500/shoes"
    },
    {
        "width": 300,
        "height": 300,
        "link": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_fill,f_auto,h_300,q_auto,w_300/shoes"
    },
    {
        "width": 800,
        "height": 800,
        "link": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_fill,f_auto,h_800,q_auto,w_800/shoes"
    },
    {
        "width": 1920,
        "height": 1080,
        "link": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_fill,f_auto,h_1080,q_auto,w_1920/shoes"
    }
]



class Config(ABC):
    def __init__(self, json_path: str, default_data = None):
        self.json_path = Path(json_path)
        self.default_data = default_data if default_data else DEFAULT_SETTINGS 
        self.authkey = authkey
        self.UPLOAD_DIR = str(Path().cwd()/"app/static/uploads")
        self.allowed_extensions = ['jpg', 'jpeg', 'png', 'webp' ,'svg']
        self.UPLOAD_IMAGES_DIRECTLY = os.getenv("UPLOAD_IMAGES_DIRECTLY","false") == "true"

        self.TEMP_UPLOAD_IMAGE_DIR = Path(self.UPLOAD_DIR)/'temp'
        self.TEMP_UPLOAD_IMAGE_DIR.mkdir(parents= True ,exist_ok=True)
        self.TEMP_UPLOAD_IMAGE_DIR = str(self.TEMP_UPLOAD_IMAGE_DIR)

        if not self.json_path.exists():
            self.__save__(self.default_data)
            self._load_attributes(self.default_data)
        else:
            self.__load__()

        self.SQLITE_DATABASE_URL = f"sqlite:///{self.database_url.absolute()}"

    @abstractmethod
    def __load__(self):
        """Load configuration from the given  file path."""
        pass
    
    def _load_attributes(self, data: dict):
        """Set class attributes from a dictionary, converting paths where necessary."""
        for key, value in data.items():
            if  isinstance(value, str):
                if Path(value).suffix in ['.db', '.log'] or key in PATHS_LIST:
                    value = Path(value)
            setattr(self, key, value)
            
    @abstractmethod
    def __save__(self, data: dict):
        """Save dictionary to a file."""
        pass


class JSONConfig(Config):
    def __load__(self):
        """Implementation of abstract method to load JSON data and set attributes."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._load_attributes(data)
      
        self.uploads_dir_path.mkdir(parents=True , exist_ok= True)
    def __save__(self, data: dict):
        """Save dictionary data to JSON file."""
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)






