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
Eres un arquitecto, ingeniero físico y scripter experto de Roblox Studio con razonamiento lógico avanzado. 
Analiza la petición del usuario. Si te pide un objeto dinámico (como un coche, una puerta automática, un objeto flotante o algo que deba moverse), diseña las piezas correspondientes y **piensa críticamente en la física**:
- Las piezas estáticas o estructurales principales pueden ir con "anchored": true.
- Las piezas móviles, ruedas de autos, o partes controladas por scripts deben ir obligatoriamente con "anchored": false para que la física y los scripts (como VehicleSeat, bodaview, o Position/CFrame changes) funcionen perfectamente.
- Limita la cantidad de objetos a un máximo de 1000 por orden.

Devuelve ÚNICAMENTE un objeto JSON válido con la siguiente estructura. No uses bloques markdown ni comillas invertidas:
{
  "reasoning": "Análisis lógico detallado de la ingeniería, física y scripts necesarios",
  "objetos": [
    {
      "shape": "Block",
      "size": {"X": 6, "Y": 2, "Z": 10},
      "offset": {"X": 0, "Y": 0, "Z": 0},
      "color": {"R": 0.1, "G": 0.4, "B": 0.9},
      "material": "Metal",
      "anchored": true,
      "transparency": 0,
      "can_collide": true,
      "has_light": false,
      "light_color": {"R": 1, "G": 1, "B": 1},
      "light_brightness": 2,
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
    return "Servidor activo con ingeniería y lógica avanzada."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear bloque') if data else 'crear bloque'

        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición del usuario: {prompt_usuario}")
        texto = response.text.strip()

        inicio = texto.find('{')
        fin = texto.rfind('}')
        
        if inicio != -1 and fin != -1 and fin > inicio:
            json_str = texto[inicio:fin+1]
            json_respuesta = json.loads(json_str)
            
            if "objetos" in json_respuesta and isinstance(json_respuesta["objetos"], list):
                if len(json_respuesta["objetos"]) > 1000:
                    json_respuesta["objetos"] = json_respuesta["objetos"][:1000]

            return jsonify(json_respuesta), 200
        else:
            raise ValueError("Formato JSON no encontrado")

    except Exception as e:
        print("ERROR EN RENDER:")
        traceback.print_exc()
        return jsonify({
            "reasoning": "Respaldo seguro de emergencia.",
            "objetos": [
                {
                  "shape": "Block",
                  "size": {"X": 4, "Y": 4, "Z": 4},
                  "offset": {"X": 0, "Y": 0, "Z": 0},
                  "color": {"R": 0.8, "G": 0.2, "B": 0.2},
                  "material": "SmoothPlastic",
                  "anchored": True,
                  "transparency": 0,
                  "can_collide": True,
                  "has_light": False,
                  "light_color": {"R": 1, "G": 1, "B": 1},
                  "light_brightness": 2,
                  "has_particles": False,
                  "has_sound": False,
                  "sound_id": "rbxassetid://0",
                  "has_script": False,
                  "script_code": ""
                }
            ]
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
