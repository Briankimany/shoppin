
from flask import session , redirect , url_for ,request ,g

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from functools import wraps

from app.data_manager.session_manager import SessionManager ,timedelta
from config.config import JSONConfig
from app.data_manager.users_manager import UserManager
from app.routes.logger import LOG , bp_error_logger

from datetime import datetime ,timezone

config = JSONConfig('config.json')
engine = create_engine(f"sqlite:///{config.database_url.absolute()}")
Session = sessionmaker(bind=engine)
db_session = Session()
session_manager = SessionManager(db_session)
user_obj = UserManager(db_session , user=None)


def get_user_ip():
    return request.headers.get('X-Real-IP') or request.remote_addr 

def get_or_create_session():
    """Ensures a session token exists in the user's session."""

    if "session_token" not in session or not session_manager.verify_session_token(session["session_token"]):
        token =  session_manager.create_new_session()
        if not token:
            raise Exception("Token not set")
        session["session_token"] = token
    if "user_id" in session:
        user_obj.session_tkn = session["session_token"]
        user_obj.reload_object(session["user_id"])

        update_data = {"user_id": user_obj.user.id,
                    'expires_at':datetime.now(timezone.utc)+timedelta(hours=24*config.session_days)}
        LOG.SESSIONS_LOGGER.debug(f"[sess-update] Updating session data {update_data}")
        user_obj.self_update_session(data=update_data)
    
    LOG.SESSIONS_LOGGER.debug(f"Session initialized. User ID: {session.get('user_id')}")
    LOG.SESSIONS_LOGGER.info("-"*35)
    return session["session_token"]



def meet_vendor_requirements(func):
    @wraps(func)
    def decorated_func(*args , **kwargs):
        user_id = session.get('user_id')
        if  user_id:
            is_vendor = UserManager.verify_is_vendor(db_session=db_session ,user_name=int(user_id))
            if  is_vendor:
                session['vendor_id'] = user_id
                
        if "vendor_id" not in session:
            return redirect (url_for("vendor.login"))
        return func(*args , **kwargs)
    return decorated_func

def meet_user_requirements(func):
    @wraps(func)
    def decorated_func(*args , **kwargs):
        vendor_id = session.get('vendor_id')
        if  vendor_id:
            session['user_id'] = vendor_id
        if "user_id" not in session:
            return redirect (url_for("user.login"))
        return func(*args , **kwargs)
    return decorated_func


def session_set(func):
    @wraps(func)
    def decorated_func(*args , **kwargs):
        get_or_create_session()
        return func(*args , **kwargs)
    return decorated_func


def inject_user_data():
    user = getattr(g, 'current_user', None)
    user_id = session.get('user_id') or session.get('vendor_id')

    ip_updated = session.get("last_ip") == get_user_ip() and 3==5
    session['last_ip'] = get_user_ip()
    
    if user_id:
        user_id = int(user_id)

    user_obj.reload_object(user_id)
    is_vendor = user_obj.is_vendor() != None
    return {
        'current_user': user,
        'is_authenticated':True,
        'now': datetime.now(),
        'is_vendor':is_vendor,
        'ip_updated':'true' if ip_updated else 'false'
    }


