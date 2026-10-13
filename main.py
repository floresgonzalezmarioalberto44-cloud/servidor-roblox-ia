import os
import json
import traceback
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('models/gemini-1.5-flash')

PROMPT_SISTEMA = """
Eres un motor JSON estricto para Roblox Studio. 
Analiza la petición del usuario y responde ÚNICAMENTE con un objeto JSON válido. No uses bloques markdown, no uses comillas invertidas, ni agregues texto fuera del JSON.

Estructura exacta obligatoria:
{
  "reasoning": "Explicación breve",
  "action": "create",
  "shape": "Block",
  "size": {"X": 4, "Y": 4, "Z": 4},
  "position": {"X": 0, "Y": 0, "Z": 0},
  "color": {"R": 0, "G": 0.8, "B": 0.2},
  "material": "Wood",
  "has_light": false,
  "light_details": {"type": "PointLight", "brightness": 2, "color": {"R": 1, "G": 1, "B": 1}},
  "has_script": false,
  "script_code": "",
  "has_sound": false,
  "sound_id": "rbxassetid://0"
}
"""

@app.route('/')
def home():
    return "Servidor activo."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear bloque') if data else 'crear bloque'

        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición: {prompt_usuario}")
        texto = response.text.strip()

        inicio = texto.find('{')
        fin = texto.rfind('}')
        
        if inicio != -1 and fin != -1 and fin > inicio:
            json_str = texto[inicio:fin+1]
            json_respuesta = json.loads(json_str)
            return jsonify(json_respuesta), 200
        else:
            raise ValueError("No JSON found")

    except Exception as e:
        print("ERROR EN RENDER:")
        traceback.print_exc()
        return jsonify({
            "reasoning": "Respaldo seguro de emergencia.",
            "action": "create",
            "shape": "Block",
            "size": {"X": 4, "Y": 4, "Z": 4},
            "position": {"X": 0, "Y": 0, "Z": 0},
            "color": {"R": 0.5, "G": 0.3, "B": 0.1},
            "material": "Wood",
            "has_light": False,
            "light_details": {"type": "PointLight", "brightness": 2, "color": {"R": 1, "G": 1, "B": 1}},
            "has_script": False,
            "script_code": "",
            "has_sound": False,
            "sound_id": "rbxassetid://0"
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
