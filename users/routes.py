from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from users.forms import LoginForm, ProfileForm
from users.models.user import User
from users.models.order import Order
from users.models.download import Download
from admin.models import Setting
from utils.extensions import db
from utils.payment import create_order
from flask_dance.contrib.google import google


users_bp = Blueprint('users', __name__, url_prefix='/users')



    
# ------------------------------
# ✅ LOGIN
@users_bp.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    if current_user.is_authenticated:
        # Already logged in users go to correct dashboard
        return redirect(url_for('users.account' if current_user.role == 'customer' else 'admin.panel'))

    form = LoginForm()
    error = None

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful ✅", "success")
            if user.role == "customer":
                return redirect(url_for('users.account'))
            else:
                return redirect(url_for('admin.panel'))
        else:
            error = "Invalid username or password."
            flash(error, "danger")

    return render_template('users/login.html', form=form, error=error)
    
    


@users_bp.route("/login/success")
def login_success():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    userinfo = resp.json()

    email = userinfo["email"]
    name = userinfo.get("name", email.split("@")[0])

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            username=name,
            password="oauth_google",  # dummy
            role="customer"
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for("users.account"))



# ------------------------------
# ✅ REGISTER
@users_bp.route('/register', methods=['GET', 'POST'], endpoint='register')
def register():
    recaptcha_site_key = Setting.query.filter_by(key='recaptcha_site_key').first()

    if request.method == 'POST':
        # Basic validations...
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('users.register'))

        # ✅ reCAPTCHA server-side verification
        recaptcha_response = request.form.get('g-recaptcha-response')
        secret_key = Setting.query.filter_by(key='recaptcha_secret_key').first()
        if secret_key:
            recaptcha_verify = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': secret_key.value,
                    'response': recaptcha_response
                }
            )
            result = recaptcha_verify.json()
            if not result.get('success'):
                flash("reCAPTCHA verification failed. Please try again.", "danger")
                return redirect(url_for('users.register'))

        # Continue registration (check existing user, hash password, etc.)
        # ...

        flash("Registration successful", "success")
        return redirect(url_for('users.login'))

    return render_template(
        'users/register.html',
        recaptcha_site_key=recaptcha_site_key.value if recaptcha_site_key else None
    )


# ------------------------------
# ✅ MAIN CUSTOMER ACCOUNT PAGE (WooCommerce-style layout)
@users_bp.route('/account')
@login_required
def account():
    if current_user.role != 'customer':
        return redirect(url_for('admin.settings'))
    return render_template('users/account.html')

# ------------------------------
# ✅ AJAX PARTIAL LOADS (WooCommerce Tabs)
@users_bp.route('/account/<section>')
@login_required
def account_section(section):
    if current_user.role != 'customer':
        return redirect(url_for('admin.settings'))

    section_map = {
        'overview': 'users/sections/overview.html',
        'orders': 'users/sections/orders.html',
        'downloads': 'users/sections/downloads.html',
        'profile': 'users/sections/profile.html',
        'logout': None
    }

    template = section_map.get(section)

    if not template and section != 'logout':
        return "Section not found", 404

    if section == 'orders':
        orders = current_user.orders
        return render_template(template, user=current_user, orders=orders)

    elif section == 'downloads':
        downloads = current_user.downloads
        return render_template(template, user=current_user, downloads=downloads)

    elif section == 'profile':
        from users.forms import ProfileForm
        form = ProfileForm(obj=current_user)
        return render_template(template, user=current_user, form=form)

    elif section == 'logout':
        return redirect(url_for('users.logout'))

    return render_template(template, user=current_user)

# ------------------------------
# ✅ PROFILE UPDATE POST AJAX
@users_bp.route('/account/profile', methods=['POST'])
@login_required
def save_profile():
    from users.forms import ProfileForm
    form = ProfileForm()

    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()
        return render_template('users/sections/profile.html', form=form)

    return render_template('users/sections/profile.html', form=form), 400


# ------------------------------
# ✅ LOGOUT
@users_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('users.login'))

# ------------------------------
# ✅ PREMIUM UPGRADE PAGE
@users_bp.route('/upgrade')
@login_required
def upgrade():
    return render_template('users/upgrade.html')

# ------------------------------
# ✅ PAYMENT HANDLING
@users_bp.route('/payment', methods=['POST'])
@login_required
def payment():
    amount = int(request.form.get("amount", 0))
    try:
        order = create_order(amount)
        current_user.is_premium = True
        db.session.commit()
        flash("Payment successful! You are now a premium user.", "success")
    except Exception as e:
        flash(f"Payment failed: {str(e)}", "danger")
    return redirect(url_for('users.account'))
