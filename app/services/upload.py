
import cloudinary
from dotenv import load_dotenv
import os
import json
from pathlib import Path

from config.config import JSONConfig
from app.models.product import Product
from app.models.vendor import Vendor
from app.routes.logger import LOG

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
        salt = os.urandom(4).hex()  
        hash_bytes = hashlib.blake2b(f"{salt}{basename}".encode()).digest()
        return base64.urlsafe_b64encode(hash_bytes).decode()[:16] 

    @staticmethod
    def upload_and_transform_image(image_path, public_id, size_idx=2 ,override_config=False):
        """Upload to Cloudinary with dynamic transformations."""
    
        if ImageManager.config.UPLOAD_IMAGES_DIRECTLY or override_config:
            upload_result = cloudinary.uploader.upload(
                image_path,
                public_id=public_id,
                overwrite=True
            )
            LOG.ADMIN_LOGGER.info(f"UPLOADED IMAGE ADN GOR THIS {upload_result}")
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
    def _load_json(path:Path):
        """Load JSON data from a file if it exists, otherwise return an empty dict.
        
        Args:
            path (Path): Path to the JSON file
            
        Returns:
            dict: Parsed JSON data or empty dict if file doesn't exist
        """

        if path.exists():
            with open(path , 'r' ) as file:
                data =json.load(file)
        else:
            data = {}
        return data
        

    @staticmethod
    def save_local_image_url(image_path:Path , image_url):
        """Save image path and URL mapping to a JSON file.
        
        Args:
            image_path (Path): Local path to the image file
            image_url (str): URL associated with the image
        """

        json_file = Path(ImageManager.config.json_path.parent) /'temp_images.json'

        data = ImageManager._load_json(json_file)

        data[image_path.name] = {"path":str(image_path),"url":image_url}

        with open(json_file , 'w') as file:
            json.dump(data,file)
    @staticmethod
    def load_migration_images(db_sessoin:Session, json_file:Path):
        """Load image records from database based on filenames in JSON file.
        
        Args:
            db_session (Session): Database session
            json_file (Path): Path to JSON file containing image filenames
            
        Returns:
            list: List of image data dictionaries
        """

        json_data = ImageManager._load_json(json_file)
        names = json_data.keys()
        results =[]
        for name in names:
            image = db_sessoin.query(ImageUpload).filter(ImageUpload.filename==name).first()
            
            image_path = Path(ImageManager.config.TEMP_UPLOAD_IMAGE_DIR) /str(image.filename)
            if image_path.exists():
                results.append(image.to_dict())
        return results
    
    @staticmethod
    def migrate_images(data):
        """Process image migration by uploading and transforming images.
        
        Args:
            data (list): List of image dictionaries containing:
                - filename
                - imageurl 
                - uniqueid
                - vendorid
                
        Returns:
            list: Processed image data with new URLs
        """
     
        all_data =[]
        for item in data:
            uniqueid = item['uniqueid']
            vendor_id = item['vendorid']
            image_url = item['imageurl']
            optimized_url =ImageManager.upload_and_transform_image(image_path=image_url,
                                                    override_config=True,
                                                    public_id=item['uniqueid'],size_idx=3)

            data = {'old_src': image_url,"uniqueid":uniqueid ,
                     'remote_src':optimized_url ,"vendor_id":vendor_id}
            all_data.append(data)
            
        return all_data

            
    @staticmethod
    def update_images_src_links(db_session: Session, image_data):
        """Update database records with new image URLs.
        
        Args:
            db_session (Session): Database session
            image_data (dict): Migration data containing:
                - uniqueid
                - remote_src
                - old_src
                - vendor_id
                
        Returns:
            dict: Update status for each record type
        Raises:
            ValueError: If required fields are missing or image not found
        """
        try:
            uniqueid = image_data.get('uniqueid')
            cloudinary_url = image_data.get('remote_src')
            old_link = image_data.get('old_src')
            vendor_id = image_data.get('vendor_id')
          

            if not all([uniqueid, cloudinary_url, old_link, vendor_id]):
                raise ValueError("Missing required fields in image_data")

            image = db_session.query(ImageUpload).filter(ImageUpload.uniqueid == uniqueid).first()
            if not image:
                raise ValueError(f"Image with uniqueid {uniqueid} not found")

            image.imageurl = cloudinary_url
    
            vendor = db_session.query(Vendor).filter(
                Vendor.id == vendor_id,
                Vendor.store_logo == old_link
            ).first()
            if vendor:
                vendor.store_logo = cloudinary_url
            else:
                product = db_session.query(Product).filter(
                    Product.vendor_id == vendor_id,
                    Product.image_url == old_link
                ).first()
                if product:
                    product.image_url = cloudinary_url

            db_session.commit()
            ImageManager.__remove_local_file__(image.filename)
            return  {
                    "image_upload_updated": bool(image),
                    "vendor_updated": bool(vendor),
                    "product_updated": bool(product)
                }
        except Exception as e:
            db_session.rollback() 
            raise  

    @staticmethod
    def __remove_local_file__(filename:str) -> bool:
        """Remove local image file after successful migration.
    
        Args:
            filename (str): Name of file to remove
            
        Returns:
            bool: True if file was removed, False otherwise
        """
        try:
            file_path = Path(ImageManager.config.TEMP_UPLOAD_IMAGE_DIR)/ filename
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            LOG.ADMIN_LOGGER.info(f"Error removing file {filename}: {str(e)}")
            return False