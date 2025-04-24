
from app.models.vendor_plans import VendorPlan, PlanFeature
from app.data_manager.client_access_manager import session_scope  ,LOG
from sqlalchemy import exists

from app.models.clearance import ClearanceLevel


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
            "commission_percent": 15.0,
            "flat_fee": 120,
            "min_price_threshold": 800,
            "payout_frequency": "monthly",
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
            "commission_percent": 12.0,
            "flat_fee": 110,
            "min_price_threshold": 800,
            "payout_frequency": "bi-weekly",
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
            "commission_percent": 10.0,
            "flat_fee": 0,  # Assuming none
            "min_price_threshold": 0,
            "payout_frequency": "weekly",
            "marketing_grace_period": True,
            "description": "For large-scale, structured vendors requiring maximum flexibility.",
            "features": [
                "Minimum 10 product categories",
                "Each subcategory must contain at least 10 products",
                "Weekly payouts (daily available after 3-day cycle)",
                "Premium analytics tools",
                "Custom support and marketing partnerships"
            ]
        }
    ]

    with session_scope(commit=True,logger=LOG.MAIN_LOGGER ,func=seed_vendor_plans,raise_exception=True) as session:
        for plan_data in plans_data:
            print("Seeding plans")
            exists_query = session.query(
                exists().where(VendorPlan.name == plan_data["name"])
            ).scalar()
            if exists_query:
                continue

            plan = VendorPlan(
                name=plan_data["name"],
                commission_percent=plan_data["commission_percent"],
                flat_fee=plan_data["flat_fee"],
                min_price_threshold=plan_data["min_price_threshold"],
                payout_frequency=plan_data["payout_frequency"],
                marketing_grace_period=plan_data["marketing_grace_period"],
                description=plan_data["description"]
            )
            plan.features = [
                PlanFeature(feature_text=f) for f in plan_data["features"]
            ]
            session.add(plan)

if __name__ == "__main__":
    seed_clearance_levels()
    seed_vendor_plans()