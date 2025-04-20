
from flask import session , redirect , url_for

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from functools import wraps

from app.data_manager.session_manager import SessionManager
from config.config import JSONConfig
from app.data_manager.users_manager import UserManager
from app.routes.logger import LOG

config = JSONConfig('config.json')
engine = create_engine(f"sqlite:///{config.database_url.absolute()}")
Session = sessionmaker(bind=engine)
db_session = Session()
session_manager = SessionManager(db_session)
user_obj = UserManager(db_session , user=None)


def get_or_create_session():
    """Ensures a session token exists in the user's session."""
    try:
        if "session_token" not in session or not session_manager.verify_session_token(session["session_token"]):
            session["session_token"] = session_manager.create_new_session()

        if "user_id" in session:
            user_obj.session_tkn = session.get("session_token")
            user_obj.reload_object(session["user_id"])
       
            user_obj.self_update_session(data={"user_id": user_obj.user.id})
      
        LOG.MAIN_LOGGER.info(f" from routes utils Session initialized. User ID: {session.get('user_id')}")
        return session["session_token"]

    except Exception as e:
        LOG.MAIN_LOGGER.error(f"Error in get_or_create_session: {e}")
        return None 
    

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



