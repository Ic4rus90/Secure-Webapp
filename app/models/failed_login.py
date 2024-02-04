from sqlalchemy import Column, Integer, String, DateTime, func, and_
from app.db.database import base, session as db

from datetime import datetime, timedelta, timezone


class FailedLogin(base):
    __tablename__ = "failed_logins"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", String)
    timestamp = Column(DateTime(timezone=True), default=func.now())

    def __init__(self, username):
        self.username = username

    @staticmethod
    def add_failed_attempt(username):
        """
        Add a failed login attempt to the database
        """
        new_entry = FailedLogin(username)
        db.add(new_entry)
        db.commit()

    @staticmethod
    def clear_failed_attempts(username):
        """
        Clear all failed login attempts for a user
        """
        db.query(FailedLogin).filter(FailedLogin.username == username).delete()
        db.commit()

    @staticmethod
    def number_of_recent_login_failures(username, minutes=5):
        """
        Get the number of failed login attempts for a user in the last x minutes
        """
        start_time = datetime.now(tz=timezone.utc) - timedelta(minutes=minutes)
        # Return the number of failed login attempts related to a specific user in the last x minutes
        return db.query(FailedLogin).filter(and_(FailedLogin.username == username, FailedLogin.timestamp > start_time)).count()


