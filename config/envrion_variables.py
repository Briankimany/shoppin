
from config.config import JSONConfig
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker


IN_DEVELOPMENT  = True


config = JSONConfig('config.json')
engine = create_engine(f"sqlite:///{config.database_url.absolute()}")
Session = sessionmaker(bind=engine)


class StatusCodes:
    WAITING = ["TP101", "TP102", "TF104", "TR109"]

    CANCELED = ["TF10"]

    SUCCESS = ["TS100" ,'TF103']

    CONTACT_ADMIN = ["TP105", "TC108", "TF106"]



class StatusNames:
    PENDING = "pending"
    FAILED = "failed"
    COMPLETED = "completed"
    CONTACT_ADMIN = "Contact admin"


