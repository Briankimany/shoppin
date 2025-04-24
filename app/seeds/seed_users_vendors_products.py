
from app.routes.vendor import sessionmaker , engine

from config.config import JSONConfig
from pathlib import Path
from app.create_database import init_db

from app.seeds.products import add_products 
from app.seeds.users_vendors import create_users ,create_vendors ,ClearanceLevel

DbSession = sessionmaker(bind=engine)
conf = JSONConfig("config.json")



def main():
    with DbSession() as db_session:
        print("[*] Sedding database ..")
        try:
            level = db_session.query(ClearanceLevel).filter(
                ClearanceLevel.level == 3
            ).first()
            assert level !=None
            create_users(db_session ,level)
        except ValueError as e:
            print(f"Error creating users: {e}")
            db_session.rollback()
            return
        try:
            create_vendors(db_session)
        except Exception as e:  
            print(f"Error creating vendors: {e}")
            db_session.rollback()
            return
        
        try:
            add_products(db_session)
            print("Done adding products")
        except Exception as e:
            db_session.rollback()
            print(f"Error adding products: {e}")


if __name__ == "__main__":
   
    if not Path(conf.database_url).exists():
       print("No db found")
       init_db()
       print("Done creating db")
    else:
        print('using existing db')
    main()
