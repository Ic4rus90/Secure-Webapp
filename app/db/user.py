from sqlite3 import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import session as db
from app.models.user import User
from sqlalchemy import update


def add_user(user: User):
    """
    Add a user to the database
    returns True if added, False if not
    """
    db.add(user)
    try:
        db.commit()
        added = True

    except:
        db.rollback()
        db.flush()
        added = False

    return added


def get_user(user_id):
    """
    Get a user from the database
    returns the user if found, None if not
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except:
        return None
    
def get_user_by_email(email):
    try:
        user = db.query(User).filter(User.email == email).first()
        return user
    except:
        return None


def get_username(username):
    """
    Get a user from the database
    returns the user if found, None if not
    """
    try:
        user = db.query(User).filter(User.username == username).first()
        return user
    except:
        return None


def change_username(new_username, user_id):
    """
    Change the username of a user
    returns True if changed, False if not
    """
    try:
        # Check if name is already taken
        name_in_use = db.query(User).filter(User.username == new_username).first()
        if name_in_use is not None:
            return False

        # Update username
        db.execute(update(User).where(User.id == user_id).values(
            username=new_username
        ))

        db.commit()
        return True
    except SQLAlchemyError as e:
        print(e)
        db.rollback()
        return False


def change_phone(new_phone, user_id):
    """
    Change the phone number of a user
    returns True if changed, False if not
    """
    try:
        # Check if phone number is already taken
        phone_in_use = db.query(User).filter(User.phone == new_phone).first()
        if phone_in_use is not None:
            return False

        # Update phone number
        db.execute(update(User).where(User.id == user_id).values(
            phone=new_phone
        ))

        db.commit()
        return True
    except SQLAlchemyError as e:
        print(e)
        db.rollback()
        return False


def change_password(new_password, user_id):
    """
    Change the password of a user
    returns True if changed, False if not
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        # Update password
        user.set_password(new_password, user.is_oauth)
        db.commit()
        return True

    except SQLAlchemyError as e:
        print(e)
        db.rollback()
        return False


