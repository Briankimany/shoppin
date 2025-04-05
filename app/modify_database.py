from sqlalchemy.orm import Session
from models.vendor import Vendor
from models.product import Product
from app.routes.vendor import db_session
from app.data_manager.vendor import VendorObj
from app.models.user_profile import UserProfile


from config.config import JSONConfig
from pathlib import Path
from typing import List
from app.create_database import init_db
import csv

def get_urls_from_csv(csv_path: str) -> list[str]:
    """Read URLs from a single-column CSV and return as list."""
    with open(csv_path, mode='r') as file:
        reader = csv.reader(file)
        return ([row[0] for row in reader if row] )[1:] 

def set_urls(extra_products:List[Product] ,image_urls):
    if image_urls:
        result = []
        for i, product in enumerate(extra_products):
            url_index = int((i / len(extra_products)) * len(image_urls))
            product.image_url = image_urls[url_index]
        
            product.stock = product.vendor_id *10
            result.append(product)
        return result
    return extra_products

    

def add_muliple_prodct(p:list[Product]):
    db_session.add_all(p)
    db_session.commit()



vendor_data = {

    "vendor1": {
        "user": {
            "name": "TechMaster",
            "email": "tech@example.com",
            "phone": "1234567001",
            "password_hash": "tech_hash_123"
        },
        "vendor": {
            "id":1,
            "name": "TechMaster Inc.",
            "email": "tech@example.com",
            "phone": "1234567001",
            "store_name": "Tech Haven",
            "store_logo": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743681390/b470ZdEWk3d2kQWT.webp",
            "payment_type": "Stripe",
            "store_description": "Gadgets, gaming gear, and cutting-edge tech",
            "verified": True
        }
    },

    # Vendor 2 (Fashion)
    "vendor2": {
        "user": {
            "name": "FashionGuru",
            "email": "fashion@example.com",
            "phone": "1234567002",
            "password_hash": "fashion_hash_123"
        },
        "vendor": {
            "id":2,
            "name": "FashionGuru Styles",
            "email": "fashion@example.com",
            "phone": "1234567002",
            "store_name": "Urban Threads",
            "store_logo": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743517291/samples/outdoor-woman.jpg",
            "payment_type": "PayPal",
            "store_description": "Trendy apparel and accessories",
            "verified": True
        }
    },

    # Vendor 3 (Home Goods)
    "vendor3": {
        "user": {
            "name": "HomeKing",
            "email": "home@example.com",
            "phone": "1234567003",
            "password_hash": "home_hash_123"
        },
        "vendor": {
            "id":3,
            "name": "HomeKing Supplies",
            "email": "home@example.com",
            "phone": "1234567003",
            "store_name": "Domestic Bliss",
            "store_logo": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743517284/samples/food/spices.jpg",
            "payment_type": "Bank Transfer",
            "store_description": "Everything for your home and kitchen",
            "verified": True
        }
    },

    # Vendor 4 (Services)
    "vendor4": {
        "user": {
            "name": "ServicePro",
            "email": "services@example.com",
            "phone": "1234567004",
            "password_hash": "services_hash_123"
        },
        "vendor": {
            "id":4,
            "name": "ServicePro Solutions",
            "email": "services@example.com",
            "phone": "1234567004",
            "store_name": "Digital Services Hub",
            "store_logo": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743691066/tech_support_zafgsj.webp",
            "payment_type": "Crypto",
            "store_description": "IT, AI, and cloud services",
            "verified": True
        }
    }
}


def create_users():
    for vendor_key, data in vendor_data.items():
        user = UserProfile(**data["user"])
        db_session.add(user)
    db_session.commit()
def create_vendors():
    for vendor_key, data in vendor_data.items():
        vendor = Vendor(**data["vendor"])
        db_session.add(vendor)
    db_session.commit()


def add_products():
    vendor1 =db_session.query(Vendor).filter(Vendor.id == 1).first()
    vendor2 =db_session.query(Vendor).filter(Vendor.id == 2).first()
    vendor3 =db_session.query(Vendor).filter(Vendor.id == 3).first()
    vendor4 =db_session.query(Vendor).filter(Vendor.id == 4).first()



    extra_products1 = [
    Product(vendor_id=vendor1.id, name="Wireless Mechanical Keyboard", description="RGB backlit wireless mechanical keyboard.", price=129.99, stock=15, category="Electronics", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor1.id, name="Noise Cancelling Headphones", description="Over-ear wireless headphones with active noise cancellation.", price=199.99, stock=12, category="Audio", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor1.id, name="Smartwatch", description="Feature-packed smartwatch with fitness tracking.", price=249.99, stock=10, category="Wearable Tech", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor1.id, name="4K Action Camera", description="Waterproof 4K action camera with stabilization.", price=149.99, stock=8, category="Cameras", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor1.id, name="Wireless Gaming Mouse", description="High-precision gaming mouse with adjustable DPI.", price=79.99, stock=20, category="Gaming", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor1.id, name="Curved Gaming Monitor", description="32-inch curved gaming monitor with 165Hz refresh rate.", price=399.99, stock=6, category="Monitors", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor1.id, name="USB-C Docking Station", description="Multi-port docking station with HDMI and Ethernet.", price=89.99, stock=15, category="Accessories", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor1.id, name="Portable SSD 1TB", description="High-speed portable SSD with USB 3.2.", price=129.99, stock=18, category="Storage", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor1.id, name="Wireless Charging Pad", description="Fast-charging wireless pad for all Qi-compatible devices.", price=49.99, stock=25, category="Accessories", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor1.id, name="Smart Light Bulbs (Pack of 3)", description="Voice-controlled smart bulbs with RGB color.", price=59.99, stock=22, category="Smart Home", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor1.id, name="VR Headset", description="Next-gen VR headset for an immersive experience.", price=349.99, stock=5, category="Gaming", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),

    Product(vendor_id=vendor1.id, name="Dash Cam", description="HD dash cam with night vision and loop recording.", price=119.99, stock=10, category="Automotive", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor1.id, name="Bluetooth Speaker", description="Portable waterproof Bluetooth speaker with deep bass.", price=89.99, stock=15, category="Audio", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor1.id, name="Mini Projector", description="Compact HD projector for home entertainment.", price=199.99, stock=7, category="Home Theater", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor1.id, name="Gaming Chair", description="Ergonomic gaming chair with lumbar support.", price=249.99, stock=9, category="Furniture", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    ]

    extra_products2 = [
    Product(vendor_id=vendor2.id, name="Leather Jacket", description="Genuine leather jacket for a stylish look.", price=199.99, stock=10, category="Men's Fashion", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor2.id, name="Casual Sneakers", description="Comfortable and stylish sneakers for everyday wear.", price=89.99, stock=15, category="Footwear", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor2.id, name="Designer Handbag", description="Luxury handbag with premium materials.", price=249.99, stock=8, category="Women's Fashion", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor2.id, name="Sports T-Shirt", description="Breathable sports T-shirt for workouts.", price=39.99, stock=25, category="Activewear", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor2.id, name="Luxury Watch", description="Elegant wristwatch with a stainless steel finish.", price=499.99, stock=5, category="Accessories", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor2.id, name="Slim Fit Jeans", description="Trendy slim-fit jeans for a modern look.", price=59.99, stock=18, category="Men's Fashion", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor2.id, name="Formal Dress", description="Elegant evening dress for special occasions.", price=179.99, stock=12, category="Women's Fashion", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor2.id, name="Winter Coat", description="Warm and stylish winter coat for cold weather.", price=199.99, stock=10, category="Outerwear", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor2.id, name="Running Shoes", description="Lightweight running shoes with cushioned soles.", price=129.99, stock=20, category="Footwear", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor2.id, name="Beanie Hat", description="Soft knit beanie for winter.", price=29.99, stock=30, category="Accessories", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    ]

    extra_products3 = [
    Product(vendor_id=vendor3.id, name="Dish Drying Rack", description="Compact stainless steel rack for drying dishes efficiently.", price=34.99, stock=20, category="Kitchen", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Electric Rice Cooker", description="Automatic rice cooker with keep-warm function.", price=79.99, stock=15, category="Kitchen Appliances", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Blender", description="High-power blender for smoothies and soups.", price=59.99, stock=25, category="Kitchen Appliances", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Pressure Cooker", description="Fast-cooking pressure cooker with multiple safety features.", price=99.99, stock=10, category="Kitchen Appliances", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Microwave Oven", description="Compact microwave with adjustable heating settings.", price=199.99, stock=12, category="Kitchen Appliances", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor3.id, name="Robo Vacuum Cleaner", description="Smart robotic vacuum with app control.", price=299.99, stock=8, category="Home Appliances", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Portable Heater", description="Energy-efficient portable heater for cold days.", price=79.99, stock=14, category="Home Appliances", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Smart Thermostat", description="WiFi-enabled thermostat for optimal temperature control.", price=149.99, stock=7, category="Home Automation", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor3.id, name="Bathroom Mirror Cabinet", description="Wall-mounted mirror with built-in storage.", price=119.99, stock=10, category="Bathroom", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Shower Filter", description="Removes chlorine and impurities for a better shower experience.", price=49.99, stock=15, category="Bathroom", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor3.id, name="Smart Door Lock", description="Fingerprint and keypad entry for high security.", price=179.99, stock=10, category="Home Security", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Surveillance Camera", description="Indoor/outdoor security camera with night vision.", price=129.99, stock=12, category="Home Security", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor3.id, name="Laundry Basket", description="Foldable laundry basket with waterproof lining.", price=29.99, stock=30, category="Home Organization", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Storage Bins Set", description="Set of stackable storage bins for organization.", price=49.99, stock=20, category="Home Organization", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor3.id, name="Silk Pillowcases", description="Luxury silk pillowcases for better sleep and hair care.", price=59.99, stock=25, category="Bedding", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Memory Foam Mattress Topper", description="Extra comfort memory foam mattress topper.", price=199.99, stock=10, category="Bedding", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor3.id, name="Curtain Set", description="Elegant blackout curtain set for better sleep.", price=79.99, stock=15, category="Home Decor", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Artificial Plant Set", description="Low-maintenance artificial plants for decor.", price=39.99, stock=25, category="Home Decor", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor3.id, name="Towel Warmer", description="Heated towel rack for warm towels after showers.", price=149.99, stock=8, category="Bathroom", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor3.id, name="Bathrobe", description="Soft and absorbent bathrobe for comfort.", price=69.99, stock=12, category="Bathroom", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg")
    ]

    extra_products4 = [
    Product(vendor_id=vendor4.id, name="Software Installation & Setup", description="We install and configure any software on Windows, macOS, or Linux.", price=29.99, stock=999, category="Software Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor4.id, name="AI Model Training & Fine-Tuning", description="Train and fine-tune AI models for various applications.", price=199.99, stock=999, category="AI Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor4.id, name="MATLAB Project Development", description="Assistance with MATLAB simulations, algorithms, and analysis.", price=149.99, stock=999, category="Engineering Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor4.id, name="Python Script Development", description="Custom Python scripts for automation, data analysis, and more.", price=79.99, stock=999, category="Programming Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor4.id, name="Website Development & Deployment", description="Full-stack web development and deployment services.", price=299.99, stock=999, category="Web Development", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor4.id, name="Cybersecurity Consultation", description="Security audits and penetration testing for websites and systems.", price=249.99, stock=999, category="Security Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor4.id, name="Arduino & IoT Project Assistance", description="Guidance on Arduino, Raspberry Pi, and IoT projects.", price=119.99, stock=999, category="Hardware Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor4.id, name="Cloud Computing & Server Setup", description="AWS, Azure, and Google Cloud setup and management.", price=349.99, stock=999, category="Cloud Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor4.id, name="Database Design & Optimization", description="Design and optimize SQL & NoSQL databases.", price=179.99, stock=999, category="Database Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor4.id, name="Networking Setup & Troubleshooting", description="Set up routers, VPNs, and troubleshoot network issues.", price=99.99, stock=999, category="Networking Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor4.id, name="AI Chatbot Development", description="Create AI-powered chatbots for customer support and automation.", price=299.99, stock=999, category="AI Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    
    Product(vendor_id=vendor4.id, name="Machine Learning Model Deployment", description="Deploy ML models using Flask, FastAPI, or cloud services.", price=399.99, stock=999, category="AI Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor4.id, name="Tech Support & Troubleshooting", description="Remote support for troubleshooting software and hardware issues.", price=49.99, stock=999, category="IT Support", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),

    Product(vendor_id=vendor4.id, name="Embedded Systems Development", description="Develop firmware and software for embedded systems.", price=259.99, stock=999, category="Engineering Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    Product(vendor_id=vendor4.id, name="Custom API Development", description="Develop RESTful and GraphQL APIs for your applications.", price=199.99, stock=999, category="Programming Services", image_url="https://img401.picturelol.com/th/67769/9rxu5xjquw3l.jpg"),
    ]

    image_urls = get_urls_from_csv("studio_urls_c_pad,w_300,h_300.csv")

    add_muliple_prodct(p=set_urls(extra_products1 , image_urls))
    add_muliple_prodct(p=set_urls(extra_products2 , image_urls))
    add_muliple_prodct(p=set_urls(extra_products3 , image_urls))
    add_muliple_prodct(p=set_urls(extra_products4 , image_urls))

def main():
    try:
        create_users()
        create_vendors()
    except Exception as e:
        if  Path(conf.database_url).exists():
            db_path = Path(JSONConfig('config.json').database_url)
            db_path.rename(db_path.with_name(f"{db_path.stem}_BACKUP.DB"))
            init_db()
            print("encoutered error resetting all tables")
        return
    add_products()


if __name__ == "__main__":
    conf = JSONConfig("config.json")
    if not Path(conf.database_url).exists():
        init_db()
    else:
        print('using existing db')
    
    main()

    


