from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect
import re

csrf = CSRFProtect()

password_strength_checker_bp = Blueprint('password_strength_checker', __name__, url_prefix='/tools')

class PasswordStrengthForm(FlaskForm):
    password = PasswordField('Enter Password to Test', validators=[DataRequired()])
    submit = SubmitField('Check Strength')

def check_strength(password):
    length = len(password)
    lower = bool(re.search(r'[a-z]', password))
    upper = bool(re.search(r'[A-Z]', password))
    digit = bool(re.search(r'\d', password))
    symbol = bool(re.search(r'[!@#$%^&*()_\-+=\[\]{};:\'",.<>?\\|/~`]', password))
    score = sum([lower, upper, digit, symbol])

    if length < 8:
        return "Very Weak", "Password is too short. Minimum 8 characters recommended.", score
    elif score == 1:
        return "Weak", "Add uppercase, numbers, and symbols to strengthen.", score
    elif score == 2:
        return "Medium", "Try adding more character types and increasing length.", score
    elif score == 3:
        return "Strong", "Your password is quite strong. For best security, use all four types.", score
    else:
        return "Very Strong", "Excellent! Your password is highly secure.", score

@password_strength_checker_bp.route('/password-strength-checker', methods=['GET', 'POST'])
def password_strength_checker():
    form = PasswordStrengthForm()
    verdict, feedback, score = None, None, None
    if form.validate_on_submit():
        password = form.password.data
        verdict, feedback, score = check_strength(password)
    return render_template('tools/password_strength_checker.html', form=form, verdict=verdict, feedback=feedback, score=score)
