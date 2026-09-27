import os
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
  return "¡El servidor puente para Roblox está despierto y activo! 🚀", 200


@app.route("/process-action", methods=["POST"])
def process_action():
  try:
    data = request.json
    npc_prompt = data.get("prompt", "")

    print(f"Orden recibida desde Roblox: {npc_prompt}")

    respuesta_ia = {
        "action": "create",
        "shape": "Part",
        "size": {"X": 4, "Y": 4, "Z": 4},
        "color": {"R": 0, "G": 0.4, "B": 1},
        "position": {"X": 0, "Y": 5, "Z": 0},
    }

    return jsonify(respuesta_ia), 200

  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)