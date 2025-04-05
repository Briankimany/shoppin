from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify

from app.models.user_profile import UserProfile as User 
from app.data_manager.users_manager import UserManager
from config.config import JSONConfig
from app.routes.routes_utils import session_set 
from app.routes.logger import LOG
from app.routes.mail import send_reset_email
from app.data_manager.token_manager import ResetTokenManager
from functools import wraps

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import time




config = JSONConfig('config.json')

engine = create_engine(f"sqlite:///{config.database_url.absolute()}")
Session = sessionmaker(bind=engine)
db_session = Session()

user_bp = Blueprint("user", __name__, url_prefix="/user")
user_obj = UserManager(db_session=db_session , user=None)

def force_user_reload(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global user_obj 
        if user_obj:
            if "user_id" in session:
                user_obj.reload_object(session["user_id"] , token=session.get("session_token"))
            if "session_token"  in session:
                user_obj.session_tkn = session.get('session_token') 
        return func(*args, **kwargs)
    
    return wrapper


@user_bp.route("/")
def home():
    return "".join([f"<br> {k}: {v}</br>" for k,v in session.items()])


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if request.method == "POST":
        name = request.form["identifier"]
        password = request.form["password"] 
        verified = user_obj.verify_password(password=password , user=name)  
        is_vendor = session.get('IS_VENDOR' , None) == True
       
        if verified:
            user_obj.reload_object(user=name)
            session["user_id"] = user_obj.user.id
            session['user_name'] =name
            previous_token = user_obj.get_tkn_from_user_id()
            if previous_token:
                session['session_token'] = previous_token.token
                
            user_obj.session_tkn = session['session_token']
            user_obj.self_update_session(data={'user_id':user_obj.user.id})

            LOG.USER_LOGGER.info(f"[LOGED IN] {user_obj}")
            if  is_vendor:
                session['IS_VENDOR'] = None
                vendor = user_obj.is_vendor()
                if vendor:
                    session['vendor_id'] =vendor.id
                    return redirect (url_for('vendor.dashboard'))
            return redirect(url_for("shop.shop_home"))

    return render_template("login/login.html")


@user_bp.route("/register", methods=["GET", "POST"])
@session_set
def register():
    """User registration"""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        name = request.form['name']
        phone = request.form['phone']
        unique_name , names =  user_obj.verify_unique_name(db_session=db_session , suggested_name=name)
        session['names']=names
        if unique_name:
            user_obj.self_register( data={"name":name,"email":email,"password_hash":password , 'phone':phone})
        else:
            return render_template("login/register.html" , message = "enter a unique name")

        session["user_id"] = user_obj.user.id  
        session['user_name'] = user_obj.user.name
        user_obj.session_tkn = session['session_token']
        user_obj.self_update_session(data={'user_id':user_obj.user.id})
       
        if session.get('vendor_register' , None):
            session['vendor_register'] = None
            return redirect (url_for ("vendor.add_details"))
        return redirect(url_for("shop.shop_home"))
    return render_template("login/register.html")


@user_bp.route("/logout")
@session_set
def logout():
    """Logs out the user"""
    session.clear()
    return redirect(url_for("shop.shop_home"))

@user_bp.route("/profile")
@session_set
def profile():
    """User profile page"""
    if  'user_id' not in session:
        return redirect(url_for("user.login"))
    else:
        user_obj.reload_object(user=session.get('user_id'))
    return render_template("user/profile.html", user=user_obj.user)


@user_bp.route("/edit-profile" , methods = ["POST"])
@session_set
def edit_profile():
    """
    data = {name:<name> , phone: <phone> , email: <email> , password_hash: <password>}
    """
    data = request.get_json().get('data')
    name = data.get('name')
    email = data.get("email")
    phone = data.get("phone")
    new_data = {'name': name ,'phone':phone , 'email':email}
    LOG.USER_LOGGER.info("***"*10)
    if "old_password" in data.keys() and "new_password" in data.keys():
        verified = user_obj.verify_password(user= session['user_id'] , password=data.get("old_password"))
        LOG.USER_LOGGER.info(f"account verified to modify {verified}")
        if verified:
            new_data['password_hash'] = data.get("new_password")
        else:
            LOG.USER_LOGGER.info(f"Attempted password change: user={session['user_id']} to: {data.get('new_password')}")
            return "Done" , 401

    LOG.USER_LOGGER.info(f"data from edit -profile: {new_data}")
    user_obj.reload_object(user= session['user_id'])
    user_obj.update_data(data = new_data)
    return "Done" , 200


@user_bp.route("/orders")
@force_user_reload
@session_set
def orders():
    orders = user_obj.get_order_from_session_tkn(session_tkn=session['session_token'] , status='all')
    return render_template("user/orders.html", orders=orders)


@user_bp.route("/orders/<int:order_id>/items", methods=["GET"])
@force_user_reload
@session_set
def get_order_items(order_id):
    items = user_obj.get_my_previous_order_items(order_id)
    print(items)

    return jsonify(items)


@user_bp.route('/validate-token/<token>', methods=['GET', 'POST'])
def validate_token(token):
 
    token_record = ResetTokenManager.verify_token(db_session=db_session,
                                                reset_token=token)
    if not token_record:
        return render_template("user/password_reset_error.html") ,400
    
    if request.method == 'GET':
        return render_template("user/reset_password.html",
                             user_id=token_record.user_id,
                             token=token)
    
    if request.method == 'POST':
        data = request.get_json()
        new_password = data.get('new_password')

        user_obj.reload_object(user=token_record.user_id ,token=session.get("session_token"))
        user_obj.update_data({"password_hash":new_password})
        session.clear()

        return jsonify({
            "message": "Password updated successfully",
            "redirect_url": url_for('user.login')
        }), 200
        

@user_bp.route("/forgot-password", methods=["GET"])
@force_user_reload
@session_set
def forgot_password():
    response = None
    return render_template("user/forgot_password.html" , message=response)

@user_bp.route("/reset-password" , methods = ['POST'])
def reser_user_password():
    email = request.get_json().get("email")  
    user = UserManager.get_user_(db_session=db_session ,user=email)
    response = {
        "success": True,
        "message": "If this email exists in our system, you'll receive a reset link shortly.",
        "cooldown": 6 
        }
    if user:
        reset_token = ResetTokenManager.create_token(db_session=db_session ,
                                                        session_token=session.get("session_token"),
                                                        user_id=user.id ,expires_in_hours=1)
        
        
        reset_link = url_for("user.validate_token", token=reset_token.reset_token, _external=True)
        send_reset_email(recipient=user.email, reset_link=reset_link)
    else:
        time.sleep(3)
    return jsonify(response) ,200