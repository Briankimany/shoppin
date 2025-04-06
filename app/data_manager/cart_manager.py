
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_item import OrderItem , VendorOrder
from app.models.product import Product


from config.config import JSONConfig
from .session_manager import SessionManager
from .vendor_transaction import VendorTransactionSystem
import json , requests ,time
from sqlalchemy.exc import SQLAlchemyError
from app.routes.logger import LOG

class OrderManager:
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
        self.db_session = db_session
        self.order = self.db_session.query(Order).where(Order.id == order_id).first() if not isinstance(order_id , Order) else order_id
        self.config = JSONConfig(json_path="config.json")

    @staticmethod
    def get_order_by_session_tkn(db_session:Session , session_tkn):
        """
        Retrieves an order associated with a given session token.

        Args:
            db_session (Session): The active SQLAlchemy database session.
            session_tkn (str): The session token linked to the order.

        Returns:
            Order or None: The order object if found, otherwise None.
         """
        return db_session.query(Order).filter(Order.session == session_tkn, Order.status != "paid" ,Order.status != "canceled").first()


    @staticmethod
    def group_orders_to_vendors(db_session:Session , orderid:int):
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

    @staticmethod
    def create_new_order(db_session:Session, session_tkn, phone_number=None, 
                         total_amount=None, payment_type=None, cart_id=None, items=[], user_id=None) :
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

        order = OrderManager.get_order_by_session_tkn(db_session=db_session,session_tkn=session_tkn)
        try:
            if not order:
                if not user_id:
                    user_id = SessionManager.get_userid_associated_with_tkn(db_session=db_session,session_token=session_tkn)
        
                LOG.ORDER_LOGGER.info(f"Creating a new order for session: {session_tkn}, user: {user_id}")
            
                new_order = Order(
                    session=session_tkn,
                    user_id=user_id,
                    phone_number=phone_number,
                    total_amount=total_amount,
                    status="pending", 
                    payment_type=payment_type,
                    cart_id=cart_id
                )

                db_session.add(new_order)
                db_session.commit()  

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
                db_session.flush()
                
                order = new_order
            else:
                LOG.ORDER_LOGGER.info(f"Existing order found for session: {session_tkn}, Order ID: {order.id}")
                if float(order.total_amount) != float(total_amount):
                    LOG.ORDER_LOGGER.info(f"Updating the order {order.id} from {order.total_amount} to amount {total_amount}")
                    order.total_amount =total_amount
                    db_session.commit()

            OrderManager.group_orders_to_vendors(db_session=db_session ,orderid=order.id)
            return OrderManager(db_session=db_session , order_id=order)
        except SQLAlchemyError as e:
            db_session.rollback()
            LOG.ORDER_LOGGER.error(f"Database Error while creating order: {e}")
            
            return None
        
    def get_order_details(self, include_items=True):
        """
        Retrieves detailed information about an order.

        Args:
            include_items (bool, optional): Whether to include order item details. Defaults to True.

        Returns:
            dict or None: A dictionary containing order details, or None if the order does not exist.
            
            Structure:
            {
                "order_id": int,
                "user_id": int or None,
                "phone_number": str ,
                "total_amount": float,
                "status": str,
                "payment_type": str,
                "cart_id": int ,
                "created_at": datetime,
                "updated_at": datetime,
                "items": [
                    {
                        "product_id": int,
                        "quantity": int,
                        "price_at_purchase": float
                    },
                    ...
                ]  # Only if `include_items` is True
            }
        """

        if not self.order:
            return None
        
        order_data = {
            "order_id": self.order.id,
            "user_id": self.order.user_id,
            "phone_number": self.order.phone_number,
            "total_amount": float(self.order.total_amount),
            "status": self.order.status,
            "payment_type": self.order.payment_type,
            "cart_id": self.order.cart_id,
            "created_at": self.order.created_at,
            "updated_at": self.order.updated_at,
        }

        if include_items:
            order_data["items"] = [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price_at_purchase": float(item.price_at_purchase),
                }
                for item in self.db_session.query(OrderItem).filter_by(order_id=self.order.id).all()
            ]

        return order_data

    def delete_order(self):
        """ Delete the order and its associated items """
        if not self.order:
            return False
        try:
            self.db_session.query(OrderItem).filter_by(order_id=self.order.id).delete()
            self.db_session.delete(self.order)
            self.db_session.commit()
            self.order = None
            return True
        except SQLAlchemyError as e:
            self.db_session.rollback()
            print(f"Database Error: {e}")
            return False
    def update_stock(self , order_id:int):
        return OrderManager.update_stock_after_order(session=self.db_session , order_id=order_id)


    @staticmethod
    def update_stock_after_order(session: Session, order_id: int):
        """
        Updates product stock by reducing quantities based on the given order ID.

        Args:
            session (Session): SQLAlchemy database session.
            order_id (int): The ID of the order.
        """
        try:
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

        except Exception as e:
            session.rollback()  # Rollback in case of an error
            print(f"Error updating stock: {e}")

    def update_order(self, order_id: int, **kwargs):
        """
        Updates specified attributes of an existing order.

        This method modifies provided attributes of an order in the `Order` table, ensuring only valid fields are updated.

        Args:
            order_id (int): The ID of the order to be updated.
            **kwargs: Key-value pairs representing the fields to be updated. 
                    Valid keys include:
                    - phone_number (str)
                    - total_amount (Decimal)
                    - status (str) -(pending, paid, canceled)
                    - payment_type (str)
                    - vendor_id (int)

        Returns:
            bool: True if the update is successful, False otherwise.
         """
        LOG.ORDER_LOGGER.info(f"Updating order {order_id} with fields: {kwargs}")

        if not self.order or self.order.id != order_id:
            LOG.ORDER_LOGGER.warning(f"Order ID mismatch or order not found for update: {order_id}")
            return False

        try:
            for key, value in kwargs.items():
                if hasattr(self.order, key):
                    LOG.ORDER_LOGGER.debug(f"Updating {key} to {value} for order {order_id}")
                    setattr(self.order, key, value)

            self.db_session.commit()
            LOG.ORDER_LOGGER.info(f"Order {order_id} updated successfully")
            return True
        except SQLAlchemyError as e:
            self.db_session.rollback()
            LOG.ORDER_LOGGER.error(f"Database Error while updating order {order_id}: {e}")
            return False

    
    def divide_to_vendors(self,order_id):
        return OrderManager.allocate_order_shares(order_id=order_id ,
                                                  db_session=self.db_session)
    
    @staticmethod
    def allocate_order_shares(order_id , db_session:Session):
        num_vendors ,vendor_data =VendorTransactionSystem.divide_order_to_vendors(order_id=order_id , 
                                                        db_session=db_session)
        LOG.VENDOR_LOGGER.info("[ORDER DIVISION] order {} allocated to {} vendors".format(order_id,num_vendors))
        return vendor_data
    
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
            LOG.ORDER_LOGGER.info(f"Payment request sent for session : {orderid}, Status Code: {response.status_code}")

            if response.status_code != 200:
                LOG.ORDER_LOGGER.warning(f"Invalid payment response for session: {orderid}, Response: {response.content}")
                return False

            data = {'code': response.status_code, 'invoiceid': response.json().get("response")}
            in_voice_id = data["invoiceid"]["invoice"]["invoice_id"]
            
            LOG.ORDER_LOGGER.info(f"Invoice ID {in_voice_id} generated for session: {orderid}. Waiting for status update.")

            time.sleep(config.DELAY_BEFORE_STATUS_CHECK)  
            LOG.ORDER_LOGGER.info(f"Checking payment status for session: {in_voice_id}")

            for i in range(5):
                response = requests.get(
                    url=url + f'/check-status/{in_voice_id}',
                    headers=headers,
                    data=json.dumps({"SIMULATE": config.SIMULATE, "MAXRETRIES": config.MAX_RETIRES})
                )

                code = response.status_code
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

            LOG.ORDER_LOGGER.warning(f"Payment pending for session: {orderid} after multiple checks")
            return 'pending'

        except Exception as e:
            LOG.ORDER_LOGGER.error(f"Exception occurred in payment collection for session: {orderid}: {e} Latest response:{response}")
            return None

       
