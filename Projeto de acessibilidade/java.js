import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuração correta para chave AIzaSy (Google Gemini)
CHAVE_API = "AIzaSyCQKiG7WydyA6T-PRxeg5s08Q7OVr94VCw" 
genai.configure(api_key=CHAVE_API)
model = genai.GenerativeModel('gemini-1.5-pro')

# ... (restante do código igual)

SYSTEM_PROMPT = """
Você é um tradutor RIGOROSO de linguagem natural para GeoGebra Script (GGBScript).
REGRAS OBRIGATÓRIAS:
1. Responda APENAS o comando técnico. 
2. NUNCA use markdown, blocos de código (```), ou explicações.
3. Se o usuário disser "Desenhe um círculo de raio 3", responda apenas: Círculo((0,0), 3)
4. Se não entender, responda: ERRO
"""

@app.route('/traduzir', methods=['POST'])
def traduzir():
    dados = request.json
    texto_professor = dados.get('texto', '')

    try:
        # Usando um prompt mais direto
        full_prompt = f"{SYSTEM_PROMPT}\n\nConverter: {texto_professor}"
        response = model.generate_content(full_prompt)
        
        # LIMPEZA PROFUNDA: remove espaços, aspas e blocos de código
        comando = response.text.strip().replace("```", "").replace("ggb", "").replace("javascript", "")
        
        # Log para você ver no terminal exatamente o que a IA escreveu
        print(f"DEBUG - IA recebeu: {texto_professor}")
        print(f"DEBUG - IA respondeu: '{comando}'")

        if not comando or "ERRO" in comando.upper():
            return jsonify({"comando": None, "erro": "IA confusa"}), 200
            
        return jsonify({"comando": comando})
    except Exception as e:
        print(f"Erro Grave: {e}")
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
