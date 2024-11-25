class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://my_flask_user:my_secure_password@localhost:5433/my_flask_app"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    FLASK_DEBUG = 1
    DEBUG = True

