"""_summary_
This module contains the functions used to seed the database for testing.
It should used to create the platforms account which is required.
"""

from app.seeds.main import seed_plans_levels ,seed_users_vendors_products


__all__ = [
    "seed_plans_levels",
    "seed_users_vendors_products"
]