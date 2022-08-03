from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import os

app = Flask(__name__, static_url_path='/static')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECURITY_PASSWORD_SALT'] = 'mumia@1999'
app.config['SECRET_KEY'] = '1234'
app.config['DEBUG'] = False
app.config['BCRYPT_LOG_ROUNDS'] = 13
app.config['WTF_CSRF_ENABLED'] = True
app.config['DEBUG_TB_ENABLED'] = False
app.config['DEBUG_TB_INTECEPT_REDIRECTS'] = False

#Mail settings
app.config['MAIL_SERVER'] = 'smtp.email.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

#Gmail authentication
app.config['MAIL_DEFAULT_SENDER'] = 'mumiaderick@gmail.com'
app.url_map.strict_slashes = False
login_manager = LoginManager(app)
mail = Mail(app)
print (os.environ.get("EMAIL_USER"))
# login_manager.login_view = 'login'

db = SQLAlchemy(app)
bcrypt = Bcrypt()
from Blockchain import bchain
