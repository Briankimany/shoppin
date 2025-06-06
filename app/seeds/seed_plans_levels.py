
from app.models.vendor_plans import VendorPlan, PlanFeature
from app.data_manager.client_access_manager import session_scope
from app.routes.logger import LOG 
from sqlalchemy import exists
from app.models.model_utils import PayoutFrequency
from app.models.clearance import ClearanceLevel
import app.seeds.platform_seeds as platform_seeds

def seed_clearance_levels():
    levels = {
        1: "Admin",
        2: "Maintainer",  # Vendor/Customer Support
        3: "Vendor",      # Selling products
        4: "Client"       # Regular user
    }
    
    with session_scope(commit=True,logger=LOG.MAIN_LOGGER ,func=seed_vendor_plans,raise_exception=True) as session:
        print('Seeding levels..')
        for id_, name in levels.items():
            exists = session.query(ClearanceLevel).filter_by(id=id_).first()
            if not exists:
                level = ClearanceLevel()
                level.name = name 
                level.level = id_
                session.add(level)


def seed_vendor_plans():
    plans_data = [
        {
            "name": "Standard",
            "product_commission_percent": 15.0,
            "products_flat_fee": 120,
            "products_min_price_threshold": 800,
            "payout_frequency": PayoutFrequency.MONTHLY,
         
            "min_payout_threshold": 350,  
   
            "marketing_grace_period": False,
            "description": "Starter plan for individual or casual sellers.",
            "features": [
                "No minimum product count required",
                "Basic analytics dashboard",
                "Standard customer support",
                "Monthly payouts (bi-weekly optional with extra fee)",
                "No platform marketing after grace period"
            ]
        },
        {
            "name": "Professional",
            "product_commission_percent": 12.0,
            "products_flat_fee": 110,
            "products_min_price_threshold": 800,
            "payout_frequency": PayoutFrequency.BI_WEEKLY,
       
            "min_payout_threshold": 400,
  
            "marketing_grace_period": True,
            "description": "Ideal for vendors with structured product categories and moderate scale.",
            "features": [
                "Minimum 5 product categories with 3+ subcategories each",
                "Each subcategory must contain at least 3 products",
                "Standard analytics access",
                "Bi-weekly or weekly payouts (fees apply)",
                "Dedicated customer support"
            ]
        },
        {
            "name": "Enterprise",
            "product_commission_percent": 10.0,
            "products_flat_fee": 0,
            "products_min_price_threshold": 0,
            "payout_frequency": PayoutFrequency.WEEKLY,
            "min_payout_threshold": 300, 
            "marketing_grace_period": True,
            "description": "For large-scale, structured vendors requiring maximum flexibility.",
            "features": [
                "Minimum 10 product categories",
                "Each subcategory must contain at least 10 products",
                "Weekly payouts (daily available after 3-day cycle)",
                "Premium analytics tools",
                "Custom support and marketing partnerships"
            ]
        }]
    plans_data[0]["unscheduled_withdrawal_percentage"] = 3.0
    plans_data[0]["unscheduled_withdrawal_flat_fee"] = 17
    plans_data[0]["max_unscheduled_withdrawal_fee"] = 175

    plans_data[0]["scheduled_withdrawal_percentage"] = 2.0
    plans_data[0]["scheduled_withdrawal_flat_fee"] = 10
    plans_data[0]["max_scheduled_withdrawal_fee"] = 150

    plans_data[1]["unscheduled_withdrawal_percentage"] = 4.0
    plans_data[1]["unscheduled_withdrawal_flat_fee"] = 17
    plans_data[1]["max_unscheduled_withdrawal_fee"] = 175

    plans_data[1]["scheduled_withdrawal_percentage"] = 3.5
    plans_data[1]["scheduled_withdrawal_flat_fee"] = 10
    plans_data[1]["max_scheduled_withdrawal_fee"] = 150

    plans_data[2]["unscheduled_withdrawal_percentage"] = 5
    plans_data[2]["unscheduled_withdrawal_flat_fee"] = 17
    plans_data[2]["max_unscheduled_withdrawal_fee"] = 175

    plans_data[2]["scheduled_withdrawal_percentage"] = 5
    plans_data[2]["scheduled_withdrawal_flat_fee"] = 10
    plans_data[2]["max_scheduled_withdrawal_fee"] = 150

    with session_scope(commit=True,
                       logger=LOG.MAIN_LOGGER ,
                       func=seed_vendor_plans
                       ,raise_exception=True) as session:
        
        for plan_data in plans_data:
            print("Seeding plans")
            exists_query = session.query(
                exists().where(VendorPlan.name == plan_data["name"])
            ).scalar()
            if exists_query:
                continue
            features = [
                PlanFeature(feature_text=f) for f in plan_data["features"]
            ]
            plan_data.pop('features')
      
            plan = VendorPlan(**plan_data)
            plan.features = features
            session.add(plan)

def main():
    seed_clearance_levels()
    seed_vendor_plans()
    platform_seeds.main()
    
if __name__ == "__main__":
    main()
