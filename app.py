from flask import Flask, request, jsonify
from flask_cors import CORS
import pexpect
import os

app = Flask(__name__)
CORS(app)

# Map start of command to the expected end marker
END_MARKERS = {
    "uci": "uciok",
    "isready": "readyok",
    "position": "Set",
    "go": "bestmove"
}

def init_engine():
    try:
        engine = pexpect.spawn('./chess_game', encoding='utf-8', timeout=None)
        engine.sendline('uci')
        engine.expect('uciok')
        engine.sendline('isready')
        engine.expect('readyok')
        return engine
    except Exception as e:
        raise RuntimeError(f"Failed to initialize engine: {e}")

def get_expected_marker(command):
    for prefix in END_MARKERS:
        if command.startswith(prefix):
            return END_MARKERS[prefix]
    return None

def read_response(engine, sent_command=None):
    print(f"Sent command: {sent_command}")
    response = []

    while True:
        try:
            line = engine.readline().strip()
            print(f"Received line: {line}")
            print(">>", line)  # Log the response line

            # Skip the sent command if echoed back
            if line == sent_command:
                continue
            if line:
                response.append(line)

            # Stop if we encounter a response like 'uciok' or 'readyok'
            if line in ['readyok', 'uciok', 'Set'] or line.startswith('bestmove'):
                break

        except pexpect.exceptions.TIMEOUT:
            print("[TIMEOUT ERROR] Waiting for response...")
            response.append("[Timeout while waiting for response]")
            break
        except pexpect.exceptions.EOF:
            print("[EOF ERROR] Engine closed unexpectedly")
            response.append("[Engine closed unexpectedly]")
            break

    return response


@app.route("/")
def hello_world():
    return "<p>Hello from your UCI Chess Server!</p>"

@app.route('/uci', methods=['POST'])
def uci_command():
    try:
        data = request.get_json()
        commands = data.get("commands")

        if not commands or not isinstance(commands, list):
            return jsonify({"error": "Please provide a list of UCI commands as 'commands'"}), 400

        engine = init_engine()
        full_response = []

        for cmd in commands:
            engine.sendline(cmd)
            resp = read_response(engine, sent_command=cmd)  # Pass the sent command
            full_response.append({cmd: resp})

        engine.terminate()  # Clean up
        return jsonify({"responses": full_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(debug=False, host='0.0.0.0', port=port, threaded=True)

if __name__ == "__main__":
    # Use the port from the environment variable, default to 5000 if not set
    # port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=5000)
