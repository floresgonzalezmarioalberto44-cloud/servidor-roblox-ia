import os
import json
import traceback
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Inicializamos el cliente moderno oficial de Google GenAI
API_KEY = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else genai.Client()

PROMPT_SISTEMA = """
Eres un motor de arquitectura y diseño para Roblox Studio. Analiza la petición del usuario y diseña una construcción detallada con múltiples piezas ("objetos").
Si piden una mesa, diseña una tabla superior plana (Block) y cuatro patas cilíndricas o bloques de soporte. Si piden un auto, incluye un VehicleSeat. Si piden un árbol, incluye tronco y copa.

Devuelve ÚNICAMENTE un objeto JSON válido. No uses bloques markdown (```json), no uses comillas invertidas ni texto fuera del JSON.

Estructura obligatoria exacta:
{
  "reasoning": "Descripción de la construcción",
  "objetos": [
    {
      "shape": "Block",
      "size": {"X": 6, "Y": 1, "Z": 4},
      "offset": {"X": 0, "Y": 4, "Z": 0},
      "color": {"R": 0.5, "G": 0.3, "B": 0.1},
      "material": "Wood",
      "anchored": true,
      "transparency": 0,
      "can_collide": true
    }
  ]
}
"""

@app.route('/')
def home():
    return "Servidor activo con el SDK oficial."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear objeto') if data else 'crear objeto'

        # Usamos el cliente moderno con gemini-2.0-flash
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"{PROMPT_SISTEMA}\n\nPetición del usuario: {prompt_usuario}"
        )
        
        texto = response.text.strip()
        print("TEXTO RECIBIDO DE LA IA:", texto)

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
            raise ValueError("No se encontró un JSON válido en la respuesta.")

    except Exception as e:
        print("--- ERROR CRÍTICO EN RENDER ---")
        traceback.print_exc()
        return jsonify({
            "reasoning": "Error interno: " + str(e),
            "objetos": [
                {
                  "shape": "Block",
                  "size": {"X": 6, "Y": 1, "Z": 4},
                  "offset": {"X": 0, "Y": 4, "Z": 0},
                  "color": {"R": 0.6, "G": 0.4, "B": 0.2},
                  "material": "Wood",
                  "anchored": True,
                  "transparency": 0,
                  "can_collide": True
                }
            ]
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
