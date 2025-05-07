
from app.models.client_access_history import  ClientAccessLog
from .scoped_session import session_scope

       
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
