import os
import json
import traceback
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Usamos el modelo correcto y compatible con la API actual
model = genai.GenerativeModel('gemini-2.0-flash')

PROMPT_SISTEMA = """
Eres un motor de arquitectura para Roblox Studio. Devuelve ÚNICAMENTE un objeto JSON válido, sin bloques markdown (```json).
Diseña una construcción con múltiples piezas ("objetos"). Si piden un auto, incluye un "VehicleSeat" y varias piezas. Si piden un árbol, incluye tronco y copa.

Estructura obligatoria exacta:
{
  "reasoning": "Construcción detallada",
  "objetos": [
    {
      "shape": "Cylinder",
      "size": {"X": 2, "Y": 6, "Z": 2},
      "offset": {"X": 0, "Y": 3, "Z": 0},
      "color": {"R": 0.4, "G": 0.2, "B": 0.1},
      "material": "Wood",
      "anchored": true,
      "transparency": 0,
      "can_collide": true
    },
    {
      "shape": "Ball",
      "size": {"X": 5, "Y": 5, "Z": 5},
      "offset": {"X": 0, "Y": 7, "Z": 0},
      "color": {"R": 0.1, "G": 0.7, "B": 0.2},
      "material": "Grass",
      "anchored": true,
      "transparency": 0,
      "can_collide": true
    }
  ]
}
"""

@app.route('/')
def home():
    return "Servidor activo."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear objeto') if data else 'crear objeto'

        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición: {prompt_usuario}")
        texto = response.text.strip()

        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        texto = texto.strip()

        inicio = texto.find('{')
        fin = texto.rfind('}')
        
        if inicio != -1 and fin != -1 and fin > inicio:
            json_str = texto[inicio:fin+1]
            json_respuesta = json.loads(json_str)
            return jsonify(json_respuesta), 200
        else:
            raise ValueError("No se encontró JSON válido.")

    except Exception as e:
        print("--- ERROR EN RENDER ---")
        traceback.print_exc()
        return jsonify({
            "reasoning": "Respaldo por error de API.",
            "objetos": [
                {
                  "shape": "Cylinder",
                  "size": {"X": 2, "Y": 6, "Z": 2},
                  "offset": {"X": 0, "Y": 3, "Z": 0},
                  "color": {"R": 0.4, "G": 0.2, "B": 0.1},
                  "material": "Wood",
                  "anchored": True,
                  "transparency": 0,
                  "can_collide": True
                },
                {
                  "shape": "Ball",
                  "size": {"X": 5, "Y": 5, "Z": 5},
                  "offset": {"X": 0, "Y": 7, "Z": 0},
                  "color": {"R": 0.1, "G": 0.7, "B": 0.2},
                  "material": "Grass",
                  "anchored": True,
                  "transparency": 0,
                  "can_collide": True
                }
            ]
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
