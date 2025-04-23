import secrets
import string
from datetime import datetime, timedelta ,timezone
from sqlalchemy.orm import Session
from app.models.user_profile import ResetToken ,AccountActivation ,UserProfile
from app.data_manager.client_access_manager import session_scope
from app.routes.logger import LOG

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
        return datetime.now(timezone.utc) + timedelta(hours=hours)
    

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

class AcctivationTokenManager(TokenGenerator):

    @classmethod
    def create_account_activation(cls ,expire_after,session_token:str ,user_id:int):
        token = cls.generate_reset_token()

        activation = AccountActivation()
        activation.expires_at = cls.get_expiration(hours=expire_after) 
        activation.token = token
        activation.session_token = session_token
        activation.user_id = user_id

        with session_scope(commit=True ,
                            raise_exception=True ,
                            logger=LOG.USER_LOGGER,
                           func=cls.create_account_activation) as db_session:
            db_session.add(activation)

        return token
    
    @classmethod
    def verify_account_token(cls,token):
        with session_scope(
                logger=LOG.USER_LOGGER,
                func=cls.verify_account_token,
                commit = True
            ) as db_session:
            
           
            LOG.USER_LOGGER.debug(f"[ACC-VERIFICATION] initiating verification for tkn: {token}")

            activation_token = db_session.query(AccountActivation).filter(
                AccountActivation.token == token,
                AccountActivation.expires_at >datetime.now(timezone.utc)
            ).first()

            if activation_token:
                user_id = db_session.query(AccountActivation).filter(AccountActivation.token == token).first().user_id
                user = db_session.query(UserProfile).filter(UserProfile.id == user_id)

                user = db_session.query(UserProfile).join(
                    AccountActivation , UserProfile.id == AccountActivation.user_id
                ).filter(AccountActivation.token == token).first()
                
                LOG.USER_LOGGER.debug(f"Activating account: {user}")
                if not user:
                    raise Exception("error cant find the user ")
                user.activated = True

            LOG.USER_LOGGER.debug(f"Account verified :{activation_token!=None}")
            
            return activation_token !=None
                
    
        
    