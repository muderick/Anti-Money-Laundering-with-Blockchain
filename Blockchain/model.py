from datetime import datetime
from xml.dom.minicompat import NodeList
from Blockchain import db, login_manager
import pytz
import json
from hashlib import sha256
import  os
import requests
from time import time
from flask import current_app
from flask_login import UserMixin
import jwt


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Float(50), nullable=False, default=1000.00)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Africa/Nairobi')))
    transactions = db.relationship('Transactions', backref='current', lazy=True)

    def __repr__(self):
        return f"Users('{self.username}', '{self.user_id}', '{self.email}','{self.image_file}','{self.balance}')"

    def get_id(self):
        return self.user_id
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def get_reset_token(self, expires=500):
        return jwt.encode({'reset_password': self.username, 'exp': time() + expires},
                           key=os.getenv('SECRET_KEY_FLASK'))

    @staticmethod
    def verify_reset_token(token):
        try:
            username = jwt.decode(token, key=os.getenv('SECRET_KEY_FLASK'))['reset_password']
            print(username)
        except Exception as e:
            print(e)
            return
        return Users.query.filter_by(username=username).first()
   

    @staticmethod
    def verify_email(email):

        user = Users.query.filter_by(email=email).first()

        return user

class Bminers(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    miner_name = db.Column(db.String(50), unique=True, nullable=False)
    ip_address = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Bminers('{self.email}', '{self.ip_address}', '{self.phone_number}')"


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.String, nullable=False)
    recipient = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    proof = db.Column(db.Integer, nullable=True)
    hash = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.String, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"Transactions('{self.sender}', '{self.recipient}', '{self.amount}')"
