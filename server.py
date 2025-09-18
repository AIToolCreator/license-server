from flask import Flask, request, jsonify

app = Flask(__name__)

# Original valid keys
VALID_KEYS = [
    "DEF-456-UVW",
    "N355BSD16DXDRRT",
    "A40DJ0BGTSW494M",
    "Grobar",
    "S3L5KC5FV4WEKW8"
]

# New: key -> device mapping (in-memory)
KEY_DEVICE_MAP = {}

@app.route("/validate", methods=["POST"])
def validate():
    data = request.json
    key = data.get("key")
    device_id = data.get("device_id")

    if not key or not device_id:
        return jsonify({"error": "Key and device_id required"}), 400

    if key not in VALID_KEYS:
        return jsonify({"valid": False, "reason": "Invalid key"})

    # If key not yet bound, bind to this device
    if key not in KEY_DEVICE_MAP:
        KEY_DEVICE_MAP[key] = device_id
        return jsonify({"valid": True, "bound": True})

    # If key already bound to this device, allow
    if KEY_DEVICE_MAP[key] == device_id:
        return jsonify({"valid": True, "bound": True})

    # If key bound elsewhere → reject
    return jsonify({"valid": False, "reason": "Key already used on another device"})

@app.route("/")
def home():
    return "License server with device binding is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
