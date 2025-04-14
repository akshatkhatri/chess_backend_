from flask import Flask, request, jsonify
from flask_cors import CORS
import pexpect
import os

app = Flask(__name__)
CORS(app)

# Start the chess engine using pexpect
engine = pexpect.spawn('./chess_game', encoding='utf-8', timeout=20)  # Add full path if needed

# Send initial UCI command
engine.sendline('uci')
engine.expect('uciok')

# Send isready to ensure it's ready
engine.sendline('isready')
engine.expect('readyok')


def send_command(cmd):
    engine.sendline(cmd)


def read_response():
    response = []

    while True:
        try:
            line = engine.readline().strip()
            print(">>", line)
            response.append(line)

            if line == 'readyok' or line.startswith('bestmove') or line == 'uciok':
                break

        except pexpect.exceptions.TIMEOUT:
            break
        except pexpect.exceptions.EOF:
            response.append("[Engine closed unexpectedly]")
            break

    return response


@app.route("/")
def hello_world():
    return "<p>Hello, Worldddd!</p>"


@app.route('/uci', methods=['POST'])
def uci_command():
    data = request.get_json()
    command = data.get("command")
    if not command:
        return jsonify({"error": "No command provided"}), 400

    send_command(command)
    output = read_response()
    return jsonify({"response": output})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render provides the port via env variable
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
