
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager

from app.models.client_access_history import  ClientAccessLog
from config.config import JSONConfig
from app.routes.logger import LOG
from typing import Callable

config = JSONConfig("config.json")
engine = create_engine(f"sqlite:///{config.database_url.absolute()}")
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope(commit=False , raise_exception=True , logger = LOG.MAIN_LOGGER,func:Callable=None):
    session = Session()
    try:
        yield session
        session.commit() if commit else None
    except Exception as e:
        msg = f"Error in scoped session {e}"
        if func:
            msg = f"error in {func.__name__} using scoped session {e}"
        logger.error(msg)
        session.rollback()
        if raise_exception:
            raise Exception(e)
    finally:
        session.close()
       


class ClientAccessManager:
    @staticmethod
    def log_access(data: dict):
        with session_scope(True) as db:
            log = ClientAccessLog(**data)
            db.add(log)

    @staticmethod
    def get_by_ip(ip: str):
        with session_scope() as db:
            access_logs= db.query(ClientAccessLog).filter_by(ip_address=ip).first()
            return access_logs.to_dict() if access_logs else None

    @staticmethod
    def get_recent(limit: int = 10):
        with session_scope() as db:
            access_logs= db.query(ClientAccessLog).order_by(ClientAccessLog.accessed_at.desc()).limit(limit).all()
            return [i.to_dict() for i in access_logs]

    @staticmethod
    def delete_by_id(log_id: int):
        with session_scope(True) as db:
            record = db.query(ClientAccessLog).filter_by(id=log_id).first()
            if record:
                db.delete(record)
