from utils.extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    role = db.Column(db.String(10), default='customer')
    is_premium = db.Column(db.Boolean, default=False)

    # Profile fields
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100))

    # Relationships (if tables exist)
    orders = db.relationship('Order', backref='user', lazy=True)
    downloads = db.relationship('Download', backref='user', lazy=True)

    def is_admin(self):
        return self.role == 'admin'

    def is_customer(self):
        return self.role == 'customer'
