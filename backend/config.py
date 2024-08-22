#!/usr/bin/python3
"""
Configurations for the flask app
"""
import os


class Config:
    """Configuration class for the flask application"""
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "TODO")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
