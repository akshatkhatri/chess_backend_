from flask import Flask, request, jsonify
from flask_cors import CORS
import pexpect
import os

app = Flask(__name__)
CORS(app)

def init_engine():
    try:
        engine = pexpect.spawn('./chess_game', encoding='utf-8', timeout=None)  # Wait as long as needed
        engine.sendline('uci')
        engine.expect('uciok')
        engine.sendline('isready')
        engine.expect('readyok')
        return engine
    except Exception as e:
        raise RuntimeError(f"Failed to initialize engine: {e}")

def read_response(engine):
    response = []

    while True:
        try:
            line = engine.readline().strip()
            print(">>", line)
            response.append(line)

            if line in ['readyok', 'uciok'] or line.startswith('bestmove'):
                break

        except pexpect.exceptions.TIMEOUT:
            response.append("[Timeout while waiting for response]")
            break
        except pexpect.exceptions.EOF:
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
            resp = read_response(engine)
            full_response.append({cmd: resp})

        engine.terminate()  # Clean up
        return jsonify({"responses": full_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
