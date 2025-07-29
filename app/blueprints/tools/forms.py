from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, URL

class URLForm(FlaskForm):
    url = StringField("Website URL", validators=[DataRequired(), URL()])
