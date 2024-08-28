from flask import request, jsonify, session
from flask_login import current_user, login_required, login_user, logout_user

from src.models import Game, Player
from src import (
    app, bcrypt, db, login_manager, socket
)

@app.before_request
def manage_db():
    db.create_all()
    db.session.close()

@app.route("/@me")
def get_current_user():
    """
    Get the current logged-in user's details.

    This route retrieves the details of the currently authenticated user based on the session.
    
    Returns:
        - 200 OK: A JSON object with the user's `id` and `email`.
        - 401 Unauthorized: A JSON object with an `error` message if no user is logged in.
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = Player.query.filter_by(id=user_id).first()
    return jsonify({
        "id": user.id,
        "email": user.email
    }) 

@app.route("/register", methods=["POST"])
def register_user():
    """
    Register a new user.

    This route creates a new user account with the provided `email`, `password`, and `username`.
    
    Request JSON body:
        - `email` (str): The user's email address.
        - `password` (str): The user's password.
        - `username` (str): The user's chosen username.
    
    Returns:
        - 201 Created: A JSON object with the newly created user's `id` and `email`.
        - 409 Conflict: A JSON object with an `error` message if a user with the given email already exists.
    """
    email = request.json["email"]
    password = request.json["password"]
    username = request.json["username"]

    user_exists = Player.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password)
    new_user = Player(username=username,email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    session["user_id"] = new_user.id
    login_user(new_user, remember=True)

    return jsonify({
        "id": new_user.id,
        "email": new_user.email
    })

@app.route("/login", methods=["POST"])
def login():
    """
    Log in an existing user.

    This route authenticates a user with the provided `email` and `password`.
    
    Request JSON body:
        - `email` (str): The user's email address.
        - `password` (str): The user's password.
    
    Returns:
        - 200 OK: A JSON object with the authenticated user's `id` and `email`.
        - 401 Unauthorized: A JSON object with an `error` message if the credentials are incorrect.
    """
    email = request.json["email"]
    password = request.json["password"]

    user = Player.query.filter_by(email=email).first()
    user = user or Player.query.filter_by(username=email).first() # User can login by email or username

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
    
    session["user_id"] = user.id
    login_user(user, remember=True)

    return jsonify({
        "id": user.id,
        "email": user.email
    })

@app.route("/logout", methods=["POST"])
def logout_user():
    """
    Log out the current user.

    This route logs out the currently authenticated user by clearing their session.
    
    Returns:
        - 200 OK: A JSON object with a success message.
    """
    session.pop("user_id")
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/new_game", methods=["POST"])
def create_game():
    """
    Create new game

    This route creates a new game and sends the game data

    Returns:
        - 200 OK: A JSON object of the new game created
    """
    if current_user.is_authenticated:
        difficulty = request.json["difficulty"]
        new_game = current_user.create_game(difficulty)
        return jsonify(new_game.to_dict())
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/join", methods=["POST"])
def join_game():
    """Join a game"""
    if current_user.is_authenticated:
        code = request.json.get("code")
        if code:
            game = current_user.join_game_with_code(code)
        else:
            game = current_user.join_random_game()
        if game:
            return jsonify(game.to_dict())
        return jsonify({"error": "Game not found"}), 404
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/available_games")
def get_available_games():
    """Get all available games"""
    if current_user.is_authenticated:
        games = current_user.get_available_games()
        return jsonify([game.to_dict() for game in games])
    return jsonify({"error": "Unauthorized"}), 401

@socket.on("lobby")
def joined_lobby(joined_game):
    """Handler function for when a player creates/joins a game"""
    socket.emit(joined_game)

@app.route("/move", methods=["POST"])
def make_move():
    """Emulates a player making a move"""
    if current_user.is_authenticated:
        post_data = request.json
        move = current_user.make_move(post_data["game_id"],
                                    post_data["tile_number"])
        socket.emit("move", move.to_dict())
        return jsonify(move.to_dict())
    else:
        return jsonify({"error": "Unauthorized"}), 401

@app.route("/message", methods=["POST"])
def send_message():
    """Emulates aplayer sending a message"""
    if current_user.is_authenticated:
        post_data = request.json
        message = current_user.send_message(post_data["game_id"],
                                            post_data["text"])
        socket.emit("chat", message.to_dict())
        return jsonify(message.to_dict())
    else:
        return jsonify({"error": "Unauthorized"}), 401

@app.route("/winner", methods=["POST"])
def declare_winner():
    """Declares winner of given game"""
    if current_user.is_authenticated:
        game_id = request.json.get("game_id")
        game = Game.query.get(game_id)
        if game:
            game.declare_winner(current_user.id)
            return jsonify(game.to_dict())
        return jsonify({"error": "Game not found"}), 404
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/send_friend_request", methods=["POST"])
def send_friend_request():
    """Sends friend request to specified player"""
    if current_user.is_authenticated:
        post_data = request.json
        friend_request = current_user.send_friend_request(post_data["username"])
        if friend_request:
            socket.emit("friend_request", friend_request.to_dict())
            return jsonify(friend_request.to_dict())
        return jsonify({"error": "Could not send friend request"}), 400
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/get_friend_requests")
def get_friend_requests():
    """Returns all friend requests received by player"""
    if current_user.is_authenticated:
        friend_requests = current_user.get_friend_requests()
        return jsonify([f_request.to_dict() for f_request in friend_requests])
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/accept_friend_request", methods=["POST"])
def accept_friend_request():
    """Accepts a friend request"""
    if current_user.is_authenticated:
        friendship = current_user.accept_friend_request(request.json.get("request_id"))
        if friendship:
            return jsonify(friendship.to_dict())
        return jsonify({"error": "Could not accept friend request"}), 400
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/reject_friend_request", methods=["POST"])
def reject_friend_request():
    """Rejects friend request"""
    if current_user.is_authenticated:
        confirm = current_user.reject_friend_request(request.json.get("request_id"))
        if confirm:
            return jsonify(confirm.to_dict())
        return jsonify({"error": "Could not accept friend request"}), 400
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/friends")
def get_friends():
    """Returns all friends of requesting user"""
    if current_user.is_authenticated:
        friends = current_user.get_all_friends()
        return jsonify([friend.to_dict() for friend in friends])
    return jsonify({"error": "Unauthorized"}), 401
