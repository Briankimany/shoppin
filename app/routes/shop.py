from flask import Blueprint, render_template, request, session, redirect, url_for, flash ,jsonify ,g

from app.data_manager.session_manager import SessionManager 
from app.data_manager.vendor import VendorObj
from app.data_manager.cart_manager import OrderManager
from app.routes.logger import LOG
from config.config import JSONConfig
from app.routes.routes_utils import  UserManager
from app.data_manager.vendor_transaction import VendorTransactionSystem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from functools import wraps
from datetime import datetime

from app.data_manager.payments import PaymentManager , PaymentCategory , PaymentMethod

from app.routes.routes_utils import session_set
config = JSONConfig("config.json")
engine = create_engine(f"sqlite:///{config.database_url.absolute()}")
Session = sessionmaker(bind=engine)
db_session = Session()


shop_bp = Blueprint("shop", __name__, url_prefix="/shop")

session_manager = SessionManager(db_session)
user_obj = UserManager(db_session , user=None)


class Category:
    def __init__(self , name , products_list):
        self.name = name 
        self.products = products_list

def vendor_selected(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        print("Checking if vendor is selected...")
        if "vendor_id" not in session:
            LOG.SHOP_LOGGER.warning("Vendor ID missing! Redirecting to shop home.")
            return redirect(url_for("shop.shop_home"))
        return func(*args, **kwargs)  # Ensure the wrapped function still executes
    return decorated_func



@shop_bp.before_request
def load_current_user():
    user_id = session.get('user_id')
    if user_id:
        user_obj.reload_object(user=user_id)
        g.current_user = user_obj.user
        if not g.current_user:
            session.clear()
        else:
            g.current_user.is_authenticated = True
    else:
        g.current_user = None

@shop_bp.context_processor
def inject_user():
   
    user = getattr(g, 'current_user', None)
    print("the current user is ",user)
    return {
        'current_user': user,
        'is_authenticated':True,
        'now': datetime.now()
    }



@shop_bp.route('/')
@session_set
def shop_home():
    vendors = VendorObj.get_all_vendors(db_session=db_session)
    return render_template("shop/shops.html", vendors=vendors)



@shop_bp.route("/logout")
@session_set
def logout():
    session.clear()
    return "Logged out"



@shop_bp.route("/complete-payment")
@session_set
def process_payment():
    cartdata =  session.get('cart' ,None)
    if  cartdata:
        total_cost =   cartdata['TotalCost']
        phone = session_manager.get_phone_from_session_token(tkn=session['session_token'])
        LOG.SHOP_LOGGER.info(f"TKN {session['session_token']} is checking out cost : {total_cost}")
        return render_template("shop/payment.html" , total_cost = total_cost , phone=phone)
    else:
        return redirect(url_for('shop.view_cart'))



@shop_bp.route("/<vendor_id>")
def vendor_products(vendor_id):
    """Displays products for a specific vendor."""
    session['vendor_id']=vendor_id
    vendor = VendorObj(vendor_id=vendor_id, db_session=db_session)
    products = vendor.get_product("vendor_id", vendor_id, occurrence="all")
    final_data = {}
    for product in products:
        key = product.category
        if key not in final_data:
            final_data[key]=[]
        final_data[key].append(product)
        
    p = [Category(k , v) for  k , v in final_data.items()]

    return render_template("shop/products.html", categories=p ,vendor=vendor.vendor_table)

@shop_bp.route("/product/<product_id>")
@vendor_selected
def specific_product(product_id):
    """Displays a specific product."""
    product = VendorObj(session.get("vendor_id"), db_session=db_session).get_product(
        product_key="id", value=product_id, occurrence="first"
    )
    return render_template("shop/specific_product.html", product=product)


@shop_bp.route("/add_to_cart", methods=["POST"])
@session_set
def add_to_cart():
    session_token = session.get("session_token")
    if not session_token:
        return jsonify({"success": False, "error": "Session expired. Please refresh and try again."}), 400

    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")
  
    if not product_id or not quantity:
        return jsonify({"success": False, "error": "Invalid data"}), 400
    result = session_manager.add_to_cart(session_token, product_id, int(quantity))
    status = result['status']
    if status == "error":
         reason = result['reason']
         LOG.SHOP_LOGGER.error("error during add to cart product: {}  quantity: {} reason: {}".format(product_id , quantity , reason))
         return jsonify({"success": False})
    return jsonify({"success": True})


@shop_bp.route("/cart/remove", methods=["POST"])
@session_set
def remove_from_cart():
    """Removes a product from the cart."""
    session_token = session["session_token"]
    data = request.get_json()

    product_id = data.get('product_id')

    if all ((session_manager ,product_id)):
        session_manager.remove_from_cart(session_token=session_token, product_id=product_id)
    return jsonify({"success": False})


@shop_bp.route("/cart")
@session_set
def view_cart(): 
    """Displays the user's cart."""
    session_token = session["session_token"]
  
    cart_id = session_manager.get_cart(session_token)
    cart_items = session_manager.get_cartitems(cart_id=cart_id)
   
    subtotal =sum([i.quantity*i.product.price for i in cart_items])
  
    return render_template("shop/cart.html", cart_items=cart_items , subtotal=subtotal)


@shop_bp.route("/update_cart", methods=["POST"])
@session_set
def update_cart():
    """Handles updating cart item quantities via JavaScript."""
    session_token = session.get("session_token")
    if not session_token:
        return jsonify({"success": False, "message": "Session expired. Please refresh and try again."}), 400

    cart_id = session_manager.get_cart(session_token)

    if not cart_id:
        return jsonify({"success": False, "message": "Cart not found."}), 404

    data = request.get_json()
    quantities = data.get("quantities", {})
    errored =  False
    for product_id, quantity in quantities.items():
        if session_manager.verify_available_stock(int(product_id) , int(quantity)):
            session_manager.update_cart_item(cart_id, int(product_id), int(quantity))
        else:
            LOG.SHOP_LOGGER.error(f"from {session_token}: avaliable stock exceeded for product id {product_id} {quantity}")
            errored = True
    if errored:
        return jsonify({"success": True, "message": "Cart updated but some items failed."})
    return jsonify({"success": True, "message": "Cart updated successfully."})


@shop_bp.route("/checkout", methods=["GET", "POST"])
@session_set
def checkout():
    """Handles the checkout process."""
    session_token = session.get("session_token")
    cart_summary = session_manager.get_cart_summary(session_token=session_token)
    session['cart']=cart_summary
   
    return render_template("shop/checkout2.html", cart_summary = cart_summary)



@shop_bp.route("/api-pay" , methods = ['POST'])
def api_process_payment():
    data = request.get_json()
    phone = data.get("phone")
    amount = data.get("amount")

    if phone[0] == "0":
        phone = phone.replace("0" , "254")

    if not phone or not amount:
        return jsonify({"message": "Invalid data received."}), 400

    session_manager =  SessionManager(db_session=db_session)
    cart_id = session_manager.get_cart(session_token=session["session_token"])

    items = [{"product_id":i.product_id , 
              "quantity":i.quantity ,
                "price_at_purchase":i.product.price} for i in session_manager.get_cartitems(cart_id=cart_id)]
    

    order= OrderManager.create_new_order(db_session=db_session,
                                            session_tkn=session["session_token"],
                                            phone_number=phone,
                                            total_amount=amount,
                                            cart_id=cart_id,
                                            items=items
                                            )
    status = OrderManager.collect_payment(phone=phone, amount=amount , orderid=order.order.session)
    LOG.SHOP_LOGGER.info("collected payment: phone {} status {} amount {} orderid {}".format(
        phone , status , amount , order.order.session
    ))
    if status:
        order.update_order(order.order.id , status =status)
    if status == 'paid':
        cart_status = session_manager.update_cart(cart_id=cart_id , attribute="is_active" , new_value=False)
        order.update_stock(order_id = order.order.id)
        vendor_data =order.divide_to_vendors(order_id=order.order.id)
        
        for vendor_phone , amount in vendor_data.items():
            PaymentManager.record_payment(source= phone,
                                        recipient=vendor_phone,
                                        amount=amount ,
                                        method=PaymentMethod.MPESA,
                                        category=PaymentCategory.PRODUCT_SALE,
                                        description="Products from order id {} sold at {}".format(order.order.id ,
                                                                                                  amount))
        return jsonify({"message": "success"}) , 200
    return jsonify({"message": f"Payment request sent for ksh: {amount} to +{phone}."}) , 200



@shop_bp.route("/search")
def search():
    return "Search Page (Placeholder)"

