from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

KEY_FILE = "key_device_map.json"

# Load key-device data from file
def load_keys():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return json.load(f)
    return {}  # No keys yet

# Save key-device data to file
def save_keys(data):
    with open(KEY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Load keys at startup
KEY_DEVICE_MAP = load_keys()

@app.route("/validate", methods=["POST"])
def validate():
    global KEY_DEVICE_MAP
    data = request.json
    key = data.get("key")
    device_id = data.get("device_id")

    if not key or not device_id:
        return jsonify({"error": "Key and device_id required"}), 400

    # Check if key exists at all
    if key not in KEY_DEVICE_MAP:
        return jsonify({"valid": False, "reason": "Invalid or revoked key"})

    # If key is not yet bound, bind it
    if KEY_DEVICE_MAP[key] == "":
        KEY_DEVICE_MAP[key] = device_id
        save_keys(KEY_DEVICE_MAP)
        return jsonify({"valid": True, "bound": True})

    # If key is already bound to this device, allow
    if KEY_DEVICE_MAP[key] == device_id:
        return jsonify({"valid": True, "bound": True})

    # If key bound elsewhere → reject
    return jsonify({"valid": False, "reason": "Key already used on another device"})

@app.route("/")
def home():
    return "License server with persistent device binding is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
