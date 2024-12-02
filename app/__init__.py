from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import Config, TestingConfig

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(config_name="default"):
    app = Flask(__name__)
    if config_name == 'testing':
        app.config.from_object(TestingConfig)
    else:
        # Load default or other configurations
        app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)  # Initialize Bcrypt with Flask app instance
    login_manager.init_app(app)

    from app.routes import main_routes, auth_routes, post_routes, like_routes, profile_routes, comment_routes
    app.register_blueprint(main_routes.main_bp)
    app.register_blueprint(auth_routes.auth_bp)
    app.register_blueprint(post_routes.post_bp)
    app.register_blueprint(comment_routes.comment_bp)
    app.register_blueprint(like_routes.like_bp)
    app.register_blueprint(profile_routes.profile_bp)

    # Define the user loader function inside `create_app` to avoid circular import
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User  # Import User model here to avoid circular import
        return User.query.get(int(user_id))  # Retrieve user from database by ID

    # Optional: Set the login view for redirecting unauthorized users
    login_manager.login_view = "auth.login"  # Change to your actual login route
    login_manager.login_message = "Please log in to access this page."

    return app
