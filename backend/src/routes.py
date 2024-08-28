from flask import request, jsonify, session

from src.models import Player
from src import app, db, bcrypt


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

    return jsonify({
        "id": new_user.id,
        "email": new_user.email
    })

@app.route("/login", methods=["POST"])
def login_user_():
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
    user = user or Player.query.filter_by(username=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
    
    session["user_id"] = user.id

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
    return jsonify({"message": "Logged out successfully"}), 200

@app.route("/available_games")
def get_available_games():
    """Get all available games"""
    current_user = Player.query.get(session["user_id"])
    if current_user:
        games = current_user.get_available_games()
        return jsonify([game.to_dict() for game in games])
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/send_friend_request", methods=["POST"])
def send_friend_request():
    """Sends friend request to specified player"""
    current_user = Player.query.get(session["user_id"])
    if current_user:
        post_data = request.json
        friend_request = current_user.send_friend_request(post_data["username"])
        if friend_request:
            return jsonify(friend_request.to_dict())
        return jsonify({"error": "Could not send friend request"}), 400
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/friend_requests")
def get_friend_requests():
    """Returns all friend requests received by player"""
    current_user = Player.query.get(session["user_id"])
    if current_user:
        friend_requests = current_user.get_friend_requests()
        return jsonify([f_request.to_dict() for f_request in friend_requests])
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/accept_friend_request", methods=["POST"])
def accept_friend_request():
    """Accepts a friend request"""
    current_user = Player.query.get(session["user_id"])
    if current_user:
        friendship = current_user.accept_friend_request(request.json.get("request_id"))
        if friendship:
            return jsonify(friendship.to_dict())
        return jsonify({"error": "Could not accept friend request"}), 400
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/reject_friend_request", methods=["POST"])
def reject_friend_request():
    """Rejects friend request"""
    current_user = Player.query.get(session["user_id"])
    if current_user:
        confirm = current_user.reject_friend_request(request.json.get("request_id"))
        if confirm:
            return jsonify(confirm.to_dict())
        return jsonify({"error": "Could not accept friend request"}), 400
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/friends")
def get_friends():
    """Returns all friends of requesting user"""
    current_user = Player.query.get(session["user_id"])
    if current_user:
        friends = current_user.get_all_friends()
        return jsonify([friend.to_dict() for friend in friends])
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/history")
def get_previous_games():
    """Retrieves all previous games of user"""
    current_user = Player.query.get(session["user_id"])
    if current_user:
        games = current_user.get_previous_games()
        return jsonify([game.to_dict() for game in games])
    return jsonify({"error": "Unauthorized"}), 401
