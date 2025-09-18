from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Default valid keys
DEFAULT_KEYS = [
    "VladislavLalic",
    "DEF-456-UVW",
    "N355BSD16DXDRRT",
    "A40DJ0BGTSW494M",
    "Grobar",
    "S3L5KC5FV4WEKW8"
]

# JSON file to persist key-device bindings
KEY_FILE = "key_device_map.json"

# Load key-device map, create default if file doesn't exist
def load_keys():
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print("[WARN] JSON decode error, recreating key file")
            data = {key: "" for key in DEFAULT_KEYS}
            save_keys(data)
    else:
        data = {key: "" for key in DEFAULT_KEYS}
        save_keys(data)
    # Ensure all default keys exist in case new ones were added
    for key in DEFAULT_KEYS:
        if key not in data:
            data[key] = ""
    return data

def save_keys(data):
    with open(KEY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Load keys on startup
KEY_DEVICE_MAP = load_keys()

@app.route("/validate", methods=["POST"])
def validate():
    global KEY_DEVICE_MAP
    data = request.json
    key = data.get("key")
    device_id = data.get("device_id")

    if not key or not device_id:
        return jsonify({"valid": False, "error": "Key and device_id required"}), 400

    # Check key exists
    if key not in KEY_DEVICE_MAP:
        return jsonify({"valid": False, "reason": "Invalid or revoked key"})

    # If key unbound, bind it to this device
    if KEY_DEVICE_MAP[key] == "":
        KEY_DEVICE_MAP[key] = device_id
        save_keys(KEY_DEVICE_MAP)
        return jsonify({"valid": True, "bound": True})

    # If already bound to this device, allow
    if KEY_DEVICE_MAP[key] == device_id:
        return jsonify({"valid": True, "bound": True})

    # Key bound elsewhere → reject
    return jsonify({"valid": False, "reason": "Key already used on another device"})

@app.route("/reset_keys", methods=["POST"])
def reset_keys():
    """
    Optional: Reset all device bindings without removing keys.
    Example request: POST /reset_keys with JSON {"admin_pass": "secret"}
    """
    data = request.json
    admin_pass = data.get("admin_pass", "")
    if admin_pass != "your_admin_password":
        return jsonify({"error": "Unauthorized"}), 401

    for k in KEY_DEVICE_MAP:
        KEY_DEVICE_MAP[k] = ""
    save_keys(KEY_DEVICE_MAP)
    return jsonify({"status": "All keys reset"})

@app.route("/")
def home():
    return "License server with persistent device binding is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
