#!/usr/bin/python3
"""
Configurations for the flask app
"""
import os, redis


class Config:
    """Configuration class for the flask application"""
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", 'sqlite:///users.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

        
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")
