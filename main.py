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
Eres un motor JSON para Roblox Studio. Responde ÚNICAMENTE con un objeto JSON válido, sin bloques markdown ni texto adicional. 
Diseña una construcción lógica compuesta por una lista de objetos ("objetos"). Por ejemplo, si piden un árbol, haz un cilindro marrón para el tronco y una esfera verde para la copa.

Estructura obligatoria exacta:
{
  "reasoning": "Explicación de la construcción",
  "objetos": [
    {
      "shape": "Cylinder",
      "size": {"X": 2, "Y": 6, "Z": 2},
      "offset": {"X": 0, "Y": 3, "Z": 0},
      "color": {"R": 0.4, "G": 0.2, "B": 0.1},
      "material": "Wood",
      "anchored": true,
      "transparency": 0,
      "can_collide": true,
      "has_light": false,
      "has_particles": false,
      "has_sound": false,
      "sound_id": "rbxassetid://0",
      "has_script": false,
      "script_code": ""
    },
    {
      "shape": "Ball",
      "size": {"X": 6, "Y": 6, "Z": 6},
      "offset": {"X": 0, "Y": 7, "Z": 0},
      "color": {"R": 0.1, "G": 0.7, "B": 0.2},
      "material": "Grass",
      "anchored": true,
      "transparency": 0,
      "can_collide": true,
      "has_light": false,
      "has_particles": false,
      "has_sound": false,
      "sound_id": "rbxassetid://0",
      "has_script": false,
      "script_code": ""
    }
  ]
}
"""

@app.route('/')
def home():
    return "Servidor activo."

@app.route('/construir', methods=['POST'])
def construir():
    fallback_json = {
        "reasoning": "Respaldo seguro de emergencia por defecto.",
        "objetos": [
            {
              "shape": "Block",
              "size": {"X": 4, "Y": 4, "Z": 4},
              "offset": {"X": 0, "Y": 2, "Z": 0},
              "color": {"R": 0.4, "G": 0.2, "B": 0.1},
              "material": "Wood",
              "anchored": True,
              "transparency": 0,
              "can_collide": True,
              "has_light": False,
              "has_particles": False,
              "has_sound": False,
              "sound_id": "rbxassetid://0",
              "has_script": False,
              "script_code": ""
            },
            {
              "shape": "Ball",
              "size": {"X": 5, "Y": 5, "Z": 5},
              "offset": {"X": 0, "Y": 6, "Z": 0},
              "color": {"R": 0.1, "G": 0.8, "B": 0.2},
              "material": "Grass",
              "anchored": True,
              "transparency": 0,
              "can_collide": True,
              "has_light": False,
              "has_particles": False,
              "has_sound": False,
              "sound_id": "rbxassetid://0",
              "has_script": False,
              "script_code": ""
            }
        ]
    }

    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear objeto') if data else 'crear objeto'

        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición: {prompt_usuario}")
        texto = response.text.strip() if response and hasattr(response, 'text') else ""

        inicio = texto.find('{')
        fin = texto.rfind('}')
        
        if inicio != -1 and fin != -1 and fin > inicio:
            json_str = texto[inicio:fin+1]
            json_respuesta = json.loads(json_str)
            
            # Validar que contenga la lista de objetos
            if "objetos" not in json_respuesta or not isinstance(json_respuesta["objetos"], list):
                return jsonify(fallback_json), 200
                
            return jsonify(json_respuesta), 200
        else:
            return jsonify(fallback_json), 200

    except Exception as e:
        print("ERROR EN RENDER:")
        traceback.print_exc()
        return jsonify(fallback_json), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
