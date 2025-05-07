
from sqlalchemy.orm import Session

from app.models.vendor import Vendor
from app.models.product import Product
from app.routes.vendor import sessionmaker , engine
from config.config import JSONConfig

from typing import List
import csv
from app.data_manager.charges_manager import ChargeRuleManager ,Payee

DbSession = sessionmaker(bind=engine)
conf = JSONConfig("config.json")

def get_urls_from_csv(csv_path: str) -> list[str]:
    """Read URLs from a single-column CSV and return as list."""
    with open(csv_path, mode='r') as file:
        reader = csv.reader(file)
        return ([row[0] for row in reader if row] )[1:] 


def add_muliple_prodct(db_session:Session,p:list[Product]):

    """Add multiple products to the database."""
    products_list =[]
    for product in p:
        existing_product = db_session.query(Product).filter(Product.name == product.name).first()
        if existing_product:
            print(f"Product with name {product.name} already exists, skipping.")
            continue
        else:
            print(f"Adding product: {product.name}")
        products_list.append(product)

    if products_list:
        db_session.add_all(products_list)
        db_session.commit()

def get_image(vendor_key):
    image_map = {
        "vendor1": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743681390/b470ZdEWk3d2kQWT.webp",
        "vendor2": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743517291/samples/outdoor-woman.jpg",
        "vendor3": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743517284/samples/food/spices.jpg",
        "vendor4": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743691066/tech_support_zafgsj.webp"
    }
    return image_map[vendor_key]

def get_image_url(name,is_preview):
    return get_image('vendor1')


sample_products = [
    # Vendor 1 (Electronics)
    {
        "vendor_id": 1,
        "name": "Wireless Bluetooth Earbuds",
         "vendor's_commision_coverage":10,
        "price": 59.99,
        "stock": 150,
        "image_url": get_image_url("earbuds", is_preview=False),
        "preview_url": get_image_url("earbuds", is_preview=True)
    },
    {
        "vendor_id": 1,
        "name": "Smart Watch Pro",
        "price": 199.99,
        "stock": 75,
        "image_url": get_image_url("smartwatch", is_preview=False),
        "preview_url": get_image_url("smartwatch", is_preview=True)
    },
    {
        "vendor_id": 1,
        "name": "Portable Charger 10000mAh",
        "price": 29.99,
        "stock": 200,
        "image_url": None, 
        "preview_url": None
    },
     {
        "vendor_id": 1,
        "name": "Gaming console",
         "vendor's_commision_coverage":70,
        "price": 25000,
        "stock": 200,
        "image_url": None,  
        "preview_url": None
    },

    # Vendor 2 (Books)
    {
        "vendor_id": 2,
        "name": "Python Programming Cookbook",
        "price": 39.95,
        "stock": 50,
        "image_url": get_image_url("python-book", is_preview=False),
        "preview_url": get_image_url("python-book", is_preview=True)
    },
    {
        "vendor_id": 2,
        "name": "The Art of Computer Science",
        "price": 89.99,
        "stock": 30,
        "image_url": get_image_url("cs-art", is_preview=False),
        "preview_url": None 
    },
    {
        "vendor_id": 2,
        "name": "Database Design Essentials",
        "price": 49.50,
        "stock": 0,
        "image_url": get_image_url("database-book", is_preview=False),
        "preview_url": get_image_url("database-book", is_preview=True)
    },

    # Vendor 3 (Home Goods)
    {
        "vendor_id": 3,
        "name": "Organic Cotton Bed Sheets",
        "price": 79.99,
        "stock": 120,
        "image_url": get_image_url("bedsheets", is_preview=False),
        "preview_url": get_image_url("bedsheets", is_preview=True)
    },
    {
        "vendor_id": 3,
        "name": "Ceramic Dinnerware Set",
        "price": 129.99,
        "stock": 45,
        "image_url": get_image_url("dinnerware", is_preview=False),
        "preview_url": get_image_url("dinnerware", is_preview=True)
    },
    {
        "vendor_id": 3,
        "name": "Stainless Steel Cookware",
        "price": 149.99,
        "stock": 30,
        "image_url": None,
        "preview_url": None
    },
        {
        "vendor_id": 3,
        "vendor's_commision_coverage":40,
        "name": "StCookware",
        "price": 149.99,
        "stock": 30,
        "image_url": None, 
        "preview_url": None
    },
    {
        "vendor_id": 3,
        "vendor's_commision_coverage":40,
        "name": "Pan",
        "price": 100,
        "stock": 30,
        "image_url": None,  
        "preview_url": None
    },
    {
        "vendor_id": 1,
        "name": "Portable Charger 10000mAh",
        "price": 614.31,
        "stock": 57,
        "image_url": "get_image_url('portable_charger', is_preview=False)",
        "preview_url": "get_image_url('portable_charger', is_preview=True)",
        "vendor's_commision_coverage": 50
    },
    {
        "vendor_id": 1,
        "name": "Gaming Console",
        "price": 1184.08,
        "stock": 74,
        "image_url": "get_image_url('gaming_console', is_preview=False)",
        "preview_url": "get_image_url('gaming_console', is_preview=True)",
        "vendor's_commision_coverage": 70
    },
    {
        "vendor_id": 1,
        "name": "Smartphone X2",
        "price": 676.20,
        "stock": 89,
        "image_url": "get_image_url('smartphone_x2', is_preview=False)",
        "preview_url": "get_image_url('smartphone_x2', is_preview=True)",
        "vendor's_commision_coverage": 30
    },
    {
        "vendor_id": 1,
        "name": "Wireless Bluetooth Earbuds",
        "price": 1170.00,
        "stock": 164,
        "image_url": "get_image_url('earbuds', is_preview=False)",
        "preview_url": "get_image_url('earbuds', is_preview=True)",
        "vendor's_commision_coverage": 10
    },
    {
        "vendor_id": 1,
        "name": "Smart Watch Pro",
        "price": 1945.55,
        "stock": 156,
        "image_url": "get_image_url('smart_watch_pro', is_preview=False)",
        "preview_url": "get_image_url('smart_watch_pro', is_preview=True)",
        "vendor's_commision_coverage": 20
    },
    {
        "vendor_id": 1,
        "name": "Laptop Air 15",
        "price": 1840.66,
        "stock": 60,
        "image_url": "get_image_url('laptop_air_15', is_preview=False)",
        "preview_url": "get_image_url('laptop_air_15', is_preview=True)",
        "vendor's_commision_coverage": 80
    },
    {
        "vendor_id": 1,
        "name": "4K LED Television",
        "price": 1593.89,
        "stock": 198,
        "image_url": "get_image_url('4k_led_tv', is_preview=False)",
        "preview_url": "get_image_url('4k_led_tv', is_preview=True)",
        "vendor's_commision_coverage": 60
    },
    {
        "vendor_id": 1,
        "name": "Wireless Headphones",
        "price": 1088.97,
        "stock": 89,
        "image_url": "get_image_url('wireless_headphones', is_preview=False)",
        "preview_url": "get_image_url('wireless_headphones', is_preview=True)",
        "vendor's_commision_coverage": 40
    },
    {
        "vendor_id": 1,
        "name": "Bluetooth Speaker",
        "price": 1509.67,
        "stock": 54,
        "image_url": "get_image_url('bluetooth_speaker', is_preview=False)",
        "preview_url": "get_image_url('bluetooth_speaker', is_preview=True)",
        "vendor's_commision_coverage": 15
    },
    {
        "vendor_id": 1,
        "name": "Digital Camera Pro",
        "price": 1482.30,
        "stock": 61,
        "image_url": "get_image_url('digital_camera_pro', is_preview=False)",
        "preview_url": "get_image_url('digital_camera_pro', is_preview=True)",
        "vendor's_commision_coverage": 25
    },
    {
        "vendor_id": 1,
        "name": "Wireless Bluetooth Earbuds",
        "price": 59.99,
        "stock": 150,
        "image_url": "get_image_url('earbuds', is_preview=False)",
        "preview_url": "get_image_url('earbuds', is_preview=True)",
        "vendor's_commision_coverage": 5
    }
]


def add_products(db_session:Session):
    
    for product_data in sample_products:
        vendor = db_session.query(Vendor).filter_by(id=product_data['vendor_id']).first()
        assert vendor !=None 
        assert vendor.plan !=None 

        if db_session.query(Product).filter_by(name=product_data['name']).first():
            print(f"Product already exists {product_data}")
            continue

        commision_from_vendor = product_data.get("vendor's_commision_coverage",0)
        if commision_from_vendor:
            product_data.pop("vendor's_commision_coverage")

        product = Product(**product_data)
        db_session.add(product)
        db_session.flush()

        if commision_from_vendor:
            ChargeRuleManager.create_product_charge_rule(
                        db_session=db_session,
                        product_id=product.id,
                        percentage=commision_from_vendor,
                        payee=Payee('vendor',product_data['vendor_id'])
                        )
    
        ChargeRuleManager.create_product_charge_rule(
            db_session=db_session,
            product_id=product.id,
            percentage=100-commision_from_vendor,
            payee=Payee('product',product.id)

        )
     
    # Commit to database
    db_session.commit()


