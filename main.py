import os
import json
import traceback
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

PROMPT_SISTEMA = """
Eres un motor estricto de JSON para Roblox Studio. Analiza la petición del usuario y diseña una construcción dinámica compuesta por múltiples piezas ("objetos").
Si piden un vehículo, incluye un "VehicleSeat" y partes móviles. Si piden un árbol, incluye un cilindro marrón y una esfera verde. 

Devuelve ÚNICAMENTE un objeto JSON válido. No uses bloques markdown (```json), no uses comillas invertidas ni texto fuera del JSON.

Estructura obligatoria exacta:
{
  "reasoning": "Descripción de la construcción",
  "objetos": [
    {
      "shape": "Block",
      "size": {"X": 4, "Y": 2, "Z": 4},
      "offset": {"X": 0, "Y": 0, "Z": 0},
      "color": {"R": 0.5, "G": 0.5, "B": 0.5},
      "material": "SmoothPlastic",
      "anchored": true,
      "transparency": 0,
      "can_collide": true
    }
  ]
}
"""

@app.route('/')
def home():
    return "Servidor activo y sin respaldos."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear bloque') if data else 'crear bloque'

        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición del usuario: {prompt_usuario}")
        texto = response.text.strip()
        print("TEXTO RECIBIDO DE GEMINI:", texto)

        # Limpieza de markdown si el modelo llega a incluirlo por error
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
        print("--- ERROR DIRECTO EN RENDER ---")
        traceback.print_exc()
        # Si falla, devolvemos el error exacto en el JSON en lugar de un respaldo oculto
        return jsonify({
            "reasoning": "Error interno del servidor: " + str(e),
            "objetos": []
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
