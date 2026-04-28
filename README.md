# Interface de Voz para Docentes STEM

Ferramenta de acessibilidade que permite a professores cegos criarem construções matemáticas no GeoGebra usando apenas comandos de voz em português.

## Como funciona

1. O professor fala um comando em português (ex: *"desenhe um círculo de raio 3"*)
2. O áudio é capturado pelo navegador e transcrito
3. O texto é enviado para um servidor local que usa a IA Gemini para traduzir para linguagem GeoGebra
4. O resultado é desenhado automaticamente no gráfico
5. O sistema confirma o comando por voz

---

## Pré-requisitos

- [Google Chrome](https://www.google.com/chrome/) (obrigatório — outros navegadores não suportam reconhecimento de voz)
- [Python 3.10+](https://www.python.org/downloads/) — durante a instalação, marque **"Add Python to PATH"**
- Chave de API do Google Gemini (gratuita) — obtenha em [aistudio.google.com](https://aistudio.google.com)

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. Instale as dependências Python

```bash
pip install flask flask-cors google-generativeai
```

### 3. Configure sua chave de API

Abra o arquivo `server.py` e substitua na linha 8:

```python
CHAVE_API = "SUA_CHAVE_AQUI"
```

pela sua chave real obtida no [Google AI Studio](https://aistudio.google.com/apikey).

---

## Como rodar

### Passo 1 — Inicie o servidor

No terminal, dentro da pasta do projeto:

```bash
py server.py
```

Você verá:
Running on http://127.0.0.1:5000

> ⚠️ Mantenha esse terminal aberto enquanto usar a ferramenta.

### Passo 2 — Abra a interface

Abra o arquivo `index.html` no **Google Chrome**.

### Passo 3 — Use

Clique em **"Iniciar Comando de Voz"** e fale um comando como:

- *"desenhe um círculo de raio 3"*
- *"trace a reta y igual a 2x mais 1"*
- *"faça a parábola x ao quadrado"*
- *"marque o ponto 2 vírgula 3"*

---

## Estrutura do projeto
projeto/
index.html   # Interface principal
app.js       # Lógica de voz e comunicação
style.css    # Estilos
server.py    # Servidor Flask + integração Gemini

---

## Observações

- O servidor roda localmente — nenhum dado é enviado para servidores externos além da API do Gemini
- O modelo utilizado é o `gemini-3-flash-preview`
- Em caso de erro de cota da API, aguarde alguns minutos e tente novamente

---

## Tecnologias utilizadas

- [GeoGebra API](https://www.geogebra.org/m/sehh3grj)
- [Google Gemini API](https://ai.google.dev/)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Flask](https://flask.palletsprojects.com/)
