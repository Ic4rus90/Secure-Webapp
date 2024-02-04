from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, PasswordField
from wtforms.validators import Length, DataRequired, EqualTo
from flask import flash

from app.db.user import get_username


"""
Contains forms related to authentication and user management
"""


class TOTPForm(FlaskForm):
    code = StringField('TOTP', validators=[DataRequired(), Length(max=20)])


class UserForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=1, max=20)])
    phone = StringField('Phone number', validators=[Length(min=8, max=15)])
    # TODO: add password requirements that adhere to safety standards! Both for register and edit
    password = StringField('Password', validators=[Length(min=8, max=40)])
    email = EmailField('Email', validators=[Length(min=8, max=40)])


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=20)])
    email = EmailField('Email', validators=[DataRequired()]) 
    phone = StringField('Phone', validators=[Length(max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=40)])
    password2 = PasswordField('Repeat Password', validators=[EqualTo('password'), Length(min=8, max=40)])

    def unique_username(self, username):
        user = get_username(username)
        if user is not None:
            flash('Please use another username', 'error')
            print(username)
            return user


class EditUsernameForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=20)])


class EditPhoneForm(FlaskForm):
    phone = StringField('Phone', validators=[DataRequired(), Length(min=8, max=15)])


class EditPasswordForm(FlaskForm):
    old_password = PasswordField('Old Password',
                                 validators=[DataRequired(), Length(min=8, max=40)])

    new_password = PasswordField('Password',
                                 validators=[DataRequired(), Length(min=8, max=40)])

    new_password2 = PasswordField('Repeat Password',
                                  validators=[DataRequired(), EqualTo('new_password'), Length(min=8, max=40)])


