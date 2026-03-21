from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os

app = Flask(__name__, static_folder='.')

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
    data     = request.json
    messages = data.get('messages', [])
    image_b64  = data.get('image')      # base64 string opcional
    image_mime = data.get('mime', 'image/jpeg')

    # Construir el ultimo mensaje con imagen si viene
    if image_b64 and messages:
        last = messages[-1]
        messages = messages[:-1] + [{
            "role": "user",
            "content": [
                {"type": "text", "text": last["content"]},
                {"type": "image_url", "image_url": {
                    "url": f"data:{image_mime};base64,{image_b64}"
                }}
            ]
        }]

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=full_messages,
            max_tokens=1500,
            temperature=0.7,
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
