from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class AdminSettingForm(FlaskForm):
    key = StringField("Setting Key", validators=[DataRequired()])
    value = StringField("Setting Value", validators=[DataRequired()])
    submit = SubmitField("Save Setting")
