from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# ---------------- Configuration ----------------
JSONBIN_ID = "68cbd52dae596e708ff2cc0b"  # Your bin ID
JSONBIN_SECRET = "$2a$10$1JSftuEGZVvuqBTLGi3URulP.U6VBxFlrzs5tfHcdtzJ02Rx2rGzi"  # X-Master-Key
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}"

HEADERS = {
    "X-Master-Key": JSONBIN_SECRET,
    "Content-Type": "application/json"
}

# ---------------- Helpers ----------------
def load_keys_from_bin():
    """Fetch the key-device map from JSONBin."""
    try:
        resp = requests.get(JSONBIN_URL + "/latest", headers=HEADERS, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            # JSONBin stores your data under 'record'
            return data.get("record", {})
        else:
            print("[WARN] Failed to load keys from JSONBin:", resp.status_code)
            return {}
    except Exception as e:
        print("[ERROR] Exception loading keys from JSONBin:", e)
        return {}

def save_keys_to_bin(data):
    """Update the JSONBin with the new key-device map."""
    try:
        resp = requests.put(JSONBIN_URL, headers=HEADERS, json=data, timeout=6)
        if resp.status_code not in [200, 201]:
            print("[WARN] Failed to save keys to JSONBin:", resp.status_code, resp.text)
    except Exception as e:
        print("[ERROR] Exception saving keys to JSONBin:", e)

# ---------------- Routes ----------------
@app.route("/validate", methods=["POST"])
def validate():
    data = request.json
    key = data.get("key")
    device_id = data.get("device_id")

    if not key or not device_id:
        return jsonify({"valid": False, "error": "Key and device_id required"}), 400

    keys_map = load_keys_from_bin()

    # Check key exists
    if key not in keys_map:
        return jsonify({"valid": False, "reason": "Invalid or revoked key"})

    # If key unbound, bind it to this device
    if keys_map[key] == "":
        keys_map[key] = device_id
        save_keys_to_bin(keys_map)
        return jsonify({"valid": True, "bound": True})

    # If already bound to this device, allow
    if keys_map[key] == device_id:
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

    keys_map = load_keys_from_bin()
    for k in keys_map:
        keys_map[k] = ""
    save_keys_to_bin(keys_map)
    return jsonify({"status": "All keys reset"})

@app.route("/")
def home():
    return "License server with JSONBin device binding is running!"

# ---------------- Main ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
