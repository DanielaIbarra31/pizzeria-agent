import os
import traceback
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Obtener API Key
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GENAI_API_KEY:
    print("ERROR: No encontré la GEMINI_API_KEY en las variables de entorno.")

# Configurar Gemini
try:
    genai.configure(api_key=GENAI_API_KEY)
    INSTRUCCIONES = """
    Eres Luigi, de Pizzería La Mía.
    Menú: Peperoni $10, Hawaiana $11, 4 Quesos $12.
    Tu misión: Saludar, tomar el pedido, preguntar dirección y confirmar.
    Sé breve.
    """
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=INSTRUCCIONES)
except Exception as e:
    print(f"Error configurando Gemini: {e}")

# Memoria Volátil (Se borra si el servidor se reinicia)
sesiones = {}

@app.route('/', methods=['GET'])
def home():
    return "Luigi (Versión Memoria) está activo y sin errores."

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # 1. Validar que nos envíen JSON
        if not request.is_json:
            return jsonify({"error": "El cuerpo de la petición no es JSON"}), 400

        data = request.json
        
        # 2. Obtener datos con valores por defecto para no romper
        msg = data.get('message')
        user_id = data.get('user_id', 'anonimo') # Si no hay ID, usa 'anonimo'

        print(f"Mensaje recibido de {user_id}: {msg}") # Esto saldrá en los logs

        if not msg:
            return jsonify({"error": "No enviaste el campo 'message'"}), 400

        # 3. Gestión de Memoria
        if user_id not in sesiones:
            print(f"Creando nueva sesión para {user_id}")
            sesiones[user_id] = model.start_chat(history=[])

        chat_session = sesiones[user_id]

        # 4. Enviar a Gemini
        response = chat_session.send_message(msg)
        
        return jsonify({
            "respuesta": response.text,
            "debug_id": user_id 
        })

    except Exception as e:
        # Si algo falla, imprimimos el error real en los logs de Render
        print("!!!!!! ERROR EN EL SERVIDOR !!!!!!!")
        traceback.print_exc()
        return jsonify({"error": f"Ocurrió un error interno: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
