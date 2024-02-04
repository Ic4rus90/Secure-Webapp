from app.db.database import session as db
from app.models.boat import Boat


def add_boat_to_db(boat: Boat):
    """
    Add a boat to the database
    """
    db.add(boat)
    try:
        db.commit()
        added = True

    except:
        db.rollback()
        db.flush()
        added = False
    return added


def get_boats():
    """
    Get all the boats from the database
    Returns: List of boats
    """
    try:
        boats = db.query(Boat.id, Boat.type, Boat.make, Boat.foot, Boat.year, Boat.engineMake, Boat.engineHp,
                         Boat.price, Boat.description, Boat.image_url).all()
        return boats
    except:
        return None


def get_boat_by_id(boat_id):
    """
    Get a boat by id
    """
    try:
        boat = db.query(Boat).filter(Boat.id == boat_id).first()
        return boat
    except:
        return None
