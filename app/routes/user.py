from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify ,g

from app.data_manager.users_manager import UserManager

from app.routes.routes_utils import session_set  ,meet_user_requirements ,inject_user_data ,db_session ,bp_error_logger
from app.routes.logger import LOG
from app.routes.mail import MailService
from app.data_manager.token_manager import ResetTokenManager ,AcctivationTokenManager
from functools import wraps
import time

from .views.user import VerifyAccount


user_bp = Blueprint("user", __name__, url_prefix="/user")
user_obj = UserManager(db_session=db_session , user=None)

user_bp.add_url_rule('/account-verification' ,view_func=VerifyAccount.as_view("account_verification"))


def force_user_reload(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global user_obj 
        if user_obj:
            if "user_id" in session or 'vendor_id' in session:
                user_id = session.get("user_id") or session.get("vendor_id")
                user_obj=user_obj.reload_object(int(user_id), token=session.get("session_token"))
            if "session_token"  in session:
                user_obj.session_tkn = session.get('session_token') 
        return func(*args, **kwargs)
    
    return wrapper


@user_bp.before_request
def load_current_user():
    global user_obj
    user_id = session.get('user_id') or session.get('vendor_id')
    if user_id:
        user_id = int(user_id)

    if user_id:
        user_obj.reload_object(user=user_id)
        g.current_user = user_obj.user
        if not g.current_user:
            session.clear()
        else:
            g.current_user.is_authenticated = True
    else:
        g.current_user = None

@user_bp.context_processor
def inject_user():
    return inject_user_data()


@user_bp.route("/")
def home():
    return "".join([f"<br> {k}: {v}</br>" for k,v in session.items()])


def send_activation_link(return_json = True):
    user_id = session['user_id']
    token = AcctivationTokenManager.create_account_activation(expire_after=1
                                                            ,session_token=session['session_token'],
                                                            user_id=int(user_id))
    LOG.USER_LOGGER.debug(f"Token generated {token}")

    data = MailService.send_account_activation_link(
        activation_url=url_for("user.account_verification" ,
                            dst=url_for('user.profile' ,_external=True),token=token ,_external=True),
        recepient=user_obj.user.email,
        return_json=return_json
    )
    LOG.USER_LOGGER.debug(f"Response from sending email {data.get_json()if return_json else data}")
    LOG.USER_LOGGER.debug("-"*35)

    return data



@user_bp.route('/send-verification', methods=['POST' ,'GET'])
@force_user_reload
@session_set
def verify_account():

    user_id = session.get('user_id')
    if not user_id:
        return jsonify( {"message":"error",'data':"invalid request"})

    user_obj.reload_object(int(user_id))

    LOG.USER_LOGGER.debug  ("*"*35)
    LOG.USER_LOGGER.debug(f"Account verification for {user_obj.user.email}")

    if request.method == 'GET':
        LOG.USER_LOGGER.debug("Displaying account confirmation page")
        LOG.USER_LOGGER.debug  ("*"*35)
        return render_template("user/account_confirmation.html" ,user_email = user_obj.user.email)

    else:
        return send_activation_link()




@user_bp.route("/login", methods=["GET", "POST"])
@bp_error_logger(LOG.USER_LOGGER)
@session_set
def login():
    """User login"""
    LOG.USER_LOGGER.debug("-"*35)

    if request.method == "POST":
        name = request.form["identifier"]
        password = request.form["password"] 

        LOG.USER_LOGGER.debug("[login] Attempted login name: {} passwd: {} ".format(name , password))
        verified = user_obj.verify_password(password=password , user=name)  
        LOG.USER_LOGGER.debug(f"[login] Verified = {verified}")

        status_code = 403
        if verified:
            status_code= 200
            user_obj.reload_object(user=name)
                
            session["user_id"] = user_obj.user.id
            session['user_name'] =name
        
            if not user_obj.user.activated == True:
                is_vendor = False
                LOG.USER_LOGGER.debug("Account not verified")
                url = url_for('user.verify_account',_external=False)
            
            else:
                previous_token = user_obj.get_tkn_from_user_id() ## make sure its not expired

                if previous_token:
                    session['session_token'] = previous_token.token
                    
                user_obj.session_tkn = session['session_token']
                user_obj.self_update_session(data={'user_id':user_obj.user.id})

                LOG.USER_LOGGER.info(f"[LOGED IN] {user_obj}")
                
                is_vendor = user_obj.verify_is_vendor(db_session=db_session,user_name=int(session["user_id"]))

                if  is_vendor:
                    session['IS_VENDOR'] = None
                    session['vendor_id'] =session['user_id']
                    url= url_for('vendor.dashboard' ,_external=False)
                else:
                    url = url_for("shop.shop_home", _external=False)

            data ={"message":"success",'data':f"redirecting to {'portal' if is_vendor else 'Our shops'}",'url':url}

        else:
            LOG.USER_LOGGER.debug(f"[LOG IN FAILED] {user_obj} :{name} :{password}")
            url = url_for("user.login",_external=False)
            data = {"message":"error" ,'data':"Invalid name/email or password",'url':url}
        LOG.USER_LOGGER.debug("-"*35)
        return jsonify(data)  ,status_code
    
    LOG.USER_LOGGER.debug("-"*35)
    return render_template("login/login.html")


@user_bp.route("/register", methods=["GET", "POST"])
@session_set
@session_set
def register():
    """User registration"""
    if request.method == "POST":
        LOG.USER_LOGGER.debug("-"*35)
        
        email = request.form["email"]
        password = request.form["password"]
        name = request.form['name']
        first_name = request.form['first_name']
        second_name = request.form['second_name']
        phone = request.form['phone']

        unique_name , msg =  user_obj.verify_unique_name(db_session=db_session , suggested_name=name ,email=email)
    
        if unique_name:
            LOG.USER_LOGGER.debug("[REG] Registering {} email: {} phone {}".format(name , email,phone))
            user_obj.self_register( data={"name":name,
                                          "first_name":first_name,
                                          "second_name":second_name,
                                          "email":email,
                                          "password_hash":password ,
                                            'phone':phone})
        else:
            return jsonify({"message":"warning" ,"data":msg})

        session["user_id"] = user_obj.user.id  
        session['user_name'] = user_obj.user.name
        user_obj.session_tkn = session['session_token']
        user_obj.self_update_session(data={'user_id':user_obj.user.id})

        email_sent = send_activation_link(False)
        url = url_for('user.verify_account',_external=True)

        data ={"message":"success" if email_sent else 'error',
               'data':'Ready for verification' if email_sent else 'An error occured and could not verify email','url':url}
        LOG.USER_LOGGER.debug(f"[VER-DATA] {data}")

        return jsonify(data)

    return render_template("login/register.html")


@user_bp.route("/logout")
@meet_user_requirements
@session_set
def logout():
    """Logs out the user"""
    session.clear()
    return redirect(url_for("shop.shop_home"))


@user_bp.route("/profile")
@bp_error_logger(logger=LOG.USER_LOGGER ,raise_exeption=True)
@meet_user_requirements
@session_set
def profile():
    """User profile page"""
    id_ =int(session['user_id'] or session['vendor_id'])

    return render_template("user/profile.html", user=UserManager(db_session,id_).user)


@user_bp.route("/edit-profile" , methods = ["POST"])
@bp_error_logger(LOG.USER_LOGGER)
@meet_user_requirements
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
    user_obj.reload_object(user= int(session['user_id']))

    data_updated = user_obj.update_data(data = new_data)
    return jsonify({"message":"success" if data_updated else "error" ,"data":"Completed edits"}) ,200 if data_updated else 400



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
    
    return jsonify(items)


@user_bp.route('/validate-token/<token>', methods=['GET', 'POST'])
def validate_token(token):
 
    token_record = ResetTokenManager.verify_token(db_session=db_session,
                                                reset_token=token)
    
    destination = request.args.get('dst')
    if destination:
        return redirect (destination)
    
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
@session_set
def reser_user_password():
    email = request.get_json().get("email") 
    user = UserManager.get_user_(db_session=db_session ,user=email)
    response = {
        "success": True,
        "message": "If this email exists in our system, you'll receive a reset link shortly.",
        "cooldown": 6 
        }
    if user:
        LOG.USER_LOGGER.debug("[PASS-RESET] Initiating password reset for {}".format(email))
        reset_token = ResetTokenManager.create_token(db_session=db_session ,
                                                        session_token=session.get("session_token"),
                                                        user_id=user.id ,expires_in_hours=1)
        
        
        reset_link = url_for("user.validate_token", token=reset_token.reset_token, _external=True)
        MailService.send_reset_email(recipient=user.email, reset_link=reset_link)
    else:
        LOG.USER_LOGGER.info("[PASS-RESET] invalid email : {}".format(email))
        time.sleep(3)
    return jsonify(response) ,200

