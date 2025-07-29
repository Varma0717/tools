from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
oauth = OAuth()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
mail = Mail()
migrate = Migrate()
csrf = CSRFProtect()
