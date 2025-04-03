
import cloudinary
from dotenv import load_dotenv
import os
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
        # try:
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
        # except Exception as e:
        #     raise RuntimeError(f"Cloudinary upload failed: {str(e)}")

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