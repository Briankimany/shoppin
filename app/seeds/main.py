
import app.seeds.seed_users_vendors_products as seed_users_vendors_products
import app.seeds.seed_plans_levels as seed_plans_levels

import os 

if __name__ == "__main__":
    seed_plans_levels.main()
    seed_users_vendors_products.main()