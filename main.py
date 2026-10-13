import os
import json
import traceback
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

API_KEY = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else genai.Client()

@app.route('/')
def home():
    return "Servidor 100% libre de respaldos activo."

@app.route('/construir', methods=['POST'])
def construir():
    try:
        data = request.get_json()
        prompt_usuario = data.get('prompt', '') if data else ''

        print(f"--- NUEVA ORDEN DIRECTA DE USUARIO: {prompt_usuario} ---")

        # Prompt ultra directo: la IA DEBE usar el texto exacto del usuario y crear múltiples piezas variadas
        prompt_estricto = (
            "Eres un motor experto de arquitectura y diseño 3D para Roblox Studio.\n"
            "El usuario ha escrito la siguiente orden exacta: \"" + prompt_usuario + "\"\n\n"
            "Analiza detalladamente qué es lo que pide el usuario y diséñalo completamente desde cero usando MÚLTIPLES piezas (bloques, cilindros, esferas, cuñas, VehicleSeat si es vehículo).\n"
            "No reutilices diseños anteriores. Adapta las formas, tamaños, colores y posiciones exclusivamente a lo que pide esta orden.\n\n"
            "Devuelve ÚNICAMENTE un objeto JSON válido. No uses bloques markdown (```json), no uses comillas invertidas ni texto adicional.\n\n"
            "Estructura obligatoria exacta:\n"
            "{\n"
            "  \"reasoning\": \"Descripción de cómo diseñaste la petición del usuario\",\n"
            "  \"objetos\": [\n"
            "    {\n"
            "      \"shape\": \"Block\",\n"
            "      \"size\": {\"X\": 4, \"Y\": 1, \"Z\": 4},\n"
            "      \"offset\": {\"X\": 0, \"Y\": 0, \"Z\": 0},\n"
            "      \"color\": {\"R\": 0.5, \"G\": 0.3, \"B\": 0.1},\n"
            "      \"material\": \"Wood\",\n"
            "      \"anchored\": true,\n"
            "      \"transparency\": 0,\n"
            "      \"can_collide\": true\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt_estricto
        )
        
        texto = response.text.strip()
        print("TEXTO RECIBIDO DE GEMINI:", texto)

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
        print("--- ERROR CRÍTICO EN LA IA ---")
        traceback.print_exc()
        # Sin respaldos falsos: si algo falla, devolvemos el error exacto en el JSON
        return jsonify({
            "reasoning": "Error al procesar con IA: " + str(e),
            "objetos": []
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
