from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)

app.config['SECRET_KEY'] = 'bf63738e2959ffe0adc8db1a8ece15d5'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orion.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'É necessário estar logado para acessar esta página'
login_manager.login_message_category = 'alert-info'

from orion import routes