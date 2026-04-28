import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500", "http://localhost:5500"])

CHAVE_API = "AIzaSyB1yW-gC7ukENAOouvXB2lTu3EGITibiz0"
genai.configure(api_key=CHAVE_API)
model = genai.GenerativeModel('gemini-3-flash-preview')

SYSTEM_PROMPT = """Você é um tradutor de linguagem natural para comandos GeoGebra.

REGRAS:
1. Responda APENAS o comando. Sem explicações, sem markdown, sem crases.
2. Use SEMPRE equações e sintaxe universal do GeoGebra:
   - Círculo centrado na origem raio 3: x^2 + y^2 = 9
   - Reta: f(x) = 2x + 1
   - Ponto: A = (2, 3)
   - Parábola: f(x) = x^2
3. Se não conseguir traduzir, responda apenas: ERRO

EXEMPLOS:
- "círculo de raio 3" → x^2 + y^2 = 9
- "círculo de raio 5" → x^2 + y^2 = 25
- "reta y igual a 2x mais 1" → f(x) = 2x + 1
- "parábola x ao quadrado" → f(x) = x^2
- "ponto em 2 vírgula 3" → A = (2, 3)
"""

@app.route('/traduzir', methods=['POST'])
def traduzir():
    texto = request.json.get('texto', '').strip()
    if not texto:
        return jsonify({"erro": "Texto vazio"}), 400

    print(f"[IN]  {texto}")

    try:
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nConverter: {texto}")
        comando = response.text.strip()
        for lixo in ['```ggbscript', '```geogebra', '```javascript', '```', '\n']:
            comando = comando.replace(lixo, '').strip()

        print(f"[OUT] {comando}")

        if not comando or 'ERRO' in comando.upper():
            return jsonify({"comando": None, "erro": "Comando não reconhecido"})

        return jsonify({"comando": comando})

    except Exception as e:
        print(f"[ERR] {e}")
        return jsonify({"erro": str(e)}), 500

@app.route('/ping')
def ping():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)