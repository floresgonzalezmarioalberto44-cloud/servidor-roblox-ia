import os
from flask import Flask, jsonify, request
import google.generativeai as genai
import json

app = Flask(__name__)

# Configuramos la API Key de Google de forma segura desde las variables de Render
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Usamos Gemini 1.5 Flash para máxima velocidad y precisión
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/", methods=["GET"])
def home():
    return "¡El servidor con Gemini 1.5 Flash está activo y listo para construir! 🚀", 200

@app.route("/process-action", methods=["POST"])
def process_action():
    try:
        data = request.json
        npc_prompt = data.get("prompt", "")
        
        print(f"Procesando orden con Gemini: {npc_prompt}")
        
        # Instrucción maestra para que Gemini actúe como motor lógico y arquitecto de Roblox
        prompt_sistema = f"""
        Eres el motor de IA de un sistema de construcción por NPCs en Roblox. 
        El usuario ha pedido el siguiente objeto o estructura: "{npc_prompt}".
        
        Analiza inteligentemente:
        1. ¿Qué piezas (bloques, cilindros, esferas, cuñas) componen esta estructura paso a paso con sus tamaños, colores (RGB de 0 a 1), posiciones relativas (X, Y, Z) y rotaciones?
        2. ¿Este objeto requiere interactividad o físicas especiales (ej. una pelota que se patea, un vehículo que se conduce, un trampolín que impulsa)? Si es puramente estático (como un muro, una casa o un árbol), "requires_script" debe ser falso.
        3. Si requiere script, redacta un código en Lua robusto para Roblox, incluyendo lógica de proximidad (ej. los botones en pantalla solo funcionan si el jugador está cerca) y soporte universal para PC, Móvil y Consola.

        DEBES responder EXCLUSIVAMENTE con un objeto JSON válido, sin textos extra ni formato markdown adicional, siguiendo esta estructura exacta:
        {{
            "action": "build_complex_sequence",
            "description": "{npc_prompt}",
            "parts": [
                {{
                    "shape": "Part",
                    "size": {{"X": 4, "Y": 1, "Z": 4}},
                    "color": {{"R": 0.5, "G": 0.5, "B": 0.5}},
                    "position": {{"X": 0, "Y": 0.5, "Z": 0}},
                    "rotation": {{"X": 0, "Y": 0, "Z": 0}}
                }}
            ],
            "requires_script": false,
            "script_code": ""
        }}
        """
        
        # Llamamos a Gemini para que piense y genere la respuesta estructurada
        response = model.generate_content(prompt_sistema)
        texto_respuesta = response.text.strip()
        
        # Limpiamos posibles etiquetas de bloque de código que ponga la IA por error
        if texto_respuesta.startswith("```json"):
            texto_respuesta = texto_respuesta[7:]
        if texto_respuesta.endswith("```"):
            texto_respuesta = texto_respuesta[:-3]
            
        json_resultado = json.loads(texto_respuesta.strip())
        return jsonify(json_resultado), 200

    except Exception as e:
        # En caso de cualquier detalle, devolvemos un respaldo seguro para que el juego no falle
        fallback = {
            "action": "build_complex_sequence",
            "description": data.get("prompt", "Objeto"),
            "parts": [
                {"shape": "Part", "size": {"X": 4, "Y": 4, "Z": 4}, "color": {"R": 0.2, "G": 0.6, "B": 1}, "position": {"X": 0, "Y": 2, "Z": 0}}
            ],
            "requires_script": False,
            "script_code": ""
        }
        return jsonify(fallback), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
