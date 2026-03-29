from flask import Flask, request, jsonify
from flask_cors import CORS
import openai 

app = Flask(__name__)
CORS(app) # Permite que o frontend fale com o backend

# Configure sua chave de API aqui
CHAVE_API = "AIzaSyCQKiG7WydyA6T-PRxeg5s08Q7OVr94VCw"

SYSTEM_PROMPT = """
Você é um compilador especializado em converter linguagem natural pedagógica para comandos de GeoGebra Script (GGBScript). Sua função é apoiar um docente cego na criação de gráficos.
Regras de Ouro:
Responda APENAS com o comando técnico do GeoGebra. Nunca use Markdown (como ```), nunca explique e nunca peça desculpas.
Se o usuário disser 'Crie uma função quadrática padrão', responda: f(x) = x^2
Se o usuário der uma instrução de cor ou estilo, anexe o comando correspondente: Ex: 'Círculo de raio 2 vermelho' -> Círculo((0,0), 2); DefinirCor(c1, "Red")
Se o comando for ambíguo, escolha a interpretação matemática mais comum no Ensino Superior.
Idioma de entrada: Português (Brasil). Saída: Comandos GeoGebra.
"""

@app.route('/traduzir', methods=['POST'])
def traduzir():
    dados = request.json
    texto_professor = dados.get('texto')

    # Chamada à IA (Exemplo com GPT/Gemini) [cite: 23]
    # Aqui implementamos o Chain-of-Thought para precisão [cite: 24]
    try:
        # Lógica de integração com a API da sua escolha
        # Simulação de retorno da IA:
        comando_gerado = "Círculo((0,0), 5)" # O retorno real viria da API
        
        return jsonify({"comando": comando_gerado})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)