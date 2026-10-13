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
    return "Servidor directo y sin respaldos activo."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', '') if data else ''

        print(f"Petición directa del usuario: {prompt_usuario}")

        # Prompt 100% directo y enfocado en lo que pide el usuario con múltiples piezas detalladas
        prompt_estricto = f"""
Actúa como un generador experto de estructuras 3D para Roblox Studio.
El usuario ha escrito exactamente esta solicitud: "{prompt_usuario}"

Tu tarea es diseñar este objeto desglosado en MÚLTIPLES piezas (bloques, cilindros, esferas, cuñas, o VehicleSeat si es un vehículo). 
Define con precisión milimétrica para cada pieza:
- shape (Block, Cylinder, Ball, Wedge, VehicleSeat)
- size (X, Y, Z)
- offset relativas desde el centro de la construcción (X, Y, Z)
- color RGB (valores de 0.0 a 1.0)
- material de Roblox (Wood, Metal, SmoothPlastic, Glass, Neon, etc.)
- anchored (true/false)
- transparency (0 a 1)
- can_collide (true/false)

Devuelve ÚNICAMENTE un objeto JSON válido. No uses bloques markdown (```json), no uses comillas invertidas ni texto adicional fuera del JSON.

Estructura obligatoria exacta:
{{
  "reasoning": "Descripción detallada de la construcción generada",
  "objetos": [
    {{
      "shape": "Block",
      "size": {{"X": 4, "Y": 1, "Z": 4}},
      "offset": {{"X": 0, "Y": 0, "Z": 0}},
      "color": {{"R": 0.5, "G": 0.3, "B": 0.1}},
      "material": "Wood",
      "anchored": true,
      "transparency": 0,
      "can_collide": true
    }}
  ]
}
"""

        response = model.generate_content(prompt_estricto)
        texto = response.text.strip()
        print("TEXTO CRUDO DE GEMINI:", texto)

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
        print("--- ERROR DIRECTO EN EL SERVIDOR ---")
        traceback.print_exc()
        # Devolvemos el error real con código 500 para enterarnos exactamente de qué pasa si falla
        return jsonify({
            "reasoning": "Error interno: " + str(e),
            "objetos": []
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
