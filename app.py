from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import os

app = Flask(__name__, static_folder='.')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
Usa ocasionalmente emojis de espacio como ✨ 🌟 🚀 🪐 ⭐ 🌌 cuando encajen naturalmente.
Cuando escribas matematicas, usa notacion LaTeX: $formula$ para formulas en linea y $$formula$$ para formulas en bloque. Por ejemplo: $\pi \approx 3.14159$, $$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$
Cuando el usuario pida "humanizar" un texto, reescribelo de forma natural como si lo hubiera escrito una persona real: usa frases cortas y largas mezcladas, alguna imperfeccion menor, vocabulario variado, evita palabras tipicas de IA como "crucial", "fundamental", "en conclusion", "en resumen", "es importante destacar". Suena conversacional y autentico."""

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data      = request.json
    messages  = data.get('messages', [])
    image_b64 = data.get('image')
    image_mime= data.get('mime', 'image/jpeg')

    # Si viene imagen, responder que no está disponible por ahora
    if image_b64:
        return jsonify({"reply": "🔭 ¡Ups! La visión de imágenes está en mantenimiento por ahora. Pero puedes describirme lo que ves y te ayudo igual 🚀"})

    # Comando oculto
    last_msg = messages[-1]['content'].strip().lower() if messages else ''
    if 'six seven' in last_msg:
        return jsonify({"reply": "Mi loco, dele pa fuera. 🚪"})

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=full_messages,
            max_tokens=1500,
            temperature=0.7,
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        err = str(e)
        if '429' in err or 'rate_limit' in err.lower() or 'quota' in err.lower():
            return jsonify({"reply": "🌌 Dame unos momentos para recargar las estrellas... Estoy recibiendo demasiadas consultas a la vez. ¡Intentá de nuevo en unos segundos! ⭐"})
        return jsonify({"error": err}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
