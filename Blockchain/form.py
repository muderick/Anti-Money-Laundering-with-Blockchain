from ipaddress import ip_address
from flask import flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, BooleanField, SubmitField, PasswordField, IntegerField, FileField, URLField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, NumberRange
from Blockchain.model import Users, Bminers
from Blockchain.model import *
from flask_login import current_user
from Blockchain import Bcrypt


class UsersForm(FlaskForm):
    username = StringField('User Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            flash('That Email is taken.\nTry using another email.', 'info')
            raise ValidationError('Email already taken.\nTry using another email.')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already in use.')
        
    def validate_pass(self, password, confirm_password):
        if password != confirm_password:
            flash('Enter the same password twice', 'info')
            raise ValidationError('Password doesnt match')


class NewTransactionForm(FlaskForm):
    recipient = StringField('Reciever Mail', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired(), NumberRange(min=0, message='Must enter a number greater than 0')])
    submit = SubmitField('Submit')

    
class RegisterNodesForm(FlaskForm):
    ip_address = URLField('Node IPs', validators=[DataRequired()])
    miner_name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_ip(self, username):
        user = Bminers.query.filter_by(ip_address=ip_address.data).first()
        if user:
            raise ValidationError('Opps Ip already exists')
            flash('Ip address already exists', 'info')
        else:
            raise ValidationError('Registered Successfully')
            flash('Ip address registered successfully', 'info')

class LoginForm(FlaskForm):
    """
    login.html
    """
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
    
    # def validate_password(self, password):
    #     if bcrypt.check_password_hash(password, password.data):
    #         flash('Password incorrect', 'error')
    #         raise ValidationError('Password incorrect')


class UpdateProfileForm(FlaskForm):
    """
    profile.html
    """
    username = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Upload Image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_full_name(self, username):
        """
        checks for duplicate
        :param username:
        """
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                flash('That name is taken.', 'danger')
                raise ValidationError('That Email is taken.\n Choose another name or email.')

    def validate_email(self, email):
        """
        checks for duplicate
        :param email:
        """
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                flash('That Email is taken. Try another one.', 'danger')
                raise ValidationError('That Email is taken.\nTry using another email.')
            
    def validate_username(self, username):
        """
        checks for duplicate
        :param email:
        """
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                flash('That Username is taken. Try another one.', 'danger')
                raise ValidationError('That Username is taken.\nTry using another name.')
