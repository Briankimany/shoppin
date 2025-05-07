
# services/payment_processor.py
from app.data_manager import ChargeRecorder, PaymentManager ,OrderManager
from app.routes.logger  import LOG
from app.models.model_utils import PaymentCategory,PaymentMethod
from app.seeds.platform_seeds import get_platform_id

class PaymentProcessorService:
    """Handles all payment processing business logic"""
    
    def __init__(self):
       
        self.logger = LOG.SHOP_LOGGER

    def process_order_charges(self, order_id, session_token, sales_data):
        """Handle all charge calculations and updates"""
        fee_data = ChargeRecorder.record_products_charges(
            order_id=order_id,
            session_tkn=session_token
        )
        
        commission_data = ChargeRecorder.record_products_commision(
            order_id,
            session_tkn=session_token
        )
        
        net_sales = {
            vendor: amount - fee_data.get(vendor, 0) - commission_data.get(vendor, 0)
            for vendor, amount in sales_data.items()
        }
        
        net_sales[get_platform_id()] = sum(fee_data.values()) + sum(commission_data.values())
        
        self.logger.debug(f"Calculated net sales: {net_sales}")
        return net_sales

    def record_vendor_payments(self, order_id, session_token, sales_data):
        """Batch record all vendor payments"""
        payments = [{
            "source": f"order-{order_id}",
            "recipient": f"vendor-{vendor_id}",
            "session_tkn": session_token,
            "amount": amount,
            "method": PaymentMethod.MPESA,
            "category": PaymentCategory.PRODUCT_SALE,
            "description": f"sale from order {order_id} - {float(amount)}"
        } for vendor_id, amount in sales_data.items()]
        
        PaymentManager.record_payments_batch(payments)