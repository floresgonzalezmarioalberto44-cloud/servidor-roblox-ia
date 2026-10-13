import os
import json
import traceback
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Usamos estrictamente el nombre con el prefijo models/ que requiere esta versión de la API
model = genai.GenerativeModel('models/gemini-1.5-flash')

PROMPT_SISTEMA = """
Eres un motor de arquitectura y diseño para Roblox Studio. Analiza la petición del usuario y devuelve ÚNICAMENTE un objeto JSON válido con múltiples piezas ("objetos").
Si piden un árbol, diseña un cilindro marrón (Wood) para el tronco y una esfera o bloque verde (Grass / SmoothPlastic) para la copa. 
Si piden un auto, incluye un "VehicleSeat" y varias piezas móviles.

No uses bloques markdown (```json), no uses comillas invertidas ni texto fuera del JSON.

Estructura obligatoria exacta:
{
  "reasoning": "Descripción de la construcción",
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
    return "Servidor activo y listo para construir."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear bloque') if data else 'crear bloque'

        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición del usuario: {prompt_usuario}")
        texto = response.text.strip()
        print("TEXTO RECIBIDO DE GEMINI:", texto)

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
            raise ValueError("La respuesta de la IA no contiene un JSON válido.")

    except Exception as e:
        print("--- ERROR INTERNO EN RENDER ---")
        traceback.print_exc()
        return jsonify({
            "reasoning": "Error interno capturado: " + str(e),
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
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
