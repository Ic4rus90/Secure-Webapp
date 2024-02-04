from app.db.database import session as db
from app.models.review import Review


def add_review_to_db(post: Review):
    """
    Add a review to the database
    returns True if added, False if not
    """
    db.add(post)
    try:
        db.commit()
        added = True

    except:
        db.rollback()
        db.flush()
        added = False

    return added


def get_reviews():
    """
    Get all the reviews from the database
    Returns: List of reviews
    """
    try:
        review = db.query(Review.id, Review.stars, Review.content, Review.timestamp).all()
        return review
    except:
        return None


def get_boat_reviews(boat_id):
    """
    Get all the reviews for a specific boat from the database
    Returns: List of reviews for the boat
    """
    try:
        reviews = db.query(Review).filter(Review.boat_id == boat_id).all()
        return reviews
    except:
        return None

