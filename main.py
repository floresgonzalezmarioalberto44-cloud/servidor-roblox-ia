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
Eres un arquitecto e ingeniero experto de Roblox Studio. Diseña una construcción detallada con múltiples piezas ("objetos") basada en la petición del usuario.
Si piden un auto, incluye un VehicleSeat y varias piezas. Si piden un árbol, incluye tronco y hojas.

Devuelve ÚNICAMENTE un objeto JSON válido, sin bloques markdown, sin ```json y sin texto adicional.

Estructura obligatoria exacta:
{
  "reasoning": "Explicación del diseño",
  "objetos": [
    {
      "shape": "Block",
      "size": {"X": 4, "Y": 2, "Z": 6},
      "offset": {"X": 0, "Y": 0, "Z": 0},
      "color": {"R": 0.2, "G": 0.2, "B": 0.2},
      "material": "Metal",
      "anchored": true,
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
        
        if not response or not hasattr(response, 'text'):
            raise ValueError("La respuesta de la IA está vacía.")
            
        texto = response.text.strip()
        print("TEXTO BRUTO DE LA IA:", texto) # Esto saldrá en los logs de Render para depurar

        # Limpiar markdown por si acaso
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
            raise ValueError("No se encontraron llaves JSON válidas en la respuesta.")

    except Exception as e:
        print("--- ERROR CRÍTICO CAPTURADO EN RENDER ---")
        traceback.print_exc()
        
        # Respaldo ampliado de múltiples piezas (ej. un auto básico con asiento para que notes que falló pero construya más de 1 pieza)
        return jsonify({
            "reasoning": "Respaldo activo debido a una excepción detectada.",
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
                },
                {
                  "shape": "Block",
                  "size": {"X": 6, "Y": 1, "Z": 8},
                  "offset": {"X": 0, "Y": -1, "Z": 0},
                  "color": {"R": 0, "G": 0, "B": 1},
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
