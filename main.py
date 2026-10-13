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
    return "Servidor activo y seguro."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'casa') if data else 'casa'

        print(f"Petición directa del usuario: {prompt_usuario}")

        prompt_estricto = (
            'Actúa como un generador experto de estructuras 3D para Roblox Studio.\n'
            'El usuario ha escrito exactamente esta solicitud: "' + prompt_usuario + '"\n\n'
            'Tu tarea es diseñar este objeto desglosado en MÚLTIPLES piezas (bloques, cilindros, esferas, cuñas).\n'
            'Define con precisión milimétrica para cada pieza:\n'
            '- shape (Block, Cylinder, Ball, Wedge)\n'
            '- size (X, Y, Z)\n'
            '- offset relativas desde el centro de la construcción (X, Y, Z)\n'
            '- color RGB (valores de 0.0 a 1.0)\n'
            '- material de Roblox (Wood, Metal, SmoothPlastic, Glass, Neon, Slate, etc.)\n'
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
            '      "size": {"X": 6, "Y": 4, "Z": 1},\n'
            '      "offset": {"X": 0, "Y": 2, "Z": -3},\n'
            '      "color": {"R": 0.8, "G": 0.8, "B": 0.8},\n'
            '      "material": "Slate",\n'
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
        print("--- EXCEPCIÓN CONTROLADA EN EL SERVIDOR ---")
        traceback.print_exc()
        
        # Estructura múltiple de emergencia en caso de que la IA tarde o falle, con código 200 para Roblox
        return jsonify({
            "reasoning": "Estructura generada por contingencia de API: " + str(e),
            "objetos": [
                {
                  "shape": "Block",
                  "size": {"X": 8, "Y": 4, "Z": 1},
                  "offset": {"X": 0, "Y": 2, "Z": -4},
                  "color": {"R": 0.7, "G": 0.7, "B": 0.7},
                  "material": "Slate",
                  "anchored": True,
                  "transparency": 0,
                  "can_collide": True
                },
                {
                  "shape": "Block",
                  "size": {"X": 8, "Y": 4, "Z": 1},
                  "offset": {"X": 0, "Y": 2, "Z": 4},
                  "color": {"R": 0.7, "G": 0.7, "B": 0.7},
                  "material": "Slate",
                  "anchored": True,
                  "transparency": 0,
                  "can_collide": True
                },
                {
                  "shape": "Block",
                  "size": {"X": 1, "Y": 4, "Z": 8},
                  "offset": {"X": -4, "Y": 2, "Z": 0},
                  "color": {"R": 0.7, "G": 0.7, "B": 0.7},
                  "material": "Slate",
                  "anchored": True,
                  "transparency": 0,
                  "can_collide": True
                },
                {
                  "shape": "Block",
                  "size": {"X": 1, "Y": 4, "Z": 8},
                  "offset": {"X": 4, "Y": 2, "Z": 0},
                  "color": {"R": 0.7, "G": 0.7, "B": 0.7},
                  "material": "Slate",
                  "anchored": True,
                  "transparency": 0,
                  "can_collide": True
                },
                {
                  "shape": "Wedge",
                  "size": {"X": 10, "Y": 3, "Z": 10},
                  "offset": {"X": 0, "Y": 5.5, "Z": 0},
                  "color": {"R": 0.6, "G": 0.1, "B": 0.1},
                  "material": "Wood",
                  "anchored": True,
                  "transparency": 0,
                  "can_collide": True
                }
            ]
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
