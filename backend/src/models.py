#!/usr/bin/python3
"""
Contains the models of the application.
"""
import string
import random, uuid
from datetime import datetime
from flask_login import UserMixin

from src import db


class BaseModel():
    """Base class for other models"""
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        """Formal representation of an instance"""
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(["{}={}".format(key, val) for key, val in self.to_dict().items()])
            )

class GamePlayerAssociation(db.Model):
    """Association table between players and games"""
    __tablename__ = "game_players"
    player_id = db.Column(db.String(36), db.ForeignKey("players.id"), primary_key=True, nullable=True)
    game_id = db.Column(db.String(36), db.ForeignKey("games.id"), primary_key=True)
    player = db.relationship("Player", backref="played_games")
    game = db.relationship("Game", backref="game_players")


class Player(BaseModel, db.Model, UserMixin):
    """Model for the game players"""
    __tablename__ = "players"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    playing = db.Column(db.Boolean, default=False) # This would come in handy if we choose to prohibit a user playing multiple games simultaneously
    score = db.Column(db.Integer, default=0)
    won_games = db.relationship("Game", backref="winner")
    moves = db.relationship("Move", backref="moving_player")
    messages = db.relationship("Message", backref="messaging_player")

    def to_dict(self):
        """Dictionary representation"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "playing": self.playing,
            "score": self.score,
        }

    def create_game(self, difficulty):
        """Creates a new game of given difficulty and returns the instance"""
        new_game = Game()
        new_game.difficulty = difficulty
        db.session.add(new_game)
        db.session.commit()

        gp_assoc = GamePlayerAssociation()
        gp_assoc.player_id = self.id
        gp_assoc.game_id = new_game.id
        db.session.add(gp_assoc)
        db.session.commit()

        return new_game

    def join_game_with_code(self, code):
        """Joins an existing game with the given code"""
        game = Game.query.filter_by(code=code).first()

        if game:
            if len(game.game_players) == 1:
                player1 = game.game_players[0].player
                if self is not player1:
                    gp_assoc = GamePlayerAssociation()
                    gp_assoc.player_id = self.id
                    gp_assoc.game_id = game.id
                    print(gp_assoc.player_id)
                    db.session.add(gp_assoc)
                    db.session.commit()
                    return game
        return None
    
    def join_random_game(self):
        """Joins a random game from the available games"""
        available_games = self.get_available_games()
        if available_games:
            random_game = random.choice(available_games)
            assoc = GamePlayerAssociation()
            assoc.game_id = random_game.id
            assoc.player_id = self.id
            db.session.add(assoc)
            db.session.commit()
            return random_game
        return None
    
    def get_available_games(self):
        """Returns a list of all available/joinable games"""
        all_games = Game.query.all()
        available_games = [game for game in all_games if len(game.game_players) == 1]
        return available_games

    def send_message(self, game_id, text):
        """Sends a message in the game chat"""
        message = Message()
        message.player_id = self.id
        message.game_id = game_id
        message.text = text

        db.session.add(message)
        db.session.commit()
        return message

    def send_friend_request(self, player_username):
        """Sends a friend request to the player with given id"""
        player = Player.query.filter_by(username=player_username).first()
        if player and player is not self and player not in self.get_all_friends():
            friend_request = FriendRequest()
            friend_request.sender_id = self.id
            friend_request.receiver_id = player.id
            db.session.add(friend_request)
            db.session.commit()
            return friend_request
        return None
    
    def get_friend_requests(self):
        """Gets all friend requests sent to this player"""
        return FriendRequest.query.filter_by(receiver_id=self.id).all()
    
    def accept_friend_request(self, request_id):
        """Accepts a friend request"""
        request = FriendRequest.query.get(request_id)
        if request:
            friendship = Friendship()
            friendship.player1_id = request.sender_id
            friendship.player2_id = request.receiver_id
            
            db.session.add(friendship)
            db.session.delete(request)
            db.session.commit()
            return friendship
        return None
    
    def reject_friend_request(self, request_id):
        """Rejects a friend request"""
        request = FriendRequest.query.get(request_id)
        if request:
            db.session.delete(request)
            db.session.commit()
            return True
        return False
    
    def get_all_friends(self):
        """Returns all friends of this player"""
        friendships = Friendship.query.filter((Friendship.player1_id == self.id)
                                          | (Friendship.player2_id == self.id)).all()
        return [Player.query.get(f_ship.player1_id)
                if f_ship.player1_id != self.id
                else Player.query.get(f_ship.player2_id)
                for f_ship in friendships]
    
    def make_move(self, game_id, tile_number):
        """Makes a move in a single game"""
        game = Game.query.get(game_id)
        if game:
            if Move.query.filter((Move.game_id == game_id)
                                 & (Move.tile_number == tile_number)).all():
                return False
            move = Move()
            move.player_id = self.id
            move.game_id = game_id
            move.tile_number = tile_number
            db.session.add(move)
            db.session.commit()
            return move
        return None


class Game(BaseModel, db.Model):
    """Model for the tic-tac-toe game"""
    __tablename__ = "games"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    code = db.Column(db.String(10), unique=True)
    difficulty = db.Column(db.Integer, default=1)
    finished = db.Column(db.Boolean, default=False)
    winner_id = db.Column(db.String(36), db.ForeignKey("players.id"), nullable=True)
    moves = db.relationship("Move", backref="moved_game", # For lack of a better term
                            cascade="all, delete, delete-orphan")
    messages = db.relationship("Message", backref="messaged_game")

    def __init__(self):
        self.code = self.generate_random_code(8)

    def to_dict(self):
        """Dictionary representation"""
        game_players = self.game_players
        return {
            "id": self.id,
            "code": self.code,
            "difficulty": self.difficulty,
            "finished": self.finished,
            "winner_id": self.winner_id,
            "game_players": [game_player.player.to_dict() for game_player in game_players],
            "moves": [move.to_dict() for move in self.moves],
            "messages": [message.to_dict() for message in self.messages]
        }

    def generate_random_code(self, length):
        """
        Generate a random string of given length consisting of
        uppercase letters and digits
        """
        return "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                       for _ in range(length))
    
    def declare_winner(self, player_id):
        """Change game state to finished and set the winner"""
        player = Player.query.get(player_id)
        if player:
            self.winner_id = player_id
            self.finished = True
            player.score += (self.difficulty * 100) # Tentative... To be changed on further notice
            db.session.add(self)
            db.session.add(player)
            db.session.commit()

    def declare_draw(self):
        """Change game status to finished and set as a draw"""
        self.finished = True
        self.winner_id = None
        db.session.add(self)
        db.session.commit()



class Move(BaseModel, db.Model):
    """Model for a single move in a game"""
    __tablename__ = "moves"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tile_number = db.Column(db.Integer, nullable=False)
    game_id = db.Column(db.String(36), db.ForeignKey("games.id"))
    player_id = db.Column(db.String(36), db.ForeignKey("players.id"), nullable=False)

    def to_dict(self):
        """Dictionary representation"""
        return {
            "id": self.id,
            "tile_number": self.tile_number,
            "game_id": self.game_id,
            "player_id": self.player_id
        }


class Message(BaseModel, db.Model):
    """Model for messages sent by players during games"""
    __tablename__ = "messages"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = db.Column(db.Text, nullable=False)
    player_id = db.Column(db.String(36), db.ForeignKey("players.id"))
    game_id = db.Column(db.String(36), db.ForeignKey("games.id"))

    def to_dict(self):
        """Dictionary representation"""
        return {
            "id": self.id,
            "text": self.text,
            "player_id": self.player_id,
            "game_id": self.game_id
        }


class Friendship(db.Model):
    """Model for friendship amongst players"""
    __tablename__ = "friendships"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    player1_id = db.Column(db.String(36), db.ForeignKey("players.id"))
    player2_id = db.Column(db.String(36), db.ForeignKey("players.id"))

    def to_dict(self):
        """Dictionary representation"""
        return {
            "id": self.id,
            "player1": Player.query.get(self.player1_id).to_dict(),
            "player2": Player.query.get(self.player2_id).to_dict()
        }

class FriendRequest(db.Model):
    """Model for friend requests"""
    __tablename__ = "friend_requests"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), db.ForeignKey("players.id"))
    receiver_id = db.Column(db.String(36), db.ForeignKey("players.id"))

    def to_dict(self):
        """Dictionary representation"""
        return {
            "id": self.id,
            "sender": Player.get(self.sender_id).to_dict(),
            "receiver": Player.get(self.receiver_id).to_dict()
        }