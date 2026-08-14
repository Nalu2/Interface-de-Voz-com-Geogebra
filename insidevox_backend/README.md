# InsideVox v2.0

Plataforma de acessibilidade para professores cegos em STEM — GeoGebra por voz.

---

## Estrutura do projeto

```
insidevox-backend/
├── app/
│   ├── __init__.py
│   ├── main.py            ← Servidor FastAPI e CORS
│   ├── schemas.py         ← Modelos Pydantic (request/response)
│   ├── core/
│   │   └── config.py      ← Chave da API via .env (segura)
│   └── services/
│       └── gemini_service.py ← Toda a lógica de IA e prompts
├── requirements.txt
├── .env.example
└── README.md

insidevox-frontend/
├── index.html             ← Interface acessível (aria-live, tabindex)
├── app.js                 ← Voz, GeoGebra, memória de contexto
└── style.css              ← Alto contraste, foco visível
```

---

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/insidevox.git
cd insidevox
```

### 2. Configure a chave da API (segura, sem expor no código)

```bash
cd insidevox-backend
cp .env.example .env
# Abra o .env e cole sua chave:
# GEMINI_API_KEY=sua_chave_aqui
```

Obtenha sua chave gratuita em: https://aistudio.google.com/apikey

### 3. Instale as dependências Python

```bash
pip install -r requirements.txt
```

---

## Como rodar

### Passo 1 — Inicie o backend

```bash
cd insidevox-backend
uvicorn app.main:app --reload --port 8000
```

Você verá: `Uvicorn running on http://127.0.0.1:8000`

> ⚠️ Mantenha esse terminal aberto enquanto usar a ferramenta.

### Passo 2 — Abra o frontend

Abra `insidevox-frontend/index.html` no **Google Chrome** (obrigatório para Web Speech API).

Use o **Live Server** do VS Code ou qualquer servidor local.

### Passo 3 — Use

Clique em **"Comando de Voz"** ou pressione **Espaço** e fale:

| Intenção      | Exemplos de fala                                          |
|---------------|-----------------------------------------------------------|
| Criar         | "Desenhe um círculo de raio 3"                           |
| Criar         | "Trace a reta y igual a 2x mais 1"                       |
| Criar         | "Marque o ponto 2 vírgula 3"                             |
| Modificar     | "Aumente o círculo c1 para raio 5"                       |
| Modificar     | "Mude a função f para menos x ao quadrado"               |
| Ler tudo      | "Ler tudo" / "O que tem na tela?" / "Resumo"             |
| Limpar        | "Limpar tudo" / "Apagar tudo"                            |

---

## Funcionalidades

### Feedback por Etapas
Após cada comando, o sistema fala apenas sobre a última ação:
> "Círculo c1 criado, raio 3, centrado na origem"

### Comando Ler Tudo
Diga "ler tudo" para ouvir um resumo completo de tudo que está na tela:
> "Na tela há 2 elementos: Círculo c1 com raio 3. Função f igual a 2x mais 1."

### Rotulação Automática
Todo elemento criado recebe automaticamente:
- Um nome padronizado (c1, A, f...)
- Um rótulo visível no GeoGebra
- Uma entrada na lista acessível (compatível com Orca e TalkBack)

### Memória Contextual
O sistema lembra tudo que está na tela. Comandos como "aumente o círculo" ou "mude a função f" funcionam porque o estado é enviado ao backend em cada requisição.

---

## API do Backend

- `GET  /ping` — Verifica se o servidor está no ar
- `POST /comando` — Endpoint principal

Documentação interativa: http://localhost:8000/docs

---

## Tecnologias

- [GeoGebra API](https://www.geogebra.org)
- [Google Gemini API](https://ai.google.dev)
- [Web Speech API](https://developer.mozilla.org/docs/Web/API/Web_Speech_API) (voz → texto e texto → voz)
- [FastAPI](https://fastapi.tiangolo.com)
- [Pydantic v2](https://docs.pydantic.dev)