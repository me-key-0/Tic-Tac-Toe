#!/usr/bin/python3
"""
Run the flask app when executed
"""
from src import app, socketio

if __name__ == "__main__":
    socketio.run(app, debug=True)