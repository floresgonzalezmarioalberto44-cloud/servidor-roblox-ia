import os
from flask import Flask, jsonify, request
import google.generativeai as genai

app = Flask(__name__)

# Configuramos la API Key de Google que guardaremos en Render
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Aquí elegimos explícitamente el modelo rápido y gratuito (Gemini 1.5 Flash)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/", methods=["GET"])
def home():
    return "¡El servidor con Gemini 1.5 Flash está activo 24/7! 🚀", 200

@app.route("/process-action", methods=["POST"])
def process_action():
    try:
        data = request.json
        npc_prompt = data.get("prompt", "")
        
        print(f"Orden recibida para Gemini: {npc_prompt}")
        
        # Le damos instrucciones estrictas a Gemini para que devuelva un JSON estructurado
        prompt_sistema = f"""
        Eres el cerebro de un NPC constructor en Roblox. El usuario pidió: '{npc_prompt}'.
        Analiza si el objeto necesita un script interactivo con proximidad (como pelotas, autos, etc.) o si es estático.
        Devuelve estrictamente un JSON válido con esta estructura exacta:
        {{
            "action": "build_complex_sequence",
            "description": "{npc_prompt}",
            "parts": [
                {{
                    "shape": "Part",
                    "size": {{"X": 4, "Y": 4, "Z": 4}},
                    "color": {{"R": 1, "G": 0.8, "B": 0}},
                    "position": {{"X": 0, "Y": 3, "Z": 0}},
                    "rotation": {{"X": 0, "Y": 0, "Z": 0}}
                }}
            ],
            "requires_script": false,
            "script_code": ""
        }}
        """
        
        # Le mandamos la orden al modelo que elegimos
        response = model.generate_content(prompt_sistema)
        
        # Por ahora regresamos una respuesta simulada o la que decodifique Gemini
        respuesta_ia = {
            "action": "build_complex_sequence",
            "description": npc_prompt,
            "parts": [{"shape": "Part", "size": {"X": 4, "Y": 4, "Z": 4}, "color": {"R": 1, "G": 1, "B": 0}, "position": {"X": 0, "Y": 3, "Z": 0}}],
            "requires_script": False,
            "script_code": ""
        }

        return jsonify(respuesta_ia), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
