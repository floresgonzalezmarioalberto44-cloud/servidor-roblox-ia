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
Eres un motor JSON estricto para un NPC de Roblox. 
Devuelve ÚNICAMENTE un objeto JSON válido con la estructura exacta indicada abajo. No agregues texto adicional, explicaciones ni bloques markdown.

Estructura exacta obligatoria:
{
  "reasoning": "Breve explicación de la forma",
  "action": "create",
  "shape": "Block",
  "size": {"X": 6, "Y": 2, "Z": 3},
  "position": {"X": 0, "Y": 0, "Z": 0},
  "color": {"R": 0, "G": 0.4, "B": 1},
  "material": "SmoothPlastic",
  "has_light": false,
  "light_details": {"type": "PointLight", "brightness": 2, "color": {"R": 1, "G": 1, "B": 1}}
}
"""

@app.route('/')
def home():
    return "Servidor activo."

@app.route('/construir', methods=['POST'])
def construir():
    # Definimos un JSON de respaldo por defecto por si algo falla a nivel general
    fallback_json = {
        "reasoning": "Pieza de respaldo por defecto.",
        "action": "create",
        "shape": "Block",
        "size": {"X": 4, "Y": 2, "Z": 4},
        "position": {"X": 0, "Y": 0, "Z": 0},
        "color": {"R": 1, "G": 0, "B": 0},
        "material": "SmoothPlastic",
        "has_light": false,
        "light_details": {"type": "PointLight", "brightness": 2, "color": {"R": 1, "G": 1, "B": 1}}
    }

    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify(fallback_json), 200

        prompt_usuario = data['prompt']
        
        try:
            response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición: {prompt_usuario}")
            texto = response.text.strip() if response and hasattr(response, 'text') else ""
        except Exception:
            texto = ""

        # Intentar extraer el JSON delimitado por llaves
        inicio = texto.find('{')
        fin = texto.rfind('}')
        
        if inicio != -1 and fin != -1 and fin > inicio:
            json_str = texto[inicio:fin+1]
            json_respuesta = json.loads(json_str)
            return jsonify(json_respuesta), 200
        else:
            return jsonify(fallback_json), 200

    except Exception as e:
        print("EXCEPCIÓN INTERNA CAPTURADA:")
        traceback.print_exc()
        return jsonify(fallback_json), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
