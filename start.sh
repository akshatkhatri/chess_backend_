#!/bin/bash

source venv/bin/activate

apt-get update
apt-get install -y g++ make libstdc++6
# Compile your C++ chess engine
g++ main.cpp movement.cpp king_check.cpp chessboard.cpp legalmoves.cpp notations.cpp hashing.cpp Evaluation.cpp Search.cpp -o chess_game

# Optional: Make it executable just in case
chmod +x chess_game
chmod +x start.sh

pip install -r requirements.txt

export FLASK_APP=app.py
export FLASK_ENV=production  # Set to 'development' for local testing

# Run the Flask app
export PORT=5000  # Or any valid port number of your choice
gunicorn app:app --bind 0.0.0.0:5000 --timeout 300



