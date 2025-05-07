
from flask.views import MethodView
from app.services.payment_processor import PaymentProcessorService
from app.data_manager import OrderManager, SessionManager ,VendorTransactionSystem ,PaymentProcessor
from app.routes.logger import bp_error_logger
from app.routes.routes_utils import session_set
from app.routes.logger import LOG
from flask.views import MethodView
from flask import request ,session ,jsonify


class PaymentAPI(MethodView):
    """Handles payment processing endpoint with status checking"""
    
    decorators = [bp_error_logger(LOG.ORDER_LOGGER, 500), session_set]
    
    def __init__(self):
        self.processor = PaymentProcessorService()
        self.session_manager = SessionManager(db_session=None)
        self.logger = LOG.ORDER_LOGGER

    def get(self):
        """Check and update payment status"""
        
        status = self._check_order_status()
        
        if status == 'pending':
            order = self._get_current_order()
            self._process_pending_order(
                order ,
                request.args.get('num',1))

        if status == 'paid':
            return jsonify({
                "message": "success",
                "data": "Payment complete"
            }), 200
            
        return jsonify({
            "message": "success",
            "status": status
        }), 200
        
     
    def _get_current_order(self):
        """Retrieve order associated with current session"""
        return  OrderManager.get_order_by_session_tkn(
            session_tkn=session['session_token'],
            statuses=['pending','paid']
        )

    def _process_pending_order(self, order ,max_retries:int=7):
        """Handle pending payment status"""
        self.logger.debug(f"Late status check for order {order}")

        if not order.tracking_id:
            return 
        
        status=PaymentProcessor.check_status(
            invoice_id=order.tracking_id,
            max_retries=max_retries
        )
        self.logger.debug("Updating pending order")
        self.logger.debug(f"Order={order} ,status={status}")
        OrderManager.update_order(order.id,status=status)

        if status == 'paid':
            self._fulfill_order(order, order.cart_id)

    def _check_order_status(self):
        """Check order status from database"""
        order = self._get_current_order()
        return order.status if order else None


    def post(self):
            
            data = request.get_json()
            phone = self._normalize_phone(data.get('phone'))
            amount = data.get('amount')
            
            if not all([phone, amount]):
                raise ValueError("Missing phone or amount")

            cart_id = self.session_manager.get_cart(session["session_token"])
            items = self._prepare_cart_items(cart_id)
            order = self._create_order(phone, amount, cart_id, items)

            
            status = PaymentProcessor.collect_payment(
                phone=phone,
                amount=amount,
                orderid=order.order.id
            )
            
            if not status:
                return jsonify({"message": "warning", "data": "Payment failed"}), 200
            
            order.update_order(order.order.id, status=status)
            
            if status == 'paid':
                self._fulfill_order(order.order, cart_id)
                return jsonify({"message": "success" ,'data':"Payment inititated"}) , 200
            elif status == 'pending':
                return jsonify({"message": "warning" ,'data':"Payment inititated waiting for user input"}) , 200
            
            return jsonify({"message":"error", "data":f"Could not initiate payment"}) , 200
                

    def _normalize_phone(self, phone):
        """Normalize phone number format"""
        return phone.replace("0", "254", 1) if phone.startswith("0") else phone

    def _prepare_cart_items(self, cart_id):
        """Prepare cart items for order creation"""
        return [{
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price_at_purchase": item.product.final_price
        } for item in self.session_manager.get_cartitems(cart_id)]

    def _create_order(self, phone, amount, cart_id, items):
        """Create new order from cart"""
        return OrderManager.create_new_order(
            session_tkn=session["session_token"],
            phone_number=phone,
            total_amount=amount,
            cart_id=cart_id,
            items=items
        )
    def _check_order_status(self):
        order = OrderManager.get_order_by_session_tkn(
            session_tkn=session['session_token']
            )
        status = order.status if order else None 
        return status 
    
    def _fulfill_order(self, order, cart_id:int):
        """Complete all post-payment fulfillment"""
        self.session_manager.update_cart(cart_id, "is_active", False)
        OrderManager.update_stock_after_order(order.id)
        
        _, sales_data = VendorTransactionSystem.divide_order_to_vendors(order.id)
        self.processor.record_vendor_payments(order.id, session["session_token"], sales_data)
        
        net_sales = self.processor.process_order_charges(
            order.id,
            session["session_token"],
            sales_data
        )
        
        VendorTransactionSystem.update_vendors_accounts(net_sales)