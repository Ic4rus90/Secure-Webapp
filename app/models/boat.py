from sqlalchemy import Column, Integer, String, Float
from app.db.database import base


class Boat(base):
    __tablename__ = "boats"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    type = Column("type", String)
    make = Column("make", String)
    foot = Column("foot", Integer)
    year = Column("year", Integer)
    engineMake = Column("eMake", String)
    engineHp = Column("eHp", Integer)
    price = Column("price", Float)
    description = Column("description", String)
    image_url = Column("image", String)

