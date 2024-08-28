#!/usr/bin/python3
"""
Run the flask app when executed
"""
from src import app, socket

if __name__ == "__main__":
    socket.run(app, debug=True)