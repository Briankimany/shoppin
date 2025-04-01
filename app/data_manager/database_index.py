from app.models.vendor import Vendor as VendorModel
from app.models.vendor import VendorPayout as PayoutModel
from app.models.product import Product as ProductModel
from app.models.order import Order as OrderModel
from sqlalchemy.orm import Session

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

    def add_product(self, product_data):
        new_product = ProductModel(**product_data)
        self.session.add(new_product)
        self.session.commit()
        return new_product.id
    def modify_product(self , product_id  , product_details:dict):
        product = self.session.query(ProductModel).where(ProductModel.id == product_id).first()
        if not product:
            return f"No prodict with id {product_id}"
        for k ,v in product_details.items():

            setattr(product , k , v)
        self.session.commit()

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
        query = self.session.query(ProductModel).where(getattr(ProductModel, key) == val)
        return query.first() if occurrence == "first" else query.all()

