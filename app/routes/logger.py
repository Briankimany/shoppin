import logging
from pathlib import Path



class LoggerManager:
    def __init__(self, log_file="app.log", log_level=logging.DEBUG, logger_name=None):
        self.logger = logging.getLogger(logger_name)  # Use a unique logger name
        self.logger.setLevel(log_level)

        if not self.logger.handlers:  # Prevent duplicate handlers
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
    ADMIN_LOGGER = LoggerManager(parent_dir/"admin.logs", logger_name="PAYMENT").get_logger()
