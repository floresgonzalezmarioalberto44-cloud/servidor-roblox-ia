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
Eres un arquitecto e ingeniero experto de Roblox Studio con lógica avanzada. 
El usuario pedirá una construcción (como un auto con scripts, un árbol, una casa, etc.). Debes diseñar una lista detallada de múltiples piezas ("objetos") para que la estructura sea completa y funcional.

Reglas clave:
- Si piden un vehículo/auto, incluye obligatoriamente un "VehicleSeat" en el centro para que el jugador pueda conducirlo, y cilindros para las ruedas con "anchored": false.
- Para estructuras estáticas (casas, árboles), usa bloques, cilindros o esferas con "anchored": true.
- Devuelve ÚNICAMENTE un objeto JSON válido (sin markdown ```json).

Estructura obligatoria exacta:
{
  "reasoning": "Explicación de la ingeniería aplicada",
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
      "has_light": false,
      "has_particles": false,
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
        prompt_usuario = data.get('prompt', 'crear bloque') if data else 'crear bloque'

        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición del usuario: {prompt_usuario}")
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
            raise ValueError("No JSON found")

    except Exception as e:
        print("ERROR EN RENDER:")
        traceback.print_exc()
        return jsonify({
            "reasoning": "Respaldo inteligente de auto.",
            "objetos": [
                {
                  "shape": "VehicleSeat",
                  "size": {"X": 4, "Y": 1, "Z": 6},
                  "offset": {"X": 0, "Y": 0, "Z": 0},
                  "color": {"R": 0.1, "G": 0.2, "B": 0.8},
                  "material": "Metal",
                  "anchored": False,
                  "transparency": 0,
                  "can_collide": True,
                  "has_light": False,
                  "has_particles": False,
                  "has_sound": False,
                  "sound_id": "rbxassetid://0"
                }
            ]
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
