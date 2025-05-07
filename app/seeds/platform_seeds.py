
from app.data_manager.scoped_session import session_scope
from app.routes.logger import LOG
from app.data_manager.users_manager import UserManager
import os 
from dotenv import set_key ,load_dotenv

load_dotenv()

def get_platform_id():
    with session_scope(commit=True,logger=LOG.ADMIN_LOGGER) as db_session:
        PLATFORM_NAME = os.getenv("PLATFORM_NAME")

        assert PLATFORM_NAME != None 
     
        user = UserManager.get_user_(db_session=db_session,
                                     user=PLATFORM_NAME)
        assert user !=None
        print(user.is_admin)
        assert user.is_admin

        if not user.activated:
            print("Adming account is not activated")
        return user.id 
        
def create_platform_account():
    PLATFORM_NAME = os.getenv("PLATFORM_NAME")
    name = input('Enter username: ') or PLATFORM_NAME
    print(f"Plaform name is {PLATFORM_NAME} :NAME {name}")
    assert name !=None
    set_key('.env','PLATFORM_NAME' ,name)
    first_name = input("Enter first name: ") or 'platform'
    second_name = input("Enter second name: ") or 'second'
    email = input("Email: ") or 'second'
    phone = input("Phone: ") or 'second'
    password = input("Password: ") or 'second'

    assert all([name.strip(),
                first_name.strip(),
                email.strip(),
                phone.strip(),
                password.strip()])
    data = {
        "name":name,
        "first_name":first_name,
        "second_name":second_name,
        "email":email,
        "phone":phone,
        "password_hash":password
    }

    with session_scope(commit=True,logger=LOG.ADMIN_LOGGER) as db_session:
        user = UserManager.register_user(
            db_session=db_session,
            user_details=data,
            level=1
        )
        print("Proced to the login page for email verification")

def main():
    try:
        get_platform_id()
    except Exception as e:
        create_platform_account()

if __name__ == "__main__":
    main()
