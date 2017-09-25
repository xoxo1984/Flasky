from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField, TextAreaField, Field
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

# class RegistrationForm(Form):
#     email = StringField('Email',validators=[Required(),Length(1,64),Email()])
#     username = StringField('Username',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Username must have only....')])
#     password = PasswordField('Password',validators=[Required(),EqualTo('password2',message='Password not match')])
#     password2 = PasswordField('Confirm Password',validators=[Required()])
#     submit = SubmitField('Register')
#
#     def validate_email(self,field):
#         if User.query.filter_by(email=field.data).first():
#             raise ValidationError('Email already exist')
#
#     def validate_username(self,field):
#         if User.query.filter_by(username=field.data).first():
#             raise ValidationError('Username already in use')


class UpdatePasswordForm(Form):
    old_password = PasswordField('Old Password', validators=[Required()])
    new_password = PasswordField('New Password', validators=[Required()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[Required()])
    submit = SubmitField('Update')

