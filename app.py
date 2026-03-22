from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import os
import base64

app = Flask(__name__, static_folder='.')

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """Eres 4stro, un asistente universitario apasionado, entusiasta y espectacular.
Tu personalidad es energica, alegre y motivadora. Usas metaforas del espacio, estrellas y universo
cuando es natural hacerlo. Celebras los logros del usuario y lo animas siempre.
Ayudas con tareas, resumenes, explicaciones de conceptos, correccion de textos,
matematicas, programacion, historia, ciencias y cualquier materia universitaria.
Responde siempre en el idioma del usuario.
Cuando expliques algo complejo usa ejemplos practicos y analogias creativas.
Si te piden resumir un texto, hazlo de forma estructurada con puntos clave.
Si te piden corregir un texto, muestra las correcciones claramente.
Empieza tus respuestas con energia, nunca seas aburrido o frio.
Usa ocasionalmente emojis de espacio como ✨ 🌟 🚀 🪐 ⭐ 🌌 cuando encajen naturalmente."""

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data      = request.json
    messages  = data.get('messages', [])
    image_b64 = data.get('image')
    image_mime= data.get('mime', 'image/jpeg')

    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=SYSTEM_PROMPT
    )

    # Convertir historial al formato de Gemini
    gemini_history = []
    for m in messages[:-1]:  # todos menos el ultimo
        role = 'user' if m['role'] == 'user' else 'model'
        gemini_history.append({'role': role, 'parts': [m['content']]})

    chat_session = model.start_chat(history=gemini_history)

    # Construir el ultimo mensaje (con imagen si viene)
    last_msg = messages[-1]['content'] if messages else ''
    if image_b64:
        image_data = base64.b64decode(image_b64)
        parts = [
            last_msg,
            {'mime_type': image_mime, 'data': image_data}
        ]
    else:
        parts = [last_msg]

    try:
        response = chat_session.send_message(parts)
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
