
from datetime import datetime, timedelta
from sqlalchemy import func ,case
from sqlalchemy.orm import Session
from app.models.product import Product as ProductModel
from app.models.order import Order as OrderModel
from app.models.order_item import OrderItem , VendorOrder
from app.models.user_profile import UserBalance
import humanize


class VendorTransactionSystem:
    """Handles vendor transactions and dashboard reporting"""
    
    # ======================
    # Dashboard Methods
    # ======================
    
    @staticmethod
    def get_product_stats(vendor_id: int, db_session: Session, threshold: int = 10) -> dict:
        """Get inventory statistics with FIXED case-when syntax"""
        total, out_of_stock = db_session.query(
            func.count(ProductModel.id),
            func.sum(
                case(
                    (ProductModel.stock == 0, 1),  # When stock=0, count as 1
                    else_=0                         # Else count as 0
                )
            )
        ).filter(ProductModel.vendor_id == vendor_id).first()
        
        return {
            "total_products": total or 0,
            "out_of_stock": out_of_stock or 0,
            "active_products": (total or 0) - (out_of_stock or 0)
        }

    @staticmethod
    def get_revenue_stats(vendor_id: int, db_session: Session, days: int = 7) -> dict:
        """Get revenue data including daily breakdown"""
        date_range = [(datetime.now() - timedelta(days=i)).date() for i in range(days)]
        
        revenue_results = db_session.query(
            func.date(OrderModel.created_at).label('date'),
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity).label('amount')
        ).join(VendorOrder, VendorOrder.orderid == OrderModel.id
        ).join(OrderItem, VendorOrder.orderitem == OrderItem.id
        ).filter(
            VendorOrder.vendorid == vendor_id,
            OrderModel.created_at >= min(date_range)
        ).group_by(func.date(OrderModel.created_at)).all()
     
        revenue_by_date = {r.date: float(r.amount) for r in revenue_results}
        
        return {
            "dates": [d.strftime('%m-%d') for d in date_range],
            "amounts": [revenue_by_date.get(d, 0.0) for d in date_range],
            "total": sum(revenue_by_date.values()),
            "today": revenue_by_date.get(datetime.now().date(), 0.0)
        }

    @staticmethod
    def get_recent_orders(vendor_id: int, db_session: Session, limit: int = 3) -> list:
        """Get recent orders with simplified query"""
        return db_session.query(
            OrderModel,
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity).label('total')
        ).join(VendorOrder, VendorOrder.orderid == OrderModel.id
        ).join(OrderItem, VendorOrder.orderitem == OrderItem.id
        ).filter(VendorOrder.vendorid == vendor_id
        ).group_by(OrderModel.id
        ).order_by(OrderModel.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_low_stock_items(vendor_id: int, db_session: Session, threshold: int = 10) -> list:
        """Get products below stock threshold"""
        return db_session.query(ProductModel).filter(
            ProductModel.vendor_id == vendor_id,
            ProductModel.stock < threshold
        ).order_by(ProductModel.stock.asc()).all()

    @classmethod
    def get_vendor_dashboard(cls, vendor_id: int, db_session: Session) -> dict:
        """Assemble complete dashboard data"""
        dashboard = {}
        
        # 1. Product statistics
        dashboard.update(cls.get_product_stats(vendor_id, db_session))
        
        # 2. Revenue data
        revenue = cls.get_revenue_stats(vendor_id, db_session)
        dashboard.update({
            'total_revenue': revenue['total'],
            'daily_revenue': {
                'dates': revenue['dates'],
                'amounts': revenue['amounts']
            },
            'today_revenue': revenue['today']
        })
        
        # 3. Recent orders
        dashboard['recent_orders'] = [{
            'id': f"ORD-{order.id}",
            'total': float(total),
            'status': order.status,
            'time_ago': humanize.naturaltime(datetime.now() - order.created_at),
            'customer': order.session
        } for order, total in cls.get_recent_orders(vendor_id, db_session)]
        
        # 4. Low stock items
        dashboard['low_stock_items'] = [{
            'id': p.id,
            'name': p.name,
            'stock': p.stock,
            'threshold': 10
        } for p in cls.get_low_stock_items(vendor_id, db_session)]
        
        return dashboard

    # ======================
    # Balance Tracking Methods
    # ======================
    
    @staticmethod
    def update_vendor_balance(vendor_id: int, amount: float, db_session: Session):
        """Update vendor balance when orders are processed"""
            
        
        # Get or create balance record
        balance = db_session.query(UserBalance).get(vendor_id)
        if not balance:
            balance = UserBalance(id=vendor_id, balance=0)
            db_session.add(balance)
        
        balance.balance += amount
        db_session.commit()

    @classmethod
    def process_order_payment(cls, order_id: int, db_session: Session):
        """Distribute payment to vendors for an order"""
        # Get all vendor shares for this order
        vendor_shares = db_session.query(
            VendorOrder.vendorid,
            func.sum(OrderItem.price_at_purchase * OrderItem.quantity).label('amount')
        ).join(OrderItem, VendorOrder.orderitem == OrderItem.id
        ).filter(VendorOrder.orderid == order_id
        ).group_by(VendorOrder.vendorid).all()
        
        # Update each vendor's balance
        for vendor_id, amount in vendor_shares:
            cls.update_vendor_balance(vendor_id, float(amount), db_session)
            
        return len(vendor_shares)  # Return count of vendors paid
    

if __name__ == "__main__":
    from app.routes.vendor import db_session
    from pprint import pprint
    d = VendorTransactionSystem.get_vendor_dashboard(4 , db_session)
    pprint(d)