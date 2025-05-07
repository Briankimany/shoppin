
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager

from config.config import JSONConfig
from app.routes.logger import LOG
from typing import Callable


config = JSONConfig("config.json")
engine = create_engine(f"sqlite:///{config.database_url.absolute()}")
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope(commit=False , raise_exception=True , logger = LOG.DB,func:Callable=None):
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
       

