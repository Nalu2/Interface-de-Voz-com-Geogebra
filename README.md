# InsideVox

Ferramenta de acessibilidade que permite a professores com deficiência visual criarem construções matemáticas no GeoGebra usando apenas comandos de voz em português.

## Descrição

O **InsideVox** transforma comandos de voz em português em construções matemáticas no GeoGebra. O sistema utiliza inteligência artificial para interpretar linguagem natural, executar os comandos no ambiente gráfico e fornecer feedback por voz.

### Como funciona

1. O professor ativa o microfone pelo botão **Comando de Voz** ou pela tecla **Espaço**.
2. O áudio é capturado pelo navegador e transcrito pela **Web Speech API**.
3. O texto transcrito é enviado ao backend.
4. O backend utiliza o modelo **LLaMA 3.3 70B**, via **Groq API**, para transformar a linguagem natural em comandos GeoGebra.
5. Os comandos são executados no GeoGebra por meio de `evalCommand()`.
6. O sistema confirma a ação por voz, descrevendo o elemento criado ou modificado.
7. A aplicação mantém uma memória dos elementos criados, permitindo comandos contextuais como:

   * *"mude o círculo c para raio 5"*
   * *"mude a função f para x ao cubo"*

---

## Pré-requisitos

Antes de executar o projeto, certifique-se de ter:

* [Google Chrome](https://www.google.com/chrome/) — obrigatório, devido ao uso da Web Speech API.
* [Python 3.10+](https://www.python.org/downloads/) — durante a instalação, marque **Add Python to PATH**.
* Uma chave de API da [Groq](https://console.groq.com/).

---

## Instalação

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd InsideVox
```

### 2. Instale as dependências Python

```bash
pip install fastapi uvicorn groq
```

Ou, caso esteja disponível no projeto:

```bash
pip install -r insidevox_backend/requirements.txt
```

### 3. Configure a chave da Groq

Abra o arquivo:

```text
insidevox_backend/app/core/config.py
```

Localize:

```python
GROQ_API_KEY = "SUA_CHAVE_AQUI"
```

Substitua `SUA_CHAVE_AQUI` pela sua chave real obtida no [console da Groq](https://console.groq.com/).

> **Importante:** não publique sua chave de API no GitHub. Em uma versão de produção, recomenda-se utilizar variáveis de ambiente.

---

## Como executar

### Passo 1 — Inicie o servidor FastAPI

No terminal, dentro da pasta do projeto:

```bash
cd insidevox_backend
uvicorn app.main:app --reload
```

Você deverá visualizar uma mensagem semelhante a:

```text
Uvicorn running on http://127.0.0.1:8000
```

⚠️ Mantenha esse terminal aberto enquanto estiver utilizando a ferramenta.

### Passo 2 — Abra a interface

Abra o arquivo:

```text
insidevox_frontend/index.html
```

no **Google Chrome**.

### Passo 3 — Utilize comandos de voz

Clique em **Comando de Voz** ou pressione a tecla **Espaço** e fale um comando, por exemplo:

```text
desenhe um círculo de raio 3
```

Outros exemplos:

```text
crie uma função quadrática
```

```text
crie uma reta
```

```text
mude a função f para x ao cubo
```

```text
leia tudo
```

```text
limpe a tela
```

---

## Interface

A interface é organizada em três painéis:

| Painel                    | Função                                                                            |
| ------------------------- | --------------------------------------------------------------------------------- |
| **Esquerdo (280px)**      | Botão de voz, indicador de gravação, transcrição do comando e status do sistema   |
| **Central (820 × 480px)** | Janela do GeoGebra com grade cartesiana e área de feedback auditivo               |
| **Direito (260px)**       | Lista de elementos na tela com nome, tipo e descrição, além do botão **Ler Tudo** |

---

---

## Tecnologias utilizadas

* **[GeoGebra API](https://www.geogebra.org/)** — renderização das construções matemáticas.
* **LLaMA 3.3 70B via Groq API** — processamento e interpretação de linguagem natural.
* **Web Speech API** — reconhecimento de voz.
* **Web Speech Synthesis API** — síntese de fala e feedback auditivo.
* **FastAPI** — servidor backend assíncrono.
* **Python** — implementação do backend.
* **ARIA** — recursos de acessibilidade e compatibilidade com leitores de tela.
* **JavaScript, HTML e CSS** — implementação da interface frontend.

---

## Comandos suportados

### Funções

| Comando de voz                                        | GeoGebra gerado  |
| ----------------------------------------------------- | ---------------- |
| `"crie uma função quadrática"`                        | `f(x) = x^2`     |
| `"crie uma função cúbica"`                            | `f(x) = x^3`     |
| `"crie a função f de x igual a x ao quadrado mais 2"` | `f(x) = x^2 + 2` |
| `"crie a função f de x igual a raiz de x"`            | `f(x) = sqrt(x)` |
| `"crie a função f de x igual a seno de x"`            | `f(x) = sin(x)`  |

### Círculos, retas e pontos

| Comando de voz                              | GeoGebra gerado    |
| ------------------------------------------- | ------------------ |
| `"desenhe um círculo de raio 3"`            | `c: x^2 + y^2 = 9` |
| `"crie um círculo"`                         | `c: x^2 + y^2 = 1` |
| `"crie uma reta"`                           | `f(x) = x`         |
| `"crie uma reta horizontal em y igual a 3"` | `f(x) = 3`         |
| `"crie um ponto em (2,3)"`                  | `A = (2, 3)`       |

### Modificações e contexto

| Comando de voz                      | Ação                                 |
| ----------------------------------- | ------------------------------------ |
| `"mude a função f para x ao cubo"`  | Modifica a função existente          |
| `"aumente o círculo c para raio 5"` | Modifica o círculo existente         |
| `"leia tudo"`                       | Verbaliza todos os elementos na tela |
| `"limpe a tela"`                    | Remove todos os elementos            |

---

## Estrutura do projeto

```text
InsideVox/
├── insidevox_backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   └── config.py       # Configurações e chave da API
│   │   ├── services/
│   │   │   └── groq_service.py # Integração com a Groq API
│   │   ├── main.py              # Ponto de entrada do FastAPI
│   │   └── schemas.py           # Esquemas de dados
│   └── requirements.txt         # Dependências Python
├── insidevox_frontend/
│   ├── index.html               # Interface principal
│   ├── app.js                   # Lógica de voz e comunicação
│   └── style.css                # Estilos acessíveis
├── .gitignore
└── README.md
```

## Compatibilidade com leitores de tela

A interface utiliza marcação ARIA para facilitar a utilização com leitores de tela.

| Leitor de tela | Sistema operacional | Status     |
| -------------- | ------------------- | ---------- |
| **Orca**       | Linux               | ✅ Testado  |
| **NVDA**       | Windows             | ⏳ Pendente |
| **JAWS**       | Windows             | ⏳ Pendente |
| **TalkBack**   | Android             | ⏳ Pendente |
| **VoiceOver**  | macOS / iOS         | ⏳ Pendente |

## 👥 Autores

| Autor                         | Contato                                                                   | Instituição                         |
| ----------------------------- | ------------------------------------------------------------------------- | ----------------------------------- |
| **Ana Luiza Silva Rodrigues** | [silvaanaluiza120@gmail.com](mailto:silvaanaluiza120@gmail.com)           | Universidade Federal do Ceará (UFC) |
| **Lívia Almada Cruz**         | [livia.almada@ufc.br](mailto:livia.almada@ufc.br)                         | Universidade Federal do Ceará (UFC) |
| **Marcelo Martins da Silva**  | [martins2016eng@gmail.com](mailto:martins2016eng@gmail.com)               | Universidade Federal do Ceará (UFC) |

---

## Licença

Este projeto está disponível como **software livre para fins acadêmicos e de pesquisa**.
