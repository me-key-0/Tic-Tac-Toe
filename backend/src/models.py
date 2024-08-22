#!/usr/bin/python3
"""
Contains the models of the application.
"""
import enum
import secrets
from datetime import datetime

from src import db


class BaseModel():
    """Base class for other models"""
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def to_dict(self):
        return self.__dict__

class Association(db.Model, BaseModel):
    """Association table between players and games"""
    __tablename__ = "game_players"
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"))
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    player = db.relationship("Player", backref="played_games")
    game = db.relationship("Game", backref="game_players")


class Player(db.Model, BaseModel):
    """Model for the game players"""
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False)
    playing = db.Column(db.Boolean, default=False) # This would come in handy if we choose to prohibit a user playing multiple games simultaneously
    score = db.Column(db.Integer, default=0)
    moves = db.relationship("Move", backref="player",
                            cascade="all, delete, delete-orphan")


class Game(db.Model, BaseModel):
    """Model for the tic-tac-toe game"""
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(10), unique=True)
    difficulty = db.Column(db.Integer, default=0)
    finished = db.Column(db.Boolean, default=False)
    moves = db.relationship("Move", backref="game",
                            cascade="all, delete, delete-orphan")


class Move(db.Model, BaseModel):
    """Model for a single move in a game"""
    __tablename__ = "moves"
    id = db.Column(db.Integer, primary_key=True)
    tile_number = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
