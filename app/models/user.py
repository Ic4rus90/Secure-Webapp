from sqlalchemy import Column, Integer, String
from flask_login import UserMixin
import bcrypt
from app.db.database import base


class User(UserMixin, base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String, unique=True)
    password = Column("password", String, nullable=True)
    phone = Column("phone", String)
    email = Column("email", String, unique=True)
    totp_secret = Column("totp_secret", String)
    is_oauth = Column("is_oauth", Integer, default=0)

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def __init__(self, username, password, phone, email, totp_secret=None, is_oauth=0):
        self.username = username
        self.set_password(password, is_oauth)
        self.phone = phone
        self.email = email
        self.totp_secret = totp_secret
        self.is_oauth = is_oauth

    def set_password(self, password, is_oath):
        """
        Hash the password with bcrypt
        """
        if is_oath == 0:
            self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        else:
            self.password = None

    def validate_password(self, password):
        """
        Validate the password with bcrypt
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def set_oauth(self, is_oauth):
        self.is_oauth = is_oauth

