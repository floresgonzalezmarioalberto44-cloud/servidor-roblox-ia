import os
import json
import traceback
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Corrección clave: Usar el nombre directo del modelo sin 'models/'
model = genai.GenerativeModel('gemini-1.5-flash')

PROMPT_SISTEMA = """
Eres un arquitecto e ingeniero experto de Roblox Studio. Diseña una construcción detallada con múltiples piezas ("objetos") basada en la petición del usuario.
Si piden un auto, incluye un VehicleSeat y varias piezas móviles. Si piden un árbol, incluye tronco y hojas.

Devuelve ÚNICAMENTE un objeto JSON válido, sin bloques markdown, sin ```json y sin texto adicional.

Estructura obligatoria exacta:
{
  "reasoning": "Explicación del diseño",
  "objetos": [
    {
      "shape": "VehicleSeat",
      "size": {"X": 4, "Y": 1, "Z": 6},
      "offset": {"X": 0, "Y": 0, "Z": 0},
      "color": {"R": 0.8, "G": 0.1, "B": 0.1},
      "material": "Metal",
      "anchored": false,
      "transparency": 0,
      "can_collide": true,
      "has_sound": false,
      "sound_id": "rbxassetid://0"
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
            raise ValueError("No se encontraron llaves JSON válidas.")

    except Exception as e:
        print("--- ERROR EN RENDER ---")
        traceback.print_exc()
        return jsonify({
            "reasoning": "Respaldo por error corregido.",
            "objetos": [
                {
                  "shape": "VehicleSeat",
                  "size": {"X": 4, "Y": 1, "Z": 6},
                  "offset": {"X": 0, "Y": 0, "Z": 0},
                  "color": {"R": 1, "G": 0, "B": 0},
                  "material": "Metal",
                  "anchored": False,
                  "transparency": 0,
                  "can_collide": True,
                  "has_sound": False,
                  "sound_id": "rbxassetid://0"
                }
            ]
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
