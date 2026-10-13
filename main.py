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
Eres un motor experto en diseño y arquitectura 3D para Roblox Studio. 
Analiza la petición del usuario y genera un diseño detallado compuesto por múltiples piezas ("objetos").
- Si piden una mesa: crea una tabla superior horizontal grande y 4 patas cilíndricas o bloques de soporte en las esquinas.
- Si piden un árbol: crea un tronco cilíndrico marrón y una copa esférica verde o múltiples esferas de follaje.
- Si piden un carro/auto: crea un asiento de tipo "VehicleSeat" en el centro, una base de chasis y 4 ruedas cilíndricas.
- Si piden cualquier otra cosa: diseña las piezas estructurales necesarias de forma creativa y coherente.

Devuelve ÚNICAMENTE un objeto JSON válido. No uses bloques markdown (```json ... ```), no uses comillas invertidas ni texto introductorio fuera del JSON.

Estructura obligatoria exacta:
{
  "reasoning": "Breve explicación de la construcción generada",
  "objetos": [
    {
      "shape": "Block",
      "size": {"X": 4, "Y": 1, "Z": 4},
      "offset": {"X": 0, "Y": 1, "Z": 0},
      "color": {"R": 0.5, "G": 0.3, "B": 0.1},
      "material": "Wood",
      "anchored": true,
      "transparency": 0,
      "can_collide": true
    }
  ]
}
"""

@app.route('/')
def home():
    return "Servidor activo y listo para diseñar."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', 'crear objeto') if data else 'crear objeto'

        print(f"Generando diseño personalizado para: {prompt_usuario}")
        
        response = model.generate_content(f"{PROMPT_SISTEMA}\n\nPetición exacta del usuario: {prompt_usuario}")
        texto = response.text.strip()
        print("TEXTO CRUDO DE GEMINI:", texto)

        # Limpieza profunda de formato markdown por si la IA insiste en incluirlo
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
            raise ValueError("La respuesta de la IA no contiene una estructura JSON reconocible.")

    except Exception as e:
        print("--- ERROR AL PROCESAR CON LA IA ---")
        traceback.print_exc()
        
        # En caso de fallo crítico en el parseo, devolvemos un JSON de emergencia dinámico que avise en el reasoning
        return jsonify({
            "reasoning": "Error de parseo: " + str(e),
            "objetos": [
                {
                  "shape": "Block",
                  "size": {"X": 4, "Y": 2, "Z": 4},
                  "offset": {"X": 0, "Y": 1, "Z": 0},
                  "color": {"R": 1, "G": 0, "B": 0},
                  "material": "SmoothPlastic",
                  "anchored": True,
                  "transparency": 0,
                  "can_collide": True
                }
            ]
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
