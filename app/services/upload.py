
import cloudinary
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from config.config import JSONConfig

load_dotenv()


cloudinary.config(
    cloud_name =  os.getenv("CLOUD_NAME"),
    api_key =  os.getenv("API_KEY"),
    api_secret = os.getenv("API_SECRET"),
    secure=True
)

from cloudinary.utils import cloudinary_url
import cloudinary.uploader
import cloudinary.api

from app.models.images import ImageUpload
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


import base64
import hashlib


import os
import socket

class ImageManager:
    config = JSONConfig("config.json")

    IMAGE_SIZES = [
        {"width": 1000, "height": 1000},  # Main product image
        {"width": 500, "height": 500},    # Thumbnail
         {"width": 250, "height": 250},    # Gallery thumbnail
        {"width": 300, "height": 300},    # Gallery thumbnail
        {"width": 800, "height": 800},    # Medium
        {"width": 1920, "height": 1080}   # Hero
    ]

    @staticmethod
    def _validate_file(file):
        """Validate file before processing."""
        if not file or file.filename == '':
            raise ValueError("No valid file provided")

        allowed_extensions =ImageManager.config.allowed_extensions
        if '.' not in file.filename or file.filename.split('.')[-1].lower() not in allowed_extensions:
            raise ValueError("Invalid file type")

    @staticmethod
    def generate_public_id(filename):
        """Generate URL-safe public ID with random salt."""
        basename = os.path.splitext(os.path.basename(filename))[0]
        salt = os.urandom(4).hex()  # Add randomness to avoid collisions
        hash_bytes = hashlib.blake2b(f"{salt}{basename}".encode()).digest()
        return base64.urlsafe_b64encode(hash_bytes).decode()[:16]  # 16-char ID

    @staticmethod
    def upload_and_transform_image(image_path, public_id, size_idx=2):
        """Upload to Cloudinary with dynamic transformations."""
    
        if ImageManager.config.UPLOAD_IMAGES_DIRECTLY:
            upload_result = cloudinary.uploader.upload(
                image_path,
                public_id=public_id,
                overwrite=True
            )

            size = ImageManager.IMAGE_SIZES[size_idx]
            optimized_url, _ = cloudinary_url(
                upload_result['public_id'],
                width=size["width"],
                height=size["height"],
                crop="fill",
                quality="auto",
                fetch_format="webp"  # Force modern format
            )
            return optimized_url
        else:
            return None

    @staticmethod
    def record_image_upload(db_session:Session, image_url, public_id, vendor_id, filename):
        """Atomic database record creation."""
        try:
            image = ImageUpload(
                imageurl=image_url,
                uniqueid=public_id,
                vendorid=vendor_id,
                filename=filename
            )
            db_session.add(image)
            db_session.commit()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Database error: {str(e)}")
    @staticmethod
    def validate_image_not_duplicate(db_session:Session , name:str):
        image = db_session.query(ImageUpload).filter(ImageUpload.filename == name).first()
        return image
    
    @staticmethod
    def save_local_image_url(image_path:Path , image_url):
        json_file = Path(ImageManager.config.TEMP_UPLOAD_IMAGE_DIR) /'images.json'
        data = {}
        if os.path.exists(json_file):
            with open(json_file , 'r' ) as file:
                data =json.load(file)
        
        data[image_path.name] = {"path":str(image_path),"url":image_url}

        with open(json_file , 'w') as file:
            json.dump(data,file)
        
      

 
        