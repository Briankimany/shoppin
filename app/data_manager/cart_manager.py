
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_item import OrderItem , VendorOrder
from app.models.product import Product


from config.config import JSONConfig
from .session_manager import SessionManager
from .vendor_transaction import VendorTransactionSystem
import json , requests ,time
from app.routes.logger import LOG
from time import perf_counter
from typing import List 

from .scoped_session import session_scope ,Session as QuerySession


class OrderManager:
    db_session = QuerySession()

    def __init__(self, db_session: Session, order_id):
        """
        Initializes an `OrderManager` instance with an order.

        Args:
            db_session (Session): The active SQLAlchemy database session.
            order_id : The ID of the order to be managed or an instance of Order

        Attributes:
            db_session (Session): The SQLAlchemy session for database operations.
            order (Order o): The order object if found
        """
        
        self.order = self.db_session.query(Order).where(Order.id == order_id).first() if not isinstance(order_id , Order) else order_id
        self.config = JSONConfig(json_path="config.json")

    @classmethod
    def get_order_by_session_tkn(cls , session_tkn:str,statuses:List[str] = ['pending']):
    
        return cls.db_session.query(Order).filter(
            Order.session == session_tkn,
            Order.status.in_(statuses)
            ).first()
    @classmethod
    def get_order_by(cls,all_orders,**kwargs):

        conditions = [(getattr(Order,key)==value) for key ,value in kwargs.items()]
        query= cls.db_session.query(Order).filter(*conditions)
        if all_orders:
            return query.all()
        return query.first()

    @staticmethod
    def group_orders_to_vendors(db_session:Session , orderid:int ,return_data_only = False):
        sorted_orders = (
            db_session.query(OrderItem.id ,Product.vendor_id)
            .join(Product, OrderItem.product_id == Product.id)
            .filter(OrderItem.order_id == orderid)
            .order_by(Product.vendor_id) 
            .all()
        )
        grouped = {}
        for orderitem , vendorid in sorted_orders:
            if vendorid not in grouped:
                grouped[vendorid]=[]
            grouped[vendorid].append(orderitem)
        
        if return_data_only:
            return grouped
        
        LOG.ORDER_LOGGER.info("Initiating creation of vendor orders")
        LOG.ORDER_LOGGER.info(f"Data = {grouped}")

        vendororders = []
        for vendor_id, orderitems in grouped.items():
            for orderitem in orderitems:
                exists = db_session.query(VendorOrder).filter_by(
                    vendorid=vendor_id, orderid=orderid, orderitem=orderitem
                ).first()

                if not exists:
                    vendororders.append(
                        VendorOrder(vendorid=vendor_id, orderid=orderid, orderitem=orderitem)
                    )

        if vendororders:
            db_session.add_all(vendororders)
            db_session.commit()
            LOG.ORDER_LOGGER.info(f"Added {len(vendororders)} new vendor orders.")
        else:
            LOG.ORDER_LOGGER.info("No new vendor orders were added.")

    @classmethod
    def create_new_order(cls, session_tkn, phone_number=None, 
                         total_amount=None,cart_id=None, items=[], user_id=None) :
        """
        Creates a new order if none exists for the given session token and inserts associated order items.

        If no order is found for the given session token, a new order is created in the `Order` table.
        The method then inserts multiple related order items into the `OrderItem` table.

        Args:
            db_session (Session): The active SQLAlchemy database session.
            session_tkn (str): The session token associated with the order.
            phone_number (str, optional): The phone number of the customer placing the order.
            total_amount (Decimal, optional): The total cost of the order.
            payment_type (str, optional): The type of payment, either "pre-delivery" or "payment-on-delivery".
            cart_id (int, optional): The ID of the cart fulfilling the order.
            items (list[dict], optional): A list of dictionaries, each containing:
                - product_id (int): ID of the ordered product.
                - quantity (int): Number of units ordered.
                - price_at_purchase (Decimal): Price per unit at the time of purchase.
            user_id (int, optional): The user ID if the customer is registered.

        Returns:
            OrderManager: An instance of `OrderManager` managing the newly created order.
            None: if creation fails.
        """
        LOG.ORDER_LOGGER.info('='*55)
        LOG.ORDER_LOGGER.info(f"Initiating order creation for session: {session_tkn}")

        with session_scope(func=OrderManager.create_new_order) as db_session:

            order = OrderManager.get_order_by_session_tkn(session_tkn=session_tkn)
            if not order:
                if not user_id:
                    user_id = SessionManager.get_userid_associated_with_tkn(
                        db_session=db_session,session_token=session_tkn)
        
                LOG.ORDER_LOGGER.info(f"Creating a new order for session: {session_tkn}, user: {user_id}")
            
                new_order = Order(
                    session=session_tkn,
                    user_id=user_id,
                    phone_number=phone_number,
                    total_amount=total_amount,
                    status="pending", 
                    cart_id=cart_id
                )

                db_session.add(new_order)
                db_session.flush()  
                order_id = new_order.id 
                LOG.ORDER_LOGGER.info(f"New order created with ID: {new_order.id}")

                order_items = [
                    OrderItem(
                        order_id=new_order.id,
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        price_at_purchase=item["price_at_purchase"]
                    )
                    for item in items
                ]

                LOG.ORDER_LOGGER.info(f"{len(items)} order items added for Order ID: {new_order.id}")
                db_session.add_all(order_items)
                db_session.commit()
            
                order = new_order
            else:
                order_id = order.id 
                order_items = [
                    OrderItem(
                        order_id=order.id,
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        price_at_purchase=item["price_at_purchase"]
                    )
                    for item in items
                ]
                for order_item in order_items:
        
                    pre_order_item = db_session.query(OrderItem).filter_by(
                        order_id = order.id,
                        product_id=order_item.product_id
                    ).first()
                    if pre_order_item:
                        LOG.ORDER_LOGGER.debug(f"Updating orderitem {order_item}")
                        pre_order_item.quantity =order_item.quantity
                    else:
                        LOG.ORDER_LOGGER.debug(f"Creating a new order item {order_item}")
                        db_session.add(order_item)
                        db_session.flush()

                
            
                LOG.ORDER_LOGGER.info(f"Existing order found for session: {session_tkn}, Order ID: {order.id}")
                if float(order.total_amount) != float(total_amount):
                    LOG.ORDER_LOGGER.info(f"Updating the order {order.id} from {order.total_amount} to amount {total_amount}")
                    order.total_amount =total_amount
                db_session.commit()

            OrderManager.group_orders_to_vendors(db_session=db_session ,orderid=order.id)

        return OrderManager(db_session=cls.db_session , order_id=order_id)


    def delete_order(self):
        """ Delete the order and its associated items """
        if not self.order:
            return False
        order_id = self.order.id
        with session_scope(func=self.delete_order) as db_session:
            db_session.query(OrderItem).filter_by(order_id=order_id).delete()
            db_session.delete(self.order)
            db_session.commit()
            self.order = None
            return True
    
    @classmethod
    def update_stock_after_order(cls,order_id: int):
        """
        Updates product stock by reducing quantities based on the given order ID.

        Args:
            session (Session): SQLAlchemy database session.
            order_id (int): The ID of the order.
        """
        with session_scope(func=cls.update_stock_after_order) as session:
            order_items = session.query(OrderItem).filter_by(order_id=order_id).all()

            if not order_items:
                LOG.ORDER_LOGGER.info(f"No items found for order ID: {order_id}")
                return

            for item in order_items:
                product = session.query(Product).filter_by(id=item.product_id).first()
                if product:
                    if product.stock >= item.quantity:
                        product.stock -= item.quantity
                    else:
                        LOG.ORDER_LOGGER.info(f"Not enough stock for Product ID {product.id} (Requested: {item.quantity}, Available: {product.stock})")
                        continue

                session.commit()
            LOG.ORDER_LOGGER.info(f"Stock updated successfully for order ID: {order_id}")

  

    @classmethod 
    def update_order(cls, order_id: int, **kwargs):
  
        LOG.ORDER_LOGGER.info(f"Updating order {order_id} with fields: {kwargs}")
        with session_scope(func=cls.update_order) as db_session:
            order = db_session.query(Order).filter_by(id=order_id).first()

            for key, value in kwargs.items():
                if hasattr(order, key):
                    LOG.ORDER_LOGGER.debug(f"Updating {key} to {value} for order {order_id}")
                    setattr(order, key, value)

            db_session.commit()
            LOG.ORDER_LOGGER.info(f"Order {order_id} updated successfully")

        return True 
    
    @classmethod
    def divide_to_vendors(cls,order_id):
        num_vendors ,vendors_data =VendorTransactionSystem.divide_order_to_vendors(order_id=order_id)
        LOG.ORDER_LOGGER.info("[ORDER DIVISION] order {} allocated to {} vendors".format(order_id,num_vendors))
        return vendors_data

    @staticmethod
    def collect_payment(phone , amount ,orderid):
        LOG.ORDER_LOGGER.info(f"Initiating payment collection for session : {orderid}, Phone: {phone}, Amount: {amount}")
        response = None

        try:
            config = JSONConfig(json_path='config.json')
            url = config.payment_url
       
            headers = {"Authorization": f"Bearer { config.authkey}", "Content-Type": "application/json"}
            payload = json.dumps({'phone': phone, "amount": amount, 'orderid': orderid})

            response = requests.post(url=url + "/pay", data=payload, headers=headers, timeout=7)
            LOG.ORDER_LOGGER.info(f"The response is {response}")
            LOG.ORDER_LOGGER.info(f"Payment request sent for session : {orderid}, Status Code: {response.status_code}:{response.content}")

            if response.status_code != 200:
                LOG.ORDER_LOGGER.warning(f"Invalid payment response for session: {orderid}, Response: {response.content}")
                return False

        
            in_voice_id = response.json().get('response',{}).get('invoice_id' ,None)

            if not in_voice_id:
                LOG.ORDER_LOGGER.error(f"Invoice ID not found in response for session: {orderid}, Response: {response.content}")
                return False
                        
            LOG.ORDER_LOGGER.info(f"Invoice ID {in_voice_id} generated for session: {orderid}. Waiting for status update.")

            time.sleep(config.DELAY_BEFORE_STATUS_CHECK)  

            LOG.ORDER_LOGGER.info(f"Checking payment status for session: {in_voice_id}")

            start = perf_counter()
            for i in range(5):

                response = requests.post(
                    url=url + '/check-status',
                    headers=headers,
                    json={
                        "SIMULATE": True, 
                          "MAXRETRIES":5,
                          'invoice_id':in_voice_id

                    }
                )
               
                status = response.json().get('MESSAGE')
                LOG.ORDER_LOGGER.info(f"Payment status check {i+1}/5 for Invoice ID: {in_voice_id} - Status: {status}")

                if status == "COMPLETE":
                    LOG.ORDER_LOGGER.info(f"Payment completed for session: {orderid}")
                    return 'paid'
                elif status == "FAILED":
                    LOG.ORDER_LOGGER.warning(f"Payment failed for session: {orderid}")
                    return 'canceled'
                else:
                    time.sleep(2)
            
            LOG.ORDER_LOGGER.info(f"Payment is pending for session: {orderid} after multiple checks: TIME TAKEN {perf_counter()-start}")
            return 'pending'

        except Exception as e:
            if response:
                LOG.ORDER_LOGGER.error(f"Exception occurred in payment collection for session: {orderid}: error={e} status_code={response.status_code} Latest response:{response.content}")
            else:
                LOG.ORDER_LOGGER.error(f"Exception occurred in payment collection for session: {orderid}: error={e}")
            return None

     
                

