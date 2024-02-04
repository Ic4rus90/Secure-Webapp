from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.db.database import base

class Review(base):
    __tablename__="posts"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    boat_id = Column("boat_id", Integer, ForeignKey("boats.id"))
    username = Column("username", String, ForeignKey("users.username"))
    stars = Column("stars", String)
    content = Column("content", String)
    timestamp = Column(DateTime(timezone=True), default=func.now())

    def __init__(self, boat_id, username, stars, content):
        self.boat_id = boat_id
        self.username = username
        self.stars = stars
        self.content = content
