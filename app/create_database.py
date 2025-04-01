from sqlalchemy import create_engine ,inspect
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from config.config import JSONConfig
from sqlalchemy import text

from app.models.session_tracking import SessionTracking
from app.models.user_profile import UserProfile
from app.models.vendor import Vendor , VendorPayout
from app.models.product import Product 
from app.models.order import Order 
from app.models.cart import Cart , CartItem
from app.models.order_item import OrderItem

config = JSONConfig("config.json")

DATABASE_URL = f"sqlite:///{config.database_url.absolute()}"
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine)

def reset_table(table_name: str):
    """Drops the specified table and recreates the database schema."""
    with SessionLocal() as session:
        try:
            # Drop the table
            session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            session.commit()
            print(f"Table '{table_name}' dropped successfully.")

            # Recreate all tables (ensures dependencies are handled)
            Base.metadata.create_all(engine)
            print("Database schema recreated.")

        except Exception as e:
            session.rollback()
            print(f"Error resetting table {table_name}: {e}")

def init_db():

 
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    inspector = inspect(engine)
    key = 0
    tables = inspector.get_table_names()
    d = {}
    for i in tables:
        d[key] = i
        key+=1
    
    while True:
        [print(k , v) for k , v in d.items()]
        key = int(input("enter key: "))

        if key == -1:
            break
        if key == -2:
            print("initializing db....")
            init_db()
        table = d.get(key , None)
        print("Reseting table ",table)
        if table:
            reset_table(table_name=table)
            init_db()
    

