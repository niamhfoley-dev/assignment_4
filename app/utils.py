from flask import Blueprint, current_app
from app import db

like_bp = Blueprint('like', __name__)


# Helper functions to handle adding and removing likes
def add_like(user, model, like_model, model_id):
    """Helper function to add a like to a model (Post or Comment)."""
    try:
        # Check if the like already exists
        existing_like = like_model.query.filter_by(user_id=user.id, **{f"{model.__name__.lower()}_id": model_id}).first()
        if existing_like:
            return False  # Already liked

        # Add a new like entry
        like = like_model(user_id=user.id, **{f"{model.__name__.lower()}_id": model_id})
        db.session.add(like)
        db.session.commit()
        return True

    except Exception as e:
        current_app.logger.error(f"Error adding like to {model.__name__} {model_id}: {e}")
        return False


def remove_like(user, like_model, model_id):
    """Helper function to remove a like from a model (Post or Comment)."""
    try:
        # Find the like entry to delete
        like = like_model.query.filter_by(user_id=user.id, **{f"{like_model.__name__.replace('Like', '').lower()}_id": model_id}).first()
        if like:
            db.session.delete(like)
            db.session.commit()
            return True
        return False

    except Exception as e:
        current_app.logger.error(f"Error removing like from {like_model.__name__} {model_id}: {e}")
        return False
