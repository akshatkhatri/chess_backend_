from flask import Flask, request, jsonify
import subprocess


app = Flask(__name__)

engine = subprocess.Popen(
    ['chess_game.exe'],  # Replace with actual filename
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

def send_command(cmd):
    engine.stdin.write(cmd + '\n')
    engine.stdin.flush()

def read_response():
    response = []
    while True:
        line = engine.stdout.readline().strip()
        if line == 'readyok' or line.startswith('bestmove'):
            print(">>", line)
            response.append(line)
            break
        if line:
            response.append(line)
        if line == "uciok" or line == "Set":
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
    print(output)
    return jsonify({"response": output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)