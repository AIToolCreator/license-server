from flask import Flask, request, jsonify

app = Flask(__name__)

# Example list of valid keys (you can replace this with a database or file)
VALID_KEYS = ["ABC-123-XYZ", "DEF-456-UVW"]

@app.route("/validate", methods=["GET"])
def validate():
    key = request.args.get("key")
    if not key:
        return jsonify({"error": "No key provided"}), 400

    if key in VALID_KEYS:
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})

# Optional: root route to check server is alive
@app.route("/")
def home():
    return "License server is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
