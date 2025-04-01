import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url


from dotenv import load_dotenv
import os

from app.models.images import ImageUpload
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


import base64
import hashlib

load_dotenv()


CLAUDINAR_API_NAME = os.getenv("CLAUDINAR_API_NAME")
CLAUDINAR_API_KEY   = os.getenv("CLAUDINAR_API_KEY")
CLAUDINAR_API_SECRET = os.getenv("CLAUDINAR_API_SECRET")

cloudinary.config( 
    cloud_name = CLAUDINAR_API_NAME, 
    api_key = CLAUDINAR_API_KEY, 
    api_secret = CLAUDINAR_API_SECRET,
    secure=True
)

class ImageManager:

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
        
        allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
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
        try:
            upload_result = cloudinary.uploader.upload(
                image_path,
                public_id=f"vendor_uploads/{public_id}",  
                overwrite=False  
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
        except Exception as e:
            raise RuntimeError(f"Cloudinary upload failed: {str(e)}")

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
            db_session.rollback()
            raise RuntimeError(f"Database error: {str(e)}")