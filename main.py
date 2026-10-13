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
Eres un motor de arquitectura para Roblox Studio. Analiza la petición del usuario y devuelve ÚNICAMENTE un objeto JSON válido con múltiples piezas ("objetos").
Si piden una mesa, diseña la parte superior y cuatro patas. Si piden un árbol, incluye tronco y copa.

Estructura obligatoria exacta:
{
  "reasoning": "Descripción del diseño",
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
    return "Servidor activo."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear objeto') if data else 'crear objeto'

        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición: {prompt_usuario}")
        texto = response.text.strip()
        print("RESPUESTA CRUDA DE GEMINI:", texto)

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
            raise ValueError("La respuesta no contiene un JSON válido.")

    except Exception as e:
        print("--- ERROR REAL EN RENDER ---")
        traceback.print_exc()
        # Si ocurre un error, devolvemos el error exacto como JSON para ver qué pasa en Roblox
        return jsonify({
            "reasoning": "Error: " + str(e),
            "objetos": []
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
