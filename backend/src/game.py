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
    Handle a player's move in a Tic-Tac-Toe game.
    This function processes a move made by a player in a Tic-Tac-Toe game. It updates the game state,
    checks for a winner, and emits the updated game state to the players.
    Parameters:
        data (dict): A dictionary containing the following keys:
            - 'game_code' (string): The unique code identifying the game room.
            - 'tile_number' (int): The index of the tile where the player wants to make a move.
    Session:
        - 'user_id' (string): The ID of the current player making the move, retrieved from the session.
    Game Logic:
        - If it's the AI's turn (player 'O') in single-player mode, the AI makes a move.
        - Checks if the selected tile is empty and the game is not finished.
        - Updates the game board with the player's move and switches the turn.
        - Checks if the current move resulted in a win or draw:
            - Updates the game state to indicate a win or draw.
            - Calls `declare_winner()` to set the winner if applicable.
    Emits:
        - 'game_state_update' (dict): The updated game state to all players in the game room.
    Sends:
        - A message indicating the game is over and announcing the winner to all players in the game room.

    Game State:
        - The game state is a dictionary with the following structure:
            - 'board' (list): A list representing the game board, where each element is 'X', 'O', or ''.
            - 'turn' (string): Indicates whose turn it is ('X' or 'O').
            - 'winner' (string or None): The winner of the game ('X', 'O', or 'Draw').
            - 'finished' (bool): Indicates whether the game has finished.
    Examples:
        Player's move:
            data = {
                "game_code": "AB1234",
                "tile_number": 4
            }
        AI's move (in single-player mode):
            AI automatically picks a move based on the game state.
    """
    room = data['game_code']
    tile_number = data['tile_number']
    player_id = session.get('user_id')

    state = get_game_state(room)
    
    # If it's the AI's turn, let the AI make a move
    if state["turn"] == "O" and is_single_player_mode(room):
        ai_move = find_best_move(state["board"])
        tile_number = ai_move
        player_id = None  # AI has no player_id

    # Check for a valid move
    if state["board"][tile_number] == "" and not state["finished"]:
        state["board"][tile_number] = state["turn"]
        state["turn"] = "O" if state["turn"] == "X" else "X"
        winner = check_winner(state["board"])

        if winner:
            state["winner"] = winner
            state["finished"] = True
            if winner == "X" or winner == "O":
                game = Game.query.filter_by(code=room).first()
                game.declare_winner(player_id)  # For 'O', player_id is None (AI)
            send(f"Game over! Winner: {winner}", room=room)

        save_game_state(room, state)
        emit('game_state_update', state, room=room)

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

def create_game_state(single_player_mode=False):
    # Initialize a new game state with an empty board
    state = {"board": [""] * 9, "turn": "X", "winner": None, "finished": False}
    if single_player_mode:
        state["player_x_id"] = session.get('user_id')  # Player
        state["player_o_id"] = None  # AI
    return state


def save_game_state(game_code, state):
    redis_conn.set(game_code, json.dumps(state))

def get_game_state(game_code):
    state = redis_conn.get(game_code)
    return json.loads(state) if state else create_game_state()



def minimax(board, depth, is_maximizing, ai_marker, player_marker):
    """
    Minimax algorithm to determine the best move for the AI.

    :param board: List representing the game board
    :param depth: Current depth in the game tree
    :param is_maximizing: Boolean to check if the current move is maximizing or minimizing
    :param ai_marker: The marker used by the AI ('X' or 'O')
    :param player_marker: The marker used by the player ('X' or 'O')
    :return: Best score
    """
    winner = check_winner(board)
    if winner == ai_marker:
        return 1
    elif winner == player_marker:
        return -1
    elif winner == "Draw":
        return 0

    if is_maximizing:
        best_score = -float("inf")
        for i in range(9):
            if board[i] == "":
                board[i] = ai_marker
                score = minimax(board, depth + 1, False, ai_marker, player_marker)
                board[i] = ""
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float("inf")
        for i in range(9):
            if board[i] == "":
                board[i] = player_marker
                score = minimax(board, depth + 1, True, ai_marker, player_marker)
                board[i] = ""
                best_score = min(score, best_score)
        return best_score

def find_best_move(board):
    best_score = -float('inf')
    best_move = None
    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            score = minimax(board, 0, False)
            board[i] = ""
            if score > best_score:
                best_score = score
                best_move = i
    return best_move

def is_single_player_mode(room):
    state = get_game_state(room)
    return state.get("player_o_id") is None

