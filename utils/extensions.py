from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
login_manager = LoginManager()
login_manager.login_view = "users.login"
mail = Mail()
