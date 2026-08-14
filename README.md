# InsideVox

Ferramenta de acessibilidade que permite a professores com deficiência visual criarem construções matemáticas no GeoGebra usando apenas comandos de voz em português.

## Como funciona

1. O professor ativa o microfone (botão ou tecla **Espaço**) e fala um comando em português (ex: *"desenhe um círculo de raio 3"*)
2. O áudio é capturado pelo navegador e transcrito pela Web Speech API
3. O texto transcrito é enviado ao backend, que utiliza o modelo LLaMA 3.3 70B (via Groq API) para traduzir a linguagem natural em comandos GeoGebra
4. Os comandos são executados no GeoGebra via `evalCommand()`, renderizando o gráfico em tempo real
5. O sistema confirma a ação por voz, descrevendo o que foi criado
6. O sistema mantém memória dos elementos criados para referência em comandos futuros (ex: *"mude o círculo c para raio 5"*)

---

## Pré-requisitos

- [Google Chrome](https://www.google.com/chrome/) (obrigatório — outros navegadores não suportam a Web Speech API)
- [Python 3.10+](https://www.python.org/downloads/) — durante a instalação, marque **"Add Python to PATH"**
- Chave de API da Groq (gratuita) — obtenha em [console.groq.com](https://console.groq.com)

---

## Instalação




##  Instale as dependências Python
pip install fastapi uvicorn groq



