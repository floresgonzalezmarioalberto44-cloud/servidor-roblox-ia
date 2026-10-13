import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configuración de la API Key
API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

PROMPT_SISTEMA = """
Eres la mente inteligente de un NPC constructor en Roblox. Tu objetivo es analizar de forma lógica cualquier petición del usuario y decidir ingeniosamente qué construir y qué scripts o efectos necesita.

INSTRUCCIONES DE RAZONAMIENTO LOGICO:
1. Analiza el objeto pedido: ¿Qué forma física tiene? ¿De qué material y color debería ser por naturaleza?
2. Razona sobre la funcionalidad: 
   - Si el usuario pide algo interactivo (ej. un carro, una puerta, un árbol mágico, un botón), PIENSA qué script necesita para funcionar (ej. controles de conducción, crecer, abrir/cerrar, emitir luz).
   - Si el objeto no necesita funcionalidad por defecto pero el usuario la pide implícitamente o explícitamente, invéntale un script lógico.
   - Si es algo meramente decorativo, decide no ponerle script.
3. Genera un código Lua de Roblox simple pero totalmente funcional en la propiedad "script_code" cuando aplique.

RESPONDE ÚNICAMENTE EN FORMATO JSON ESTRICTO (sin ```json ni texto adicional) con esta estructura:

{
  "reasoning": "Breve explicación de por qué elegiste esta forma, color, material y si requiere script o no.",
  "action": "create",
  "shape": "Block" | "Ball" | "Cylinder" | "Wedge",
  "size": {"X": número, "Y": número, "Z": número},
  "position": {"X": 0, "Y": 5, "Z": -10},
  "color": {"R": número (0-1), "G": número (0-1), "B": número (0-1)},
  "material": "SmoothPlastic" | "Wood" | "Neon" | "Metal" | "Grass" | "Glass" | "Brick",
  "has_light": true | false,
  "light_details": {"type": "PointLight", "brightness": 3, "color": {"R": 1, "G": 1, "B": 1}},
  "has_script": true | false,
  "script_code": "-- Código Lua funcional para Roblox aquí si has_script es true"
}
"""

@app.route('/')
def home():
    return "Servidor IA del NPC Constructor activo."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "No se recibió ninguna orden"}), 400

        prompt_usuario = data['prompt']
        
        # Le pedimos a Gemini que razone sobre la orden
        prompt_completo = f"{PROMPT_SISTEMA}\n\nOrden a analizar: '{prompt_usuario}'"
        response = model.generate_content(prompt_completo)
        
        # Limpieza de markdown para recibir JSON puro
        texto = response.text.strip()
        if texto.startswith("```json"):
            texto = texto[7:]
        if texto.startswith("```"):
            texto = texto[3:]
        if texto.endswith("```"):
            texto = texto[:-3]
        texto = texto.strip()

        # Validar el JSON procesado por la IA
        json_respuesta = json.loads(texto)
        return jsonify(json_respuesta), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
