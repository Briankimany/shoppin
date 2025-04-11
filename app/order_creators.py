
from collections import defaultdict


import random
from decimal import Decimal

import pickle
import os
from pathlib import Path
from collections import defaultdict


import sys
import os
from pathlib import Path
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()


from app.data_manager.session_manager import SessionManager
from app.data_manager.cart_manager import OrderManager
from app.routes.vendor import db_session
from app.models.product import Product as ProductModel

session_manager = SessionManager(db_session)

current_dir = Path(os.getcwd())

class RevenueDataHandler:
    def __init__(self, file_path=current_dir /"vendor_revenue.pkl"):
        self.file_path = Path(file_path).expanduser()
        self.data = defaultdict(list)
        self._load_existing()

    def _load_existing(self):
        """Load existing data if file exists"""
        if self.file_path.exists():
            with open(self.file_path, 'rb') as f:
                existing = pickle.load(f)
                for vendor_id, orders in existing.items():
                    self.data[vendor_id].extend(orders)

    def add_new_results(self, new_results):
        """Merge new simulation results"""
        for vendor_id, orders in new_results.items():
            self.data[vendor_id].extend(orders)

    def save(self):
        """Save merged data back to file"""
        with open(self.file_path, 'wb') as f:
            pickle.dump(dict(self.data), f)

    def get_all_data(self):
        """Returns consolidated data"""
        return dict(self.data)

def get_quantity(product_id):
    return 2  

class MultiUserSimulator:
    def __init__(self, db_session, session_manager:SessionManager, order_manager:OrderManager):
        self.db = db_session
        self.sm = session_manager  
        self.om = order_manager  
        self.vendor_revenue = defaultdict(list)
        self.data_handler = RevenueDataHandler(current_dir /"vendor_revenue.pkl")
        self.all_data = self.data_handler.get_all_data() 
        self.all_vendors = {}
        self.summarize_all_data()

    def summarize_all_data(self):
        all_d = {}
        all_data = self.all_data
        for vendor ,order in all_data.items():
            vendor_data = {"rev":[],
                          'sold_products':{}}
            for record in order:
                vendor_data['rev'].append(record['amount'])
                
                prod_id = record['product_id']
                prod_quant = record['quantity']
                
                if prod_id not in vendor_data['sold_products']:
                    vendor_data['sold_products'][prod_id] =0
                vendor_data['sold_products'][prod_id] += prod_quant
               
            vendor_data['rev'] = sum(vendor_data['rev'])
            all_d[vendor]=vendor_data
           
        self.all_vendors = all_d
        return self.all_vendors
        
    def run_simulation(self, products, quantity_fn , num_products = 3):
        """
        Simulates product selection and quantity assignment for an order.

        Args:
            products (List[ProductModel]): List of product instances, each with .id and .vendor_id attributes.
            quantity_fn (Callable[[int], int]): Function that takes a product ID and returns a quantity.

        Environment Variables:
            SIMULATED_ORDER_STATUS: Must be one of ['pending', 'paid', 'canceled'].
            PRODUCTS_RANDOM_SEED: Integer seed value for reproducible random selection.
        """

        # 1. Create 3 users
        sessions = [self.sm.create_new_session() for _ in range(3)]
        seed =os.getenv("PRODUCTS_RANDOM_SEED")
        if seed:
            random.seed(seed)
     
        for i, session_token in enumerate(sessions):
            # 2. Each user buys 3 random products
            selected = random.sample(products, num_products)
            print("\nuser {} is buyin items".format(session_token))
            [pprint(i) for i in selected]
            print("\n")
            for product in selected:
                self.sm.add_to_cart(
                    session_token=session_token,
                    product_id=product.id,
                    quantity=quantity_fn(product.id)
                )
            
            # 3. Checkout 
            cart_id = self.sm.get_cart(session_token)
            cart_items = self.sm.get_cartitems(cart_id)
            
            items = [{
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price_at_purchase": item.product.price
            } for item in cart_items]
            
            # Calculate total 
            total = sum(
                Decimal(item["price_at_purchase"]) * item["quantity"] 
                for item in items
            )
            
            #4. Create order (your existing method)
            order = self.om.create_new_order(
                db_session=self.db,
                session_tkn=session_token,
                phone_number=f"07123{i}4567",  # Fake unique phone
                total_amount=total,
                cart_id=cart_id,
                items=items
            )

             #5. update the cart status
            status =os.getenv("SIMULATED_ORDER_STATUS" ,'paid')
            order.update_order(order.order.id , status =status)
            if status == 'paid':
                session_manager.update_cart(cart_id=cart_id , attribute="is_active" , new_value=False)
                order.divide_to_vendors(order_id=order.order.id)
                order.update_stock(order_id = order.order.id)

            # 6. Group by vendor
            for item in items:
                product = next(p for p in products if p.id == item["product_id"])
                self.vendor_revenue[product.vendor_id].append({
                    "order_id": order.order.id,
                    "amount": Decimal(item["price_at_purchase"]) * item["quantity"],
                    "product_id": product.id,
                    "quantity": item["quantity"],
                    "status":status
                })

        # merge data
        self.data_handler.add_new_results(dict(self.vendor_revenue))

        # 7. Save merged data
        self.data_handler.save()
        
        # 8. Access full history
        self.all_data = self.data_handler.get_all_data() 

        #9 update and compact vendor data
        self.summarize_all_data()

    @staticmethod
    def run(db_session , session_manager ,create_records = False):
        """Returns: {vendor_id: [order_details]}"""
        sim = MultiUserSimulator(db_session, session_manager, OrderManager)
        if create_records:
            sim.run_simulation(
                products=db_session.query(ProductModel).all(),
                quantity_fn=get_quantity
            )
        return  sim
    

def main(create_records):
    sim =MultiUserSimulator.run(db_session=db_session,session_manager=session_manager ,
                                create_records=create_records)
    return sim

if __name__ == "__main__":
    main(True)