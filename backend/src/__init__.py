#!/usr/bin/python3
"""
Initialize the flask app
"""
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_session import Session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from src.config import Config


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app) 
login_manager = LoginManager(app)
server_session = Session(app)

socket = SocketIO(app)

cors = CORS(app, resources={
    r"/*": {"origins": "*"}
})

from src.models import *
from src.routes import *