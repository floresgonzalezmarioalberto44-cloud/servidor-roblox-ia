import os
import json
import traceback
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Usamos gemini-1.5-flash con configuración de temperatura para fomentar la creatividad lógica
model = genai.GenerativeModel('models/gemini-1.5-flash')

PROMPT_SISTEMA = """
Eres el motor de IA experto en lógica, diseño y scripting de Roblox Studio. 
Analiza detalladamente la petición del usuario. Piensa qué tipo de objeto quiere, qué color tendría, qué forma se adapta mejor (Block, Ball, Cylinder, Wedge), si necesita iluminación, un script simple en Luau (como rotar, parpadear o reaccionar) y si requiere un ID de sonido de Roblox (SoundId).

DEBES responder ÚNICAMENTE con un objeto JSON válido, sin bloques de código markdown, sin comillas invertidas y sin texto adicional fuera del JSON.

Estructura JSON exacta obligatoria:
{
  "reasoning": "Explicación detallada de por qué elegiste esta forma, color, script o sonido basado en la petición del usuario",
  "action": "create",
  "shape": "Block",
  "size": {"X": 4, "Y": 2, "Z": 4},
  "position": {"X": 0, "Y": 0, "Z": 0},
  "color": {"R": 0.1, "G": 0.8, "B": 0.3},
  "material": "SmoothPlastic",
  "has_light": false,
  "light_details": {"type": "PointLight", "brightness": 2, "color": {"R": 1, "G": 1, "B": 1}},
  "has_script": false,
  "script_code": "",
  "has_sound": false,
  "sound_id": "rbxassetid://0"
}
"""

@app.route('/')
def home():
    return "Servidor activo y analizando."

@app.route('/construir', methods=['POST'])
def construir():
    # Respaldo dinámico neutral por si ocurre un fallo crítico de red con la API
    fallback_json = {
        "reasoning": "Respaldo analítico por fallo temporal de la IA.",
        "action": "create",
        "shape": "Block",
        "size": {"X": 4, "Y": 4, "Z": 4},
        "position": {"X": 0, "Y": 0, "Z": 0},
        "color": {"R": 0.5, "G": 0.5, "B": 0.5},
        "material": "SmoothPlastic",
        "has_light": False,
        "light_details": {"type": "PointLight", "brightness": 2, "color": {"R": 1, "G": 1, "B": 1}},
        "has_script": False,
        "script_code": "",
        "has_sound": False,
        "sound_id": "rbxassetid://0"
    }

    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify(fallback_json), 200

        prompt_usuario = data['prompt']
        
        # Llamada a Gemini pidiendo que analice la orden con el system prompt estricto
        response = model.generate_content(
            f"{PROMPT_SISTEMA}\n\nPetición exacta del usuario: {prompt_usuario}",
            generation_config={"temperature": 0.7}
        )
        
        texto = response.text.strip() if response and hasattr(response, 'text') else ""

        # Extracción segura del JSON delimitado por llaves
        inicio = texto.find('{')
        fin = texto.rfind('}')
        
        if inicio != -1 and fin != -1 and fin > inicio:
            json_str = texto[inicio:fin+1]
            json_respuesta = json.loads(json_str)
            return jsonify(json_respuesta), 200
        else:
            return jsonify(fallback_json), 200

    except Exception as e:
        print("EXCEPCIÓN INTERNA CAPTURADA:")
        traceback.print_exc()
        return jsonify(fallback_json), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
