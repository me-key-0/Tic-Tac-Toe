#!/usr/bin/python3
"""
Initialize the flask app
"""
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)

cors = CORS(app, resources={
    r"/*": {"origins": "*"}
})

from backend import models, routes