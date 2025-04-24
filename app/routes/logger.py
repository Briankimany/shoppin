import logging
from pathlib import Path
from functools import wraps
from flask import jsonify ,render_template,session
import os
from uuid import uuid4
from dotenv import load_dotenv
from config.envrion_variables import IN_DEVELOPMENT

load_dotenv()

class LoggerManager:
    def __init__(self, log_file="app.log", log_level=logging.DEBUG, logger_name=None):
        self.logger = logging.getLogger(logger_name)  
        self.logger.setLevel(log_level)

    
        file_handler = logging.FileHandler(log_file)  
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

class LOG:
    parent_dir = Path().cwd() / "LOGS"
    parent_dir.mkdir(parents=True , exist_ok= True)

    USER_LOGGER = LoggerManager(parent_dir/"user_bp.logs", logger_name="USER").get_logger()
    MAIN_LOGGER = LoggerManager(parent_dir/"main_bp.logs", logger_name="MAIN").get_logger()
    SHOP_LOGGER = LoggerManager(parent_dir/"shop_bp.logs", logger_name="SHOP").get_logger()
    VENDOR_LOGGER = LoggerManager(parent_dir/"vendor_bp.logs", logger_name="VENDOR").get_logger()
    ORDER_LOGGER = LoggerManager(parent_dir/"order.logs", logger_name="ORDER").get_logger()
    PAYMENT_LOGGER = LoggerManager(parent_dir/"payment.logs", logger_name="PAYMENT").get_logger()
    ADMIN_LOGGER = LoggerManager(parent_dir/"admin.logs", logger_name="ADMIN").get_logger()
    IP_BP  = LoggerManager(parent_dir/"ip-address_logs.log" ,logger_name='IPS').get_logger()
    MAIL_LOGGER =  LoggerManager(parent_dir/"emails.log" ,logger_name='MAIL').get_logger()
    SESSIONS_LOGGER = LoggerManager(parent_dir/"sessions.log" ,logger_name='SESSION').get_logger()


def bp_error_logger(logger:LOG, status_code=400 ,return_template = None ,raise_exeption=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_key = f"{func.__name__}_{str(e)}"
                if 'TEMP_ERROR_DICT' not in session:
                    session['TEMP_ERROR_DICT'] ={}
                if error_key not in session['TEMP_ERROR_DICT'] :
                    error_id = str(uuid4()) 
                    session['TEMP_ERROR_DICT'][error_key] = error_id
                else:
                    error_id = session['TEMP_ERROR_DICT'][error_key]
               
                error_message = f"Error in {func.__name__}: id=({error_id}) {str(e.args)} :args={args} ,kwargs={kwargs}"
                logger.error(error_message)

                if raise_exeption:
                    raise Exception(e)

                if return_template:
                    message = str(e) if IN_DEVELOPMENT else None
                    return render_template(return_template,message = message ,error_id = error_id)
                
                message = f"ERROR {e} " if IN_DEVELOPMENT else "Contact support"
                
                return jsonify({
                    "status": "error",
                    "message": message,
                    "code": status_code
                }), status_code
            
        return wrapper
    return decorator