from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail

db = SQLAlchemy()
oauth = OAuth()
login_manager = LoginManager()
login_manager.login_view = "users.login"
mail = Mail()
