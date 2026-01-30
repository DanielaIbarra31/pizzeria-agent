import os
import logging
from flask import Flask, request, jsonify
import google.generativeai as genai

# Configurar logs para ver errores en Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- CONFIGURACIÓN DE GEMINI ---
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY")
model = None

# Intentamos configurar la IA al arrancar
if GENAI_API_KEY:
    try:
        genai.configure(api_key=GENAI_API_KEY)
        INSTRUCCIONES = """
        Eres Luigi, de Pizzería La Mía. 🍕
        Menú: 
        - Peperoni $10
        - Hawaiana $11
        - 4 Quesos $12
        
        Tu flujo:
        1. Saludar.
        2. Tomar el pedido (tipo y tamaño).
        3. Preguntar dirección.
        4. Confirmar precio y tiempo.
        
        IMPORTANTE: Tienes memoria. Si el cliente dice "la quiero grande", debes recordar qué pizza pidió antes.
        Sé breve y amigable.
        """
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=INSTRUCCIONES)
        logger.info("✅ Gemini configurado correctamente.")
    except Exception as e:
        logger.error(f"❌ Error configurando Gemini: {e}")
else:
    logger.error("⚠️ FALTA LA API KEY: No se encontró la variable GEMINI_API_KEY.")

# --- MEMORIA VOLÁTIL ---
# Aquí guardamos los chats: { "+57300...": objeto_chat_gemini }
sesiones = {}

@app.route('/', methods=['GET'])
def home():
    return "🍕 El servidor de Luigi está ONLINE y con Memoria."

@app.route('/chat', methods=['POST'])
def chat():
    # 1. Verificaciones de seguridad
    if not model:
        return jsonify({"respuesta": "Error: Mi cerebro (API Key) no está configurado en Render."}), 500

    try:
        # 2. Recibir datos
        data = request.json
        mensaje_usuario = data.get('message')
        user_id = data.get('user_id', 'invitado') # El número de celular es la clave

        logger.info(f"Mensaje de {user_id}: {mensaje_usuario}")

        if not mensaje_usuario:
            return jsonify({"error": "No enviaste mensaje"}), 400

        # 3. Lógica de Memoria (El truco)
        # Si este número no nos ha hablado antes (o se reinició el server), creamos chat nuevo
        if user_id not in sesiones:
            logger.info(f"Creando nueva memoria para: {user_id}")
            sesiones[user_id] = model.start_chat(history=[])

        # Recuperamos SU chat específico
        chat_sesion = sesiones[user_id]

        # 4. Enviar a la IA
        response = chat_sesion.send_message(mensaje_usuario)
        texto_respuesta = response.text

        return jsonify({"respuesta": texto_respuesta})

    except Exception as e:
        logger.error(f"Error procesando chat: {e}")
        # Si falla el chat (ej: token vencido), reiniciamos su memoria
        if 'user_id' in locals() and user_id in sesiones:
            del sesiones[user_id]
        return jsonify({"respuesta": "Tuve un pequeño error técnico, ¿me repites lo último? 😵‍💫"}), 200

if __name__ == '__main__':
    # Usar el puerto que Render nos asigne o el 10000 por defecto
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
