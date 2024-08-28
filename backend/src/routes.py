from flask import request, jsonify, session
from src.models import Player
from src import app, db, bcrypt

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
def login_user():
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
    session.pop("user_id")
    return jsonify({"message": "Logged out successfully"}), 200

