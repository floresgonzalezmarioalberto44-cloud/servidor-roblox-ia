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
Eres un motor JSON para un NPC de Roblox. Responde ÚNICAMENTE con un JSON válido, sin bloques de código markdown, sin comillas invertidas y sin texto adicional. 
Estructura exacta obligatoria:
{
  "reasoning": "Breve explicación",
  "action": "create",
  "shape": "Block",
  "size": {"X": 4, "Y": 4, "Z": 4},
  "position": {"X": 0, "Y": 0, "Z": 0},
  "color": {"R": 0, "G": 0, "B": 1},
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
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "No prompt"}), 400

        prompt_usuario = data['prompt']
        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición: {prompt_usuario}")
        
        texto = response.text.strip()
        if "```" in texto:
            partes = texto.split("```")
            for p in partes:
                p_limpio = p.strip()
                if p_limpio.startswith("json"):
                    p_limpio = p_limpio[4:].strip()
                if p_limpio.startswith("{") and p_limpio.endswith("}"):
                    texto = p_limpio
                    break

        json_respuesta = json.loads(texto)
        return jsonify(json_respuesta), 200

    except Exception as e:
        # Esto imprimirá el error completo en los logs de Render
        print("ERROR INTERNO DETALLADO:")
        traceback.print_exc()
        return jsonify({"error_interno": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
