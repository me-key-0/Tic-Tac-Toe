#!/usr/bin/python3
"""
Contains the game logic
"""
from flask import request, session, json
from flask_login import current_user
from flask_socketio import emit, join_room, send

from src.models import Player, Game, Message
from src import db,  redis_conn, socketio, login_manager


@socketio.on('create_game')
def on_create_game(data):
    """
    Socket event handler for creating a new game.
    This function is triggered when a client sends a 'create_game' event. It creates a new game 
    instance, adds it to the database, commits the changes, joins the creator to the game room, 
    initializes the game state, and sends a message to the room announcing the creation of the game.
    
    """
    difficulty = data.get("difficulty", 1)
    user: Player = Player.query.get(session["user_id"])
    game = user.create_game(difficulty)
    room = game.code
    join_room(room)
    save_game_state(room, create_game_state())
    emit("game_created", f"{user.username} has created game {room}", room=room)

@socketio.on('join_game')
def on_join_game(data):
    """
    Socket event handler for joining an existing game.
    This function is triggered when a client sends a 'join_game' event. It checks if the game exists and is not finished.
    If the game is valid, it adds the client to the game room and sends a message to the room announcing the user joined.
    If the game is not found or already finished, it sends an error message back to the client.
    
    Args:
        data (dict): The data sent from the client, expected to contain the 'game_code' to identify the game to join.
    """
    user: Player = Player.query.get(session["user_id"])
    room = data.get('game_code')
    if room:
        game = Game.query.filter_by(code=room).first()
        if game and not game.finished:
            user.join_game_with_code(room)
    else:
        game = user.join_random_game()
    if game and not game.finished:
        join_room(room)
        emit("game_joined", f"{user.username} has joined the game {room}", room=room)
    else:
        emit("join_error", "Game not found or already finished.", room=request.sid)

@socketio.on('make_move')
def on_make_move(data):
    """
    Socket event handler for making a move in the game.
    This function is triggered when a client sends a 'make_move' event. It processes the move by checking if the move 
    is valid, updating the game state, checking for a winner, and saving the updated game state. If a move results in 
    a win or a draw, it updates the game accordingly and sends the current state to all players in the game room.
    Args:
        data (dict): The data sent from the client, expected to contain 'game_code' to identify the game and 'tile_number' 
                     to specify the move made by the player.
    """
    user: Player = Player.query.get(session["user_id"])
    room = data['game_code']
    game = Game.query.filter_by(code=room)
    tile_number = data['tile_number']
    state = get_game_state(room)
    if state["board"][tile_number] == "" and not state["finished"]:
        state["board"][tile_number] = state["turn"]
        state["turn"] = "O" if state["turn"] == "X" else "X"
        user.make_move(game.id, tile_number)
        winner = check_winner(state["board"])
        if winner:
            state["winner"] = winner
            state["finished"] = True
            game = Game.query.filter_by(code=room).first()
            game.declare_winner(session.get('user_id'))
        save_game_state(room, state)
        emit("game_state", state, room=room)

def check_winner(board):
    """
    Check the game board for a winner or a draw.
    This function checks all possible winning combinations in the Tic-Tac-Toe game board to see if there is a winner. 
    It returns 'X' or 'O' if one of the players has won, 'Draw' if the game is a draw, and None if there is no winner yet.
    Args:
        board (list): A list representing the current state of the game board.
        
    Returns:
        str: The winner ('X' or 'O'), 'Draw' if no spaces are left, or None if there is no winner yet.
    """

    # Logic to check the winner in Tic-Tac-Toe
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in winning_combinations:
        if board[a] == board[b] == board[c] and board[a] != "":
            return board[a]
    if "" not in board:
        return "Draw"
    return None

def create_game_state():
    """
    Initialize a new game state with an empty board.
    This function returns the initial state for a new game of Tic-Tac-Toe, including an empty board, the first player's turn, 
    and flags for the winner and whether the game is finished.
    Returns:
        dict: A dictionary representing the initial game state.
    """
    
    # Initialize a new game state with an empty board
    return {"board": [""] * 9, "turn": "X", "winner": None, "finished": False}

def save_game_state(game_code, state):
    redis_conn.set(game_code, json.dumps(state))

def get_game_state(game_code):
    state = redis_conn.get(game_code)
    return json.loads(state) if state else create_game_state()


@socketio.on("chat_message")
def send_message(data):
    """
    Socket event handler for sending a message in the chat of the game.
    This function is triggered when a client sends a 'chat_message' event. It checks if the game
    is a valid and unfinished game, creates the Message object and emits the message to all players in room.
    Args:
        data (dict): The data sent from the client, expected to contain 'game_code' to identify the game, and
        'text' containing the text of the message
    """
    user: Player = Player.query.get(session["user_id"])
    room = data["game_code"]
    game = Game.query.filter_by(code=room)
    if game and not game.finished:
        text = data["text"]
        message = user.send_message(game.id, text)
        emit("chat_message", message.to_dict(), json=True, room=room)
