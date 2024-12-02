import os  # Importing the 'os' module to access environment variables.

# Base configuration class for the application.
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Secret key for session security, fetched from environment variables.
    DB_USER = os.environ.get('DB_USER')  # Database username, fetched from environment variables.
    DB_PASSWORD = os.environ.get('DB_PASSWORD')  # Database password, fetched from environment variables.
    DB_NAME = os.environ.get('DB_NAME')  # Database name, fetched from environment variables.
    DB_HOST = os.environ.get('DB_HOST')  # Database host (e.g., localhost or IP), fetched from environment variables.
    SQLALCHEMY_DATABASE_URI = (  # Connection string for SQLAlchemy to connect to the PostgreSQL database.
        F"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disables SQLAlchemy's event system to save resources.
    TEMPLATES_AUTO_RELOAD = True  # Ensures templates are auto-reloaded during development.
    FLASK_DEBUG = 1  # Enables Flask's debugging mode (useful for development).
    DEBUG = True  # Enables general debug mode in the application.

# Configuration class specifically for testing environments.
class TestingConfig:
    TESTING = True  # Activates testing mode, which adjusts app behavior for tests.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Uses an in-memory SQLite database for fast, isolated testing.
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disables SQLAlchemy's event system (not needed for testing).
    WTF_CSRF_ENABLED = False  # Disables CSRF protection for testing forms (simplifies testing).
    SECRET_KEY = 'test_secret_key'  # Static secret key used during testing (not fetched from environment variables).
