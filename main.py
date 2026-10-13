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
    return "Servidor directo activo."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', '') if data else ''

        print(f"Petición directa del usuario: {prompt_usuario}")

        # Prompt armado con concatenación normal para evitar errores de sintaxis con las llaves
        prompt_estricto = (
            'Actúa como un generador experto de estructuras 3D para Roblox Studio.\n'
            'El usuario ha escrito exactamente esta solicitud: "' + prompt_usuario + '"\n\n'
            'Tu tarea es diseñar este objeto desglosado en MÚLTIPLES piezas (bloques, cilindros, esferas, cuñas, o VehicleSeat si es un vehículo).\n'
            'Define con precisión milimétrica para cada pieza:\n'
            '- shape (Block, Cylinder, Ball, Wedge, VehicleSeat)\n'
            '- size (X, Y, Z)\n'
            '- offset relativas desde el centro de la construcción (X, Y, Z)\n'
            '- color RGB (valores de 0.0 a 1.0)\n'
            '- material de Roblox (Wood, Metal, SmoothPlastic, Glass, Neon, etc.)\n'
            '- anchored (true/false)\n'
            '- transparency (0 a 1)\n'
            '- can_collide (true/false)\n\n'
            'Devuelve ÚNICAMENTE un objeto JSON válido. No uses bloques markdown (```json), no uses comillas invertidas ni texto adicional fuera del JSON.\n\n'
            'Estructura obligatoria exacta:\n'
            '{\n'
            '  "reasoning": "Descripción detallada de la construcción generada",\n'
            '  "objetos": [\n'
            '    {\n'
            '      "shape": "Block",\n'
            '      "size": {"X": 4, "Y": 1, "Z": 4},\n'
            '      "offset": {"X": 0, "Y": 0, "Z": 0},\n'
            '      "color": {"R": 0.5, "G": 0.3, "B": 0.1},\n'
            '      "material": "Wood",\n'
            '      "anchored": true,\n'
            '      "transparency": 0,\n'
            '      "can_collide": true\n'
            '    }\n'
            '  ]\n'
            '}'
        )

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
        return jsonify({
            "reasoning": "Error interno: " + str(e),
            "objetos": []
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
