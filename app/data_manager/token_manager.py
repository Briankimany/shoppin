import secrets
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user_profile import ResetToken

class TokenGenerator:

    RESET_TOKEN_LENGTH = 32 
    SESSION_TOKEN_LENGTH = 64
    ALLOWED_CHARS = string.ascii_letters + string.digits + '_-'

    @staticmethod
    def generate_reset_token():
        """Generate cryptographically secure reset token (32 chars)"""
        return ''.join(secrets.choice(TokenGenerator.ALLOWED_CHARS) 
                      for _ in range(TokenGenerator.RESET_TOKEN_LENGTH))
    

    @staticmethod
    def get_expiration(hours=1):
        """Standardized expiration time"""
        return datetime.utcnow() + timedelta(hours=hours)
    

class ResetTokenManager:
    @staticmethod
    def create_token(db_session:Session ,session_token, user_id, expires_in_hours=1):
        """Creates a record complete token pair with expiration"""
        reset_token= ResetToken(
            session_token=session_token,
            reset_token=TokenGenerator.generate_reset_token(),
            user_id=user_id,
            expires_at=TokenGenerator.get_expiration(expires_in_hours)
        )
        db_session.add(reset_token)
        db_session.commit()
        return reset_token

    @staticmethod
    def verify_token(db_session:Session, reset_token):
        """Validates token existence and expiration"""
        token = db_session.query(ResetToken).filter_by(
            reset_token=reset_token
        ).first()
        
        if token and token.expires_at > datetime.utcnow():
            return token
        return None