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
Devuelve ÚNICAMENTE un objeto JSON válido. NO uses bloques de código markdown, NO uses comillas invertidas (```), NO escribas explicaciones fuera del JSON.

Estructura exacta obligatoria:
{
  "reasoning": "Explicación breve",
  "action": "create",
  "shape": "Block",
  "size": {"X": 4, "Y": 2, "Z": 6},
  "position": {"X": 0, "Y": 0, "Z": 0},
  "color": {"R": 1, "G": 0, "B": 0},
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
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "No prompt"}), 400

        prompt_usuario = data['prompt']
        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición: {prompt_usuario}")
        
        texto = response.text.strip()
        
        # Limpieza ultra robusta para extraer solo el contenido entre llaves {}
        inicio = texto.find('{')
        fin = texto.rfind('}')
        if inicio != -1 and fin != -1 and fin > inicio:
            texto = texto[inicio:fin+1]

        json_respuesta = json.loads(texto)
        return jsonify(json_respuesta), 200

    except Exception as e:
        print("ERROR INTERNO DETALLADO:")
        traceback.print_exc()
        # JSON de respaldo seguro para que Roblox nunca reciba un error 500
        fallback_json = {
            "reasoning": "Respaldo automático por fallo de formato en IA.",
            "action": "create",
            "shape": "Block",
            "size": {"X": 4, "Y": 2, "Z": 6},
            "position": {"X": 0, "Y": 0, "Z": 0},
            "color": {"R": 0, "G": 0.5, "B": 1},
            "material": "SmoothPlastic",
            "has_light": false,
            "light_details": {"type": "PointLight", "brightness": 2, "color": {"R": 1, "G": 1, "B": 1}}
        }
        return jsonify(fallback_json), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
