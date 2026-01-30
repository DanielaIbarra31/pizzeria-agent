import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# 1. Configurar Gemini
# Render buscará la clave en las "Environment Variables"
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

# 2. Instrucciones de la Pizzería (El Prompt)
INSTRUCCIONES = """
Eres Luigi, el asistente de la Pizzería 'La Mía'.
Tu menú:
- Pizza Peperoni ($10)
- Pizza Hawaiana ($11)
- Pizza 4 Quesos ($12)
Objetivo: Tomar el pedido, preguntar dirección y confirmar precio total.
Sé breve y amable. No uses markdown, solo texto plano.
"""

model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=INSTRUCCIONES)
chat = model.start_chat(history=[])

@app.route('/', methods=['GET'])
def home():
    return "¡Hola! El agente de la pizzería está vivo y esperando pedidos."

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    mensaje_usuario = data.get('message', '')

    if not mensaje_usuario:
        return jsonify({"error": "No enviaste mensaje"}), 400

    # Enviar mensaje a Gemini
    response = chat.send_message(mensaje_usuario)
    
    return jsonify({
        "respuesta": response.text
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)