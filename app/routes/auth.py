import secrets
from urllib.parse import urlencode
from flask import Request, abort, current_app, flash, Blueprint, redirect, render_template, session, url_for, request
from flask_login import current_user, login_required, logout_user, login_user
import requests
from sqlalchemy import select

from app.db.user import User, get_username, change_username, change_phone, change_password, get_user_by_email
import bleach
import pyotp
import qrcode
import io
import base64
import os

from app.db.user import add_user
from app.forms.auth_forms import RegistrationForm, TOTPForm, UserForm, EditUsernameForm, EditPhoneForm, EditPasswordForm
from app.utilities.limiter import limiter

auth_routes = Blueprint('auth', __name__)

Oauth2Config = {
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'userinfo': {
            'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'email': lambda json: json['email'],
        },
        'scopes': ['https://www.googleapis.com/auth/userinfo.email']
}


@auth_routes.route('/authorize/')
def authorize():
    if current_user.is_authenticated:
        return redirect(url_for('main.boat_screen'))

    # generate a secure string for the state parameter
    session['state'] = secrets.token_urlsafe(16)

    # create a query string with the required OAuth2 parameters
    query = urlencode({
        'client_id': os.getenv('CLIENT_ID'),
        'redirect_uri': url_for('auth.callback',
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(Oauth2Config['scopes']),
        'state': session['state'],
        'prompt': 'select_account',
    })

    # redirect the user to google authorization URL
    return redirect(Oauth2Config['authorize_url'] + '?' + query)


@auth_routes.route('/callback/')
def callback():
    if current_user.is_authenticated:
        return redirect(url_for('main.boat_screen'))
    
    # Matches the state parameteres
    if request.args['state'] != session.get('state'):
        abort(401)

    # exchange authorization code for access token
    response = requests.post(Oauth2Config['token_url'], data={
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('auth.callback', _external=True),
    }, headers={'Accept': 'application/json'})

    if response.status_code != 200:
        abort(401)
    token = response.json().get('access_token')
    if not token:
        abort(401)

    # Get the users email using the access token
    response = requests.get(Oauth2Config['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    email = Oauth2Config['userinfo']['email'](response.json())

    # Find the user in the db, alternatively create user
    user = get_user_by_email(email)
    if user is None:
        username = email.split('@')[0]
        user = User(username=username, password=None, phone=None, email=email, totp_secret=None, is_oauth=1)
        add_user(user)
    login_user(user)
    return redirect(url_for('main.boat_screen'))


# Error handler for too many requests
@auth_routes.errorhandler(429)
def rate_limit_exceeded(e):
    flash('Too many attempts. Please try again later.', 'error')
    form = UserForm()
    return render_template("login.html", form=form), 429


@auth_routes.route("/confirm-totp/", methods=['POST'])
def confirm_totp():
    """
    Log in the user if the TOTP code is correct
    """
    form = TOTPForm()
    if form.is_submitted():
        user = get_username(username=request.args.get('user_name'))
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(form.code.data):
            login_user(user=user)
            return redirect(url_for('main.boat_screen'))
        else:
            flash("Incorrect code", "error")
            return redirect(url_for('auth.login'))


@auth_routes.route("/totp/")
def totp_screen():
    form = TOTPForm()
    return render_template("confirm_totp.html", 
                           form=form, 
                           user_name=request.args.get('user_name'))       


@auth_routes.route("/login/", methods=['GET', 'POST'])
@limiter.limit("3 per 1 minute", methods=['POST'])
def login():
    """
    Send the user to TOTP screen if the username and password is correct
    Limiter is set to 3 attempts per 1 minute
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.boat_screen'))

    form = UserForm()
    if form.is_submitted():
        username = form.username.data.strip()
        bleached_username = bleach.clean(username, strip=True)
        password = form.password.data

        # Implemented rate-limiter. Commented out as Flask Limiter is active
        # if FailedLogin.number_of_recent_login_failures(bleached_username, minutes=1) >= 3:
            # flash("Too many failed login attempts, please try again later", "error")
            # return render_template("login.html", form=form)

        try:
            user = get_username(username=bleached_username)
            if user and user.validate_password(password) and user.is_oauth == 0:
                # login_user(user=user)
                # FailedLogin.clear_failed_attempts(bleached_username)
                return redirect(url_for('auth.totp_screen', user_name=bleached_username))
            else:
                # FailedLogin.add_failed_attempt(bleached_username)
                flash("Incorrect username or password", "error")
                return render_template("login.html", form=form)
        except Exception as e:
            flash("An error occurred. Please try again later.", "error")
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)


@auth_routes.route("/register/", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.boat_screen'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username is unique. If it is None, then the username is unique
        if form.unique_username(bleach.clean(form.username.data, strip=True)) is None:
            # Generate a TOTP secret
            totp_secret = pyotp.random_base32()
            user = User(username=bleach.clean(form.username.data, strip=True),
                        phone=bleach.clean(form.phone.data, strip=True),
                        password=bleach.clean(form.password.data, strip=True),
                        email=bleach.clean(form.email.data, strip=True),
                        totp_secret=totp_secret,
                        is_oauth=0
                        )
            try:
                add_user(user)
                # Generate QR code for the TOTP secret
                totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(name=user.username,
                                                                         issuer_name="IKT222")
                qr_img = qrcode.make(totp_uri)
                # Convert QR code to a data URI
                img_byte_arr = io.BytesIO()
                qr_img.save(img_byte_arr)
                img_byte_arr = img_byte_arr.getvalue()
                qr_data_uri = "data:image/png;base64," + base64.b64encode(img_byte_arr).decode()

            except Exception as e:
                print(e)
                return render_template('register.html', form=form)

            # Redirect to a new template to display QR code or pass the QR code data URI to the template
            return render_template('display_qr.html', qr_data_uri=qr_data_uri)
    return render_template("register.html", form=form)


@auth_routes.route("/edit-username/", methods=['POST'])
@login_required
def edit_username():
    username_form = EditUsernameForm()
    phone_form = EditPhoneForm()
    password_form = EditPasswordForm()

    if username_form.validate_on_submit():
        new_username = bleach.clean(username_form.username.data, strip=True)
        result = change_username(new_username, current_user.id)
        if result:
            flash("Username changed", "success")
        else:
            flash("Username taken, please try choose another", "error")

    return render_template("edit_profile.html", username_form=username_form, phone_form=phone_form,
                           password_form=password_form, user=current_user)


@auth_routes.route("/edit-phone/", methods=['POST'])
@login_required
def edit_phone():
    username_form = EditUsernameForm()
    phone_form = EditPhoneForm()
    password_form = EditPasswordForm()

    if phone_form.validate_on_submit():
        new_phone = bleach.clean(phone_form.phone.data, strip=True)
        result = change_phone(new_phone, current_user.id)
        if result:
            flash("Phone number changed!", "success")
        else:
            flash("Phone number already in use!", "error")

    return render_template("edit_profile.html", username_form=username_form, phone_form=phone_form,
                           password_form=password_form, user=current_user)


@auth_routes.route("/edit-password/", methods=['POST'])
@login_required
def edit_password():
    password_form = EditPasswordForm()

    if password_form.validate_on_submit():
        old_password = password_form.old_password.data
        new_password_1 = password_form.new_password.data

        if current_user.validate_password(old_password):


            if change_password(new_password_1, current_user.id):
                flash("Password changed!", "success")
                return redirect(url_for('main.edit_profile'))

            else:
                flash("Password change failed!", "error")

        else:
            flash("Incorrect password!", "error")

    else:
        flash("Passwords do not match!", "error")

    username_form = EditUsernameForm()
    phone_form = EditPhoneForm()

    return render_template("edit_profile.html",
                           username_form=username_form,
                           phone_form=phone_form,
                           password_form=password_form,
                           user=current_user)


@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect('/')