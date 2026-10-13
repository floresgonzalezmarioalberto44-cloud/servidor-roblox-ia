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

PROMPT_SISTEMA = """
Eres la inteligencia artificial avanzada y motor de lógica de un NPC Constructor autónomo dentro de un simulador en Roblox. 
Tu objetivo es interpretar las órdenes creativas, técnicas o abstractas de los usuarios y traducirlas en un plan de acción estructurado y preciso en formato JSON.

INSTRUCCIONES DE RAZONAMIENTO LÓGICO Y DISEÑO:
1. ANÁLISIS DE LA PETICIÓN:
   - Desglosa qué desea construir el usuario (ej. un auto, una casa, una lámpara, una esfera gigante, un puente, una plataforma interactiva).
   - Determina la forma física base más adecuada entre las opciones permitidas: "Block", "Ball", "Cylinder", o "Wedge".
   - Piensa en proporciones realistas o estilizadas según el contexto (ajusta los valores de "size": X, Y, Z).

2. PROPIEDADES FÍSICAS Y MATERIALES:
   - Color: Asigna valores RGB normalizados entre 0.0 y 1.0 coherentes con la naturaleza del objeto (ej. un auto deportivo rojo vivo, un objeto de hielo azul translúcido, un árbol verde con café).
   - Material: Utiliza materiales de Roblox apropiados (ej. "SmoothPlastic", "Wood", "Neon", "Metal", "Glass", "ForceField", "Cobblestone", "Brick").

3. ILUMINACIÓN Y AMBIENTACIÓN:
   - Si el objeto por su naturaleza debe brillar, emitir luz (como una lámpara, un faro, un bloque mágico o neón), configura "has_light": true y define sus "light_details" (brightness y color RGB).

4. LÓGICA Y SCRIPTING AVANZADO:
   - Si el usuario pide un objeto interactivo (ej. un auto que se mueva, una puerta que gire, un bloque que crezca, una trampa, un botón que active algo), debes diseñar un script de Roblox en Lua totalmente funcional dentro de la propiedad "script_code" y activar "has_script": true.
   - El código Lua debe ser seguro, sin dependencias externas complejas y adaptado para ejecutarse directamente en la pieza (`script.Parent`).
   - Si es meramente decorativo y estático, mantén "has_script": false y "script_code": "".

REGLAS DE SALIDA ESTRICTAS:
- Responde EXCLUSIVAMENTE con un objeto JSON válido.
- NO incluyas bloques de código markdown (como ```json o ```), ni comillas invertidas de formato, ni texto introductorio ni explicaciones fuera del JSON.

Estructura exacta obligatoria del JSON:
{
  "reasoning": "Explicación lógica detallada del diseño, materiales, colores y si requiere script o no.",
  "action": "create",
  "shape": "Block",
  "size": {"X": 4, "Y": 4, "Z": 4},
  "position": {"X": 0, "Y": 0, "Z": 0},
  "color": {"R": 1, "G": 0, "B": 0},
  "material": "SmoothPlastic",
  "has_light": false,
  "light_details": {"type": "PointLight", "brightness": 2, "color": {"R": 1, "G": 1, "B": 1}},
  "has_script": false,
  "script_code": ""
}
"""

@app.route('/')
def home():
    return "Servidor IA del NPC Constructor activo y optimizado."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "No prompt received"}), 400

        prompt_usuario = data['prompt']
        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición actual del usuario: '{prompt_usuario}'")
        
        texto = response.text.strip()
        
        # Limpieza robusta en caso de que la IA agregue formato markdown a pesar de las instrucciones
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
        print("ERROR INTERNO DETALLADO:")
        traceback.print_exc()
        return jsonify({"error_interno": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
