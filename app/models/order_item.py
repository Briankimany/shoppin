
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, TIMESTAMP , String
from sqlalchemy.sql import func

from .order import Order
from .product import Product
from .base import Base
from .vendor import Vendor



class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey(Order.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __reprs__(self):
        return self.__str__()
    def __str__(self):
        return f"<OrderItem id={self.id} , orderid={self.order_id} , quantity={self.quantity} , product={self.product_id}"

class VendorOrder(Base):
    __tablename__ = "vendor_orders"
    id = Column(Integer , primary_key=True ,autoincrement = True)
    vendorid = Column(Integer , ForeignKey(Vendor.id) , nullable =False)
    orderid = Column(Integer , ForeignKey(Order.id) , nullable = False)
    orderitem = Column(Integer , ForeignKey(OrderItem.id),nullable = False)

