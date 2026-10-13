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

@app.route('/')
def home():
    return "Servidor activo y sin respaldos."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear objeto') if data else 'crear objeto'

        print(f"Petición directa del usuario: {prompt_usuario}")

        # Prompt estricto que utiliza DIRECTAMENTE el texto que mandaste desde Roblox
        prompt_sistema = f"""
Eres un motor estricto de arquitectura 3D para Roblox Studio. 
El usuario ha pedido exactamente lo siguiente: "{prompt_usuario}".

Diseña una construcción detallada compuesta por múltiples piezas ("objetos") que represente fielmente esa petición (por ejemplo, si pide una mesa, haz la tabla y cuatro patas; si pide un árbol, haz tronco y copa; si pide un carro, haz chasis, ruedas y asiento).

Devuelve ÚNICAMENTE un objeto JSON válido. No uses bloques markdown (```json), no uses comillas invertidas ni texto fuera del JSON.

Estructura obligatoria exacta:
{{
  "reasoning": "Descripción de la construcción",
  "objetos": [
    {{
      "shape": "Block",
      "size": {{"X": 4, "Y": 1, "Z": 4}},
      "offset": {{"X": 0, "Y": 1, "Z": 0}},
      "color": {{"R": 0.5, "G": 0.3, "B": 0.1}},
      "material": "Wood",
      "anchored": true,
      "transparency": 0,
      "can_collide": true
    }}
  ]
}}
"""

        response = model.generate_content(prompt_sistema)
        texto = response.text.strip()
        print("TEXTO CRUDO DE GEMINI:", texto)

        # Limpieza de markdown si el modelo lo llega a incluir
        if "```" in texto:
            partes = texto.split("```")
            for parte in partes:
                parte_limpia = parte.strip()
                if parte_limpia.startswith("json"):
                    parte_limpia = parte_limpia[4:].strip()
                if "{" in parte_limpia and "}" in parte_limpia:
                    texto = parte_limpia
                    break

        inicio = texto.find('{')
        fin = texto.rfind('}')
        
        if inicio != -1 and fin != -1 and fin > inicio:
            json_str = texto[inicio:fin+1]
            json_respuesta = json.loads(json_str)
            return jsonify(json_respuesta), 200
        else:
            raise ValueError("La respuesta de la IA no contiene un JSON válido.")

    except Exception as e:
        print("--- ERROR REAL EN EL SERVIDOR ---")
        traceback.print_exc()
        # Sin respaldos ocultos: si falla, devolvemos el error exacto para verlo en Roblox
        return jsonify({
            "reasoning": "Error: " + str(e),
            "objetos": []
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
