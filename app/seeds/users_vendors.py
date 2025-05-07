from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.models.vendor import Vendor
from app.routes.vendor import sessionmaker , engine
from config.config import JSONConfig
from app.models.clearance import ClearanceLevel
from app.models.vendor_plans import VendorPlan
from app.data_manager.users_manager import UserManager

DbSession = sessionmaker(bind=engine)
conf = JSONConfig("config.json")

def get_image(vendor_key):
    image_map = {
        "vendor1": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743681390/b470ZdEWk3d2kQWT.webp",
        "vendor2": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743517291/samples/outdoor-woman.jpg",
        "vendor3": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743517284/samples/food/spices.jpg",
        "vendor4": "https://res.cloudinary.com/dqmqwijyf/image/upload/c_pad,w_300,h_300/v1743691066/tech_support_zafgsj.webp"
    }
    return image_map[vendor_key]

users_data = {
    "vendor1": {
        "name": "TechMaster",
        "first_name": "Liam",
        "second_name": "Mwangi",
        "email": "tech@example.com",
        "phone": "1234567001",
        "password_hash": "tech_hash_123"
    },
    "vendor2": {
        "name": "FashionGuru",
        "first_name": "Aisha",
        "second_name": "Kariuki",
        "email": "fashion@example.com",
        "phone": "1234567002",
        "password_hash": "fashion_hash_123"
    },
    "vendor3": {
        "name": "HomeKing",
        "first_name": "David",
        "second_name": "Otieno",
        "email": "home@example.com",
        "phone": "1234567003",
        "password_hash": "home_hash_123"
    },
    "vendor4": {
        "name": "ServicePro",
        "first_name": "Grace",
        "second_name": "Njeri",
        "email": "services@example.com",
        "phone": "1234567004",
        "password_hash": "services_hash_123"
    },
    "user1": {
        "name": "Milie",
        "first_name": "Milliam",
        "second_name": "Adjiambo",
        "email": "Miliam@testmyemail.com",
        "phone": "1234567004",
        "password_hash": "millie123455"
    }
    ,
    "user1": {
        "name": "James",
        "first_name": "James",
        "second_name": "Kimani",
        "email": "James@testmyemail.com",
        "phone": "1234567004",
        "password_hash": "james12345"
    }

}

normal_users = {
    "user1": {
        "level":4,
        "name": "Milie",
        "first_name": "Milliam",
        "second_name": "Adjiambo",
        "email": "Miliam@testmyemail.com",
        "phone": "1234567004",
        "password_hash": "millie123455"
    },
    "user1": {
        "name": "James",
        "first_name": "James",
        "second_name": "Kimani",
        "email": "James@testmyemail.com",
        "phone": "1234567004",
        "password_hash": "james12345"
    }
}


vendors_data = {
    "vendor1": {
        "id": 1,
        "store_name": "Tech Haven",
        "store_logo": get_image("vendor1"),
        "payment_type": "pre",
        "store_description": "Gadgets, gaming gear, and cutting-edge tech",
        "verified": True
    },
    "vendor2": {
        "id": 2,
        "store_name": "Urban Threads",
        "store_logo": get_image("vendor2"),
        "payment_type": "post",
        "store_description": "Trendy apparel and accessories",
        "verified": True
    },
    "vendor3": {
        "id": 3,
        "store_name": "Domestic Bliss",
        "store_logo": get_image("vendor3"),
        "payment_type": "pre",
        "store_description": "Everything for your home and kitchen",
        "verified": True
    },
    "vendor4": {
        "id": 4,
        "store_name": "Digital Services Hub",
        "store_logo": get_image("vendor4"),
        "payment_type": "pre",
        "store_description": "IT, AI, and cloud services",
        "verified": True
    }
}


def create_users(db_session: Session, level: ClearanceLevel):
    print("Creating users..")
    for vendor_key, data in users_data.items():
        existing_user = db_session.query(UserProfile).filter_by(email=data['email']).first()
        if existing_user:
            print(f"User with email {data['email']} already exists, skipping.")
            continue

        user = UserProfile(**data)
        db_session.add(user) 
        user.clearance=level
    
    for _,user in normal_users.items():
        existing_user = db_session.query(
            UserProfile
        ).filter(UserProfile.name == user['name']).first()
        if existing_user:
            continue

        level = db_session.query(ClearanceLevel).filter(ClearanceLevel.level==user['level']).first()
        if not level:
            raise Exception(f"Invalid clearance level {user['level']}")
        user.pop('level')
        user =UserProfile(**user)
        db_session.add(user)
        user.clearance= level

    db_session.commit()


def create_vendors(db_session: Session, plan: VendorPlan):
    print('Adding vendors')
    for vendor_key, data in vendors_data.items():
        existing_vendor = db_session.query(Vendor).filter_by(id=data['id']).first()
        if existing_vendor:
            print(f"Vendor with id {data['id']} already exists, skipping.")
            continue

        vendor = Vendor(**data)
        db_session.add(vendor) 
        vendor.plan = plan
    db_session.commit()
