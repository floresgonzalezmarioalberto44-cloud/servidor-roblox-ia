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

# Prompt actualizado para que la IA diseñe formas y escriba código de Roblox (Lua) dinámico
PROMPT_SISTEMA = """
Eres un motor experto de IA y scripting para Roblox Studio. 
Analiza la petición del usuario y devuelve ÚNICAMENTE un objeto JSON válido con la estructura exacta indicada abajo. No agregues texto adicional, explicaciones ni bloques markdown.

Reglas para los scripts:
- Si el usuario pide algo interactivo (ej. que se mueva, cambie de color solo, emita luz especial o reaccione), pon "has_script": true y escribe código Luau válido y seguro dentro de "script_code" (usa script.Parent).
- Si es solo una estructura estática, deja "has_script": false y "script_code": "".

Estructura exacta obligatoria:
{
  "reasoning": "Breve explicación de la lógica aplicada",
  "action": "create",
  "shape": "Block",
  "size": {"X": 4, "Y": 2, "Z": 4},
  "position": {"X": 0, "Y": 0, "Z": 0},
  "color": {"R": 0.2, "G": 0.6, "B": 1},
  "material": "SmoothPlastic",
  "has_light": false,
  "light_details": {"type": "PointLight", "brightness": 2, "color": {"R": 1, "G": 1, "B": 1}},
  "has_script": false,
  "script_code": ""
}
"""

@app.route('/')
def home():
    return "Servidor activo."

@app.route('/construir', methods=['POST'])
def construir():
    fallback_json = {
        "reasoning": "Pieza de respaldo por defecto.",
        "action": "create",
        "shape": "Block",
        "size": {"X": 4, "Y": 2, "Z": 4},
        "position": {"X": 0, "Y": 0, "Z": 0},
        "color": {"R": 1, "G": 0, "B": 0},
        "material": "SmoothPlastic",
        "has_light": False,
        "light_details": {"type": "PointLight", "brightness": 2, "color": {"R": 1, "G": 1, "B": 1}},
        "has_script": False,
        "script_code": ""
    }

    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify(fallback_json), 200

        prompt_usuario = data['prompt']
        
        try:
            response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición del usuario: {prompt_usuario}")
            texto = response.text.strip() if response and hasattr(response, 'text') else ""
        except Exception:
            texto = ""

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
