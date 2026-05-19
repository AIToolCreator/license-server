import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ---------------- Configuration ----------------
JSONBIN_ID = "68cbd52dae596e708ff2cc0b"

# CHANGE THESE IF YOU CHANGE YOUR JSONBIN KEY/PASSWORD
JSONBIN_SECRET = os.environ.get(
    "JSONBIN_SECRET",
    "$2a$10$1JSftuEGZVvuqBTLGi3URulP.U6VBxFlrzs5tfHcdtzJ02Rx2rGzi"
)

ADMIN_PASS = os.environ.get(
    "ADMIN_PASS",
    "your_admin_password"
)

JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}"

HEADERS = {
    "X-Master-Key": JSONBIN_SECRET,
    "Content-Type": "application/json"
}

# ---------------- Helpers ----------------
def load_keys_from_bin():
    try:
        resp = requests.get(
            JSONBIN_URL + "/latest",
            headers=HEADERS,
            timeout=6
        )

        if resp.status_code == 200:
            data = resp.json()
            raw = data.get("record", {})

            keys = {}

            for k, v in raw.items():
                if isinstance(v, dict):
                    keys[k] = {
                        "device": v.get("device", ""),
                        "owner": v.get("owner", "")
                    }
                else:
                    keys[k] = {
                        "device": v,
                        "owner": ""
                    }

            return keys

        print("[WARN] Failed to load keys:", resp.status_code)
        return {}

    except Exception as e:
        print("[ERROR] Exception loading keys:", e)
        return {}

def save_keys_to_bin(data):
    try:
        resp = requests.put(
            JSONBIN_URL,
            headers=HEADERS,
            json=data,
            timeout=6
        )

        if resp.status_code not in [200, 201]:
            print("[WARN] Failed to save keys:", resp.status_code, resp.text)

    except Exception as e:
        print("[ERROR] Exception saving keys:", e)

# ---------------- Routes ----------------
@app.route("/")
def home():
    return "License server with JSONBin device binding is running!"

@app.route("/validate", methods=["POST"])
def validate():
    data = request.json or {}

    key = data.get("key")
    device_id = data.get("device_id")

    if not key or not device_id:
        return jsonify({
            "valid": False,
            "error": "Key and device_id required"
        }), 400

    keys_map = load_keys_from_bin()

    if key not in keys_map:
        return jsonify({
            "valid": False,
            "reason": "Invalid or revoked key"
        })

    key_info = keys_map[key]
    bound_device = key_info.get("device", "")

    # First activation
    if bound_device == "":
        keys_map[key]["device"] = device_id
        save_keys_to_bin(keys_map)

        return jsonify({
            "valid": True,
            "bound": True
        })

    # Same device
    if bound_device == device_id:
        return jsonify({
            "valid": True,
            "bound": True
        })

    # Different device
    return jsonify({
        "valid": False,
        "reason": "Key already used on another device"
    })

@app.route("/reset_keys", methods=["POST"])
def reset_keys():
    data = request.json or {}

    admin_pass = data.get("admin_pass", "")

    if admin_pass != ADMIN_PASS:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    keys_map = load_keys_from_bin()

    for k in keys_map:
        keys_map[k]["device"] = ""

    save_keys_to_bin(keys_map)

    return jsonify({
        "status": "All keys reset"
    })

# ---------------- Main ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
