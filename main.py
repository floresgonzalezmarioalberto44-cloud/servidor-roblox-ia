import os
import json
import traceback
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Configuramos el modelo de forma limpia
model = genai.GenerativeModel('models/gemini-1.5-flash')

@app.route('/')
def home():
    return "Servidor activo y listo."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear un objeto') if data else 'crear un objeto'

        # Prompt ultra directo y estricto
        prompt_completo = f"""
        Eres un generador de JSON estricto para Roblox Studio.
        El usuario pide: "{prompt_usuario}"
        
        Devuelve ÚNICAMENTE un objeto JSON válido (sin explicaciones, sin markdown como ```json). 
        Debe contener una lista llamada "objetos" con las piezas necesarias (máximo 1000).
        Cada objeto debe tener: shape ("Block", "Ball", "Cylinder", "Wedge"), size ({"X", "Y", "Z"}), offset ({"X", "Y", "Z"}), color ({"R", "G", "B"}), material, anchored (true/false), transparency, can_collide, has_light, has_particles, has_sound, sound_id, has_script, script_code.

        Ejemplo de formato:
        {{
          "reasoning": "Explicación breve",
          "objetos": [
            {{
              "shape": "Block",
              "size": {{"X": 4, "Y": 2, "Z": 6}},
              "offset": {{"X": 0, "Y": 0, "Z": 0}},
              "color": {{"R": 1, "G": 0, "B": 0}},
              "material": "Metal",
              "anchored": false,
              "transparency": 0,
              "can_collide": true,
              "has_light": false,
              "has_particles": false,
              "has_sound": false,
              "sound_id": "rbxassetid://0",
              "has_script": false,
              "script_code": ""
            }}
          ]
        }}
        """

        response = model.generate_content(prompt_completo)
        texto = response.text.strip()

        # Limpiar bloques de código markdown si los hubiera
        if texto.startswith("```"):
            texto = texto.split("```")[1]
            if texto.startswith("json"):
                texto = texto[4:]
        texto = texto.strip()

        inicio = texto.find('{')
        fin = texto.rfind('}')
        
        if inicio != -1 and fin != -1 and fin > inicio:
            json_str = texto[inicio:fin+1]
            json_respuesta = json.loads(json_str)
            return jsonify(json_respuesta), 200
        else:
            raise ValueError("No se encontró un JSON válido en la respuesta.")

    except Exception as e:
        print("EXCEPCIÓN EN RENDER:")
        traceback.print_exc()
        
        # Respaldo dinámico si ocurre un error
        return jsonify({
            "reasoning": "Respaldo por excepción interna controlada.",
            "objetos": [
                {
                  "shape": "Block",
                  "size": {"X": 4, "Y": 2, "Z": 6},
                  "offset": {"X": 0, "Y": 0, "Z": 0},
                  "color": {"R": 0, "G": 0.5, "B": 1},
                  "material": "Metal",
                  "anchored": False,
                  "transparency": 0,
                  "can_collide": True,
                  "has_light": False,
                  "has_particles": False,
                  "has_sound": False,
                  "sound_id": "rbxassetid://0",
                  "has_script": True,
                  "script_code": "while true do script.Parent.CFrame = script.Parent.CFrame * CFrame.Angles(0, math.rad(2), 0) task.wait(0.03) end"
                }
            ]
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
