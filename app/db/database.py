from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base


engine = create_engine("sqlite:///shop.db?check_same_thread=False")
base = declarative_base()

session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def init_db():
    from app.models.boat import Boat
    from app.models.review import Review
    from app.models.user import User
    from app.models.failed_login import FailedLogin
    base.metadata.create_all(bind=engine)

