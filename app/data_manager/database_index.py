from app.models.vendor import Vendor as VendorModel
from app.models.vendor import VendorPayout as PayoutModel 
from app.models.product import Product as ProductModel
from app.models.order import Order as OrderModel


from sqlalchemy.orm import Session ,sessionmaker

from sqlalchemy import create_engine
from contextlib import contextmanager


from config.config import JSONConfig
config = JSONConfig("config.json")
engine = create_engine(f"sqlite:///{config.database_url.absolute()}")
DbSession = sessionmaker(bind=engine)

@contextmanager
def session_scope(commit=False):
    session = DbSession()
    try:
        yield session
        session.commit() if commit else None
    except Exception:
        session.rollback()
    finally:
        session.close()


class Database:
    def __init__(self, session:Session):
        self.session = session  # Database session object
    
    def get_all_vendors(self):
        return self.session.query(VendorModel).all()
    
 
    def get_vendor(self, vendor_id):
        vendor = self.session.query(VendorModel).where(VendorModel.id == vendor_id).first()
        return vendor
    def add_vendor(self, vendor_data):
        new_vendor = VendorModel(**vendor_data)
        self.session.add(new_vendor)
        self.session.commit()
        return new_vendor.id

    def update_vendor(self, vendor_id, update_data):
        vendor = self.session.query(VendorModel).filter_by(id=vendor_id).first()
        if vendor:
            for key, value in update_data.items():
                if hasattr(vendor , key):
                    setattr(vendor, key, value)
 
            self.session.commit()
            return True
        return False

    def verify_vendor(self, vendor_id):
        return self.update_vendor(vendor_id, {"verified": True})

    def add_product(self, product_data ,charge):
        with session_scope() as db_session:
            new_product = ProductModel(**product_data)
            product_exist = db_session.query(ProductModel).filter(ProductModel == new_product).first()
            if product_exist:
                return product_exist.id
            
            db_session.add(new_product)
            db_session.commit()
            return new_product.id
        
    def modify_product(self , product_id  , product_details:dict):
        with session_scope() as db_session:
            product = db_session.query(ProductModel).where(ProductModel.id == product_id).first()
            if not product:
                return f"No prodict with id {product_id}"
            for k ,v in product_details.items():
                setattr(product , k , v)
            db_session.commit()

        return "Product modified"
    
    def get_vendor_products(self, vendor_id):
        return self.session.query(ProductModel).filter_by(vendor_id=vendor_id).all()

    def get_vendor_orders(self, vendor_id):
        return self.session.query(OrderModel).filter_by(vendor_id=vendor_id).all()

    def add_payout_request(self, vendor_id, amount):
        new_payout = PayoutModel(vendor_id=vendor_id, amount=amount, status="pending")
        self.session.add(new_payout)
        self.session.commit()
        return new_payout.id

    def get_payouts(self, vendor_id):
        return self.session.query(PayoutModel).filter_by(vendor_id=vendor_id).all()
    
    def get_product_by_key_val(self, key, val, occurrence="first"):
        conditions = getattr(ProductModel ,key) == val ,ProductModel.is_active == True
        query = self.session.query(ProductModel).filter(*conditions)
        return query.first() if occurrence == "first" else query.all()

