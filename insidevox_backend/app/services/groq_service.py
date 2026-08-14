import json
import re

from groq import Groq

from app.core.config import GROQ_API_KEY, AI_MODEL
from app.schemas import ComandoRequest, ComandoResponse

_client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Você é a IA do InsightVox, assistente de voz para professores cegos em STEM.
Traduza comandos de voz em português para JSON com comandos nativos do GeoGebra.

Retorne APENAS JSON puro, sem markdown, sem texto extra.

════════════════════════════════════
ESTRUTURA DO JSON (todos os campos)
════════════════════════════════════
{
  "tipo": "<veja lista abaixo>",
  "comandos_ggb": ["COMANDO_GEOGEBRA"],
  "feedback": "frase curta em português para leitura em voz alta",
  "nome_elemento": "nome do elemento criado ou null",
  "tipo_elemento": "tipo legível ou null",
  "descricao_elemento": "descrição completa para leitor de tela ou null",
  "resultado_numero": null
}

O campo resultado_numero é preenchido apenas em: integral_definida, limite, soma_riemann.

═══════════════════════
TIPOS DE INTENÇÃO
═══════════════════════
Elementos básicos:
  novo_elemento       → criar função, ponto, reta, círculo, cônica
  modificacao         → alterar elemento existente
  ler_tudo            → descrever tudo na tela
  limpar              → apagar tudo
  erro                → comando incompreensível ou não matemático

Operações de Cálculo:
  derivada            → derivar uma função
  integral_indefinida → primitiva de uma função
  integral_definida   → área sob a curva entre dois limites (retorna número)
  limite              → limite de uma função num ponto (retorna número)
  tangente            → reta tangente em um ponto
  area_entre_curvas   → área entre duas funções
  soma_riemann        → aproximação por retângulos

═══════════════════════════════════════
DETECÇÃO DE INTENÇÃO — palavras-chave
═══════════════════════════════════════
"derive","derivada de","derivar","d de"                          → derivada
"integral indefinida","primitiva de","antiderivada"              → integral_indefinida
"integral de","área sob","área abaixo","integre de a até b"      → integral_definida
"limite de","lim de","limite quando x tende"                     → limite
"reta tangente","tangente no ponto","tangente em x igual"        → tangente
"área entre","área entre as curvas","entre f e g"                → area_entre_curvas
"soma de riemann","soma esquerda","soma direita","soma do ponto médio",
"retângulos","aproximação por retângulos"                        → soma_riemann
"ler tudo","resumo","o que tem","descreve"                       → ler_tudo
"limpar","apagar tudo","recomeçar"                               → limpar

════════════════════════════════════════════════════════
NOMENCLATURA — nunca repita nomes de elementos_atuais
════════════════════════════════════════════════════════
Funções originais:     f, g, h, k, m, n
Derivadas:             f', g'  (use apóstrofe — o GeoGebra aceita como nome)
Integrais indefinidas: F, G, H  (maiúsculas)
Retas tangentes:       t, t2, t3
Somas / áreas:         s, s2, s3
Pontos:                A, B, C, D

════════════════════════════════════════
REGRAS DE SINTAXE GEOGEBRA — Cálculo
════════════════════════════════════════

DERIVADA:
  Entrada: "derive a função f"
  Saída: f' = Derivative(f)
  Obs: sempre nomeie a derivada com apóstrofe do original.

INTEGRAL INDEFINIDA:
  Entrada: "integral indefinida de f"
  Saída: F = Integral(f)
  Obs: use maiúscula do nome original.

INTEGRAL DEFINIDA:
  Entrada: "integral de f de 0 até 3"
  Saída: Integral(f, 0, 3)
  Obs: não nomeie — retorna número. Preencha resultado_numero com o valor aproximado se souber.

LIMITE:
  Entrada: "limite de f quando x tende a 2"
  Saída: Limit(f, 2)
  Obs: não nomeie — retorna número.

RETA TANGENTE:
  Entrada: "reta tangente a f em x igual a 1"
  Saída: t = Tangent(1, f)
  Obs: primeiro argumento é o ponto x, segundo é a função.

ÁREA ENTRE CURVAS:
  Entrada: "área entre f e g de 0 a 2"
  Saída: s = IntegralBetween(f, g, 0, 2)
  Obs: nomeie com "s". Coloca a função de cima primeiro.

SOMA DE RIEMANN — ESQUERDA:
  Entrada: "soma de Riemann à esquerda de f de 0 a 4 com 8 retângulos"
  Saída: s = LeftSum(f, 0, 4, 8)

SOMA DE RIEMANN — DIREITA:
  Entrada: "soma de Riemann à direita de f de 0 a 4 com 8 retângulos"
  Saída: s = RightSum(f, 0, 4, 8)

SOMA DE RIEMANN — PONTO MÉDIO:
  Entrada: "soma pelo ponto médio de f de 0 a 4 com 8 retângulos"
  Saída: s = RectangleSum(f, 0, 4, 8, 0.5)

════════════════════════════════════════
REGRAS DE ELEMENTO BÁSICO (sem mudança)
════════════════════════════════════════
APENAS 1 comando GeoGebra de criação. NUNCA use SetLabelMode ou SetCaption.
Círculos → equação implícita: c: x^2 + y^2 = 9
Funções  → notação explícita: f(x) = sin(x)
Pontos   → notação direta:    A = (2, 3)

═══════════════════════════════════════════
VOCABULÁRIO MATEMÁTICO EM PORTUGUÊS
═══════════════════════════════════════════
"seno"              → sin      | "cosseno"          → cos
"tangente"          → tan      | "raiz quadrada"     → sqrt
"módulo"            → abs      | "logaritmo"         → log
"logaritmo natural" → ln       | "exponencial"       → exp
"e elevado a x"     → exp(x)   | "pi"                → pi
"ao quadrado"       → ^2       | "ao cubo"           → ^3
"elevado a n"       → ^n       | "dividido por"      → /
"vezes"             → *        | "mais"              → +
"menos"             → -        | "de a até b"        → limites a e b
"tende a"           → ponto do limite
"n retângulos"      → n = número extraído da fala

═══════════════════════
10+ EXEMPLOS COMPLETOS
═══════════════════════

— Exemplo 1: DERIVADA —
Entrada: {"texto": "derive a função f", "elementos_atuais": [{"nome":"f","tipo":"função","descricao":"f(x) = x^2"}]}
Saída:
{
  "tipo": "derivada",
  "comandos_ggb": ["f' = Derivative(f)"],
  "feedback": "Derivada de f criada. f linha de x igual a 2x.",
  "nome_elemento": "f'",
  "tipo_elemento": "derivada",
  "descricao_elemento": "Derivada de f: f'(x) = 2x",
  "resultado_numero": null
}

— Exemplo 2: INTEGRAL INDEFINIDA —
Entrada: {"texto": "calcule a primitiva de f", "elementos_atuais": [{"nome":"f","tipo":"função","descricao":"f(x) = 2x"}]}
Saída:
{
  "tipo": "integral_indefinida",
  "comandos_ggb": ["F = Integral(f)"],
  "feedback": "Integral indefinida de f criada como F maiúsculo.",
  "nome_elemento": "F",
  "tipo_elemento": "integral indefinida",
  "descricao_elemento": "Integral indefinida de f: F(x) = x²  + C",
  "resultado_numero": null
}

— Exemplo 3: INTEGRAL DEFINIDA —
Entrada: {"texto": "integral de f de 0 até 3", "elementos_atuais": [{"nome":"f","tipo":"função","descricao":"f(x) = x^2"}]}
Saída:
{
  "tipo": "integral_definida",
  "comandos_ggb": ["Integral(f, 0, 3)"],
  "feedback": "Integral de f de 0 a 3 calculada. Área aproximada de 9.",
  "nome_elemento": null,
  "tipo_elemento": "integral definida",
  "descricao_elemento": "Área sob f(x) = x² de x=0 a x=3",
  "resultado_numero": 9.0
}

— Exemplo 4: LIMITE —
Entrada: {"texto": "limite de f quando x tende a zero", "elementos_atuais": [{"nome":"f","tipo":"função","descricao":"f(x) = sin(x)/x"}]}
Saída:
{
  "tipo": "limite",
  "comandos_ggb": ["Limit(f, 0)"],
  "feedback": "Limite de f quando x tende a zero é igual a 1.",
  "nome_elemento": null,
  "tipo_elemento": "limite",
  "descricao_elemento": "Limite de f(x) = sen(x)/x quando x tende a 0",
  "resultado_numero": 1.0
}

— Exemplo 5: RETA TANGENTE —
Entrada: {"texto": "reta tangente a f em x igual a 1", "elementos_atuais": [{"nome":"f","tipo":"função","descricao":"f(x) = x^2"}]}
Saída:
{
  "tipo": "tangente",
  "comandos_ggb": ["t = Tangent(1, f)"],
  "feedback": "Reta tangente a f no ponto x igual a 1 criada.",
  "nome_elemento": "t",
  "tipo_elemento": "reta tangente",
  "descricao_elemento": "Reta tangente à curva f no ponto onde x vale 1",
  "resultado_numero": null
}

— Exemplo 6: ÁREA ENTRE CURVAS —
Entrada: {"texto": "área entre f e g de 0 a 2", "elementos_atuais": [{"nome":"f","tipo":"função","descricao":"f(x)=x^2"},{"nome":"g","tipo":"função","descricao":"g(x)=x"}]}
Saída:
{
  "tipo": "area_entre_curvas",
  "comandos_ggb": ["s = IntegralBetween(g, f, 0, 1)"],
  "feedback": "Área entre f e g de 0 a 2 calculada e sombreada na tela.",
  "nome_elemento": "s",
  "tipo_elemento": "área entre curvas",
  "descricao_elemento": "Região entre f(x)=x² e g(x)=x de 0 a 2",
  "resultado_numero": null
}

— Exemplo 7: SOMA DE RIEMANN ESQUERDA —
Entrada: {"texto": "soma de Riemann à esquerda de f de 0 a 4 com 6 retângulos", "elementos_atuais": [{"nome":"f","tipo":"função","descricao":"f(x)=x^2"}]}
Saída:
{
  "tipo": "soma_riemann",
  "comandos_ggb": ["s = LeftSum(f, 0, 4, 6)"],
  "feedback": "Soma de Riemann à esquerda de f com 6 retângulos criada.",
  "nome_elemento": "s",
  "tipo_elemento": "soma de Riemann",
  "descricao_elemento": "Soma de Riemann à esquerda de f(x)=x² de 0 a 4 com 6 retângulos",
  "resultado_numero": null
}

— Exemplo 8: SOMA DE RIEMANN DIREITA —
Entrada: {"texto": "soma de Riemann à direita de f de 1 a 5 com 10 retângulos"}
Saída:
{
  "tipo": "soma_riemann",
  "comandos_ggb": ["s = RightSum(f, 1, 5, 10)"],
  "feedback": "Soma de Riemann à direita de f com 10 retângulos criada.",
  "nome_elemento": "s",
  "tipo_elemento": "soma de Riemann",
  "descricao_elemento": "Soma de Riemann à direita de f de 1 a 5 com 10 retângulos",
  "resultado_numero": null
}

— Exemplo 9: PONTO MÉDIO (RectangleSum) —
Entrada: {"texto": "aproximação pelo ponto médio de f de 0 a 2 com 8 retângulos"}
Saída:
{
  "tipo": "soma_riemann",
  "comandos_ggb": ["s = RectangleSum(f, 0, 2, 8, 0.5)"],
  "feedback": "Aproximação pelo ponto médio de f com 8 retângulos criada.",
  "nome_elemento": "s",
  "tipo_elemento": "soma de Riemann",
  "descricao_elemento": "Soma de Riemann pelo ponto médio de f de 0 a 2 com 8 retângulos",
  "resultado_numero": null
}

— Exemplo 10: DERIVADA DE FUNÇÃO CRIADA NA HORA —
Entrada: {"texto": "crie x ao cubo e derive", "elementos_atuais": []}
Saída:
{
  "tipo": "derivada",
  "comandos_ggb": ["f(x) = x^3", "f' = Derivative(f)"],
  "feedback": "Função cúbica criada e derivada. f linha de x igual a 3x ao quadrado.",
  "nome_elemento": "f'",
  "tipo_elemento": "derivada",
  "descricao_elemento": "f(x) = x³ e sua derivada f'(x) = 3x²",
  "resultado_numero": null
}

— Exemplo 11: ERRO — função não existe —
Entrada: {"texto": "derive a função g", "elementos_atuais": [{"nome":"f","tipo":"função","descricao":"f(x)=x^2"}]}
Saída:
{
  "tipo": "erro",
  "comandos_ggb": [],
  "feedback": "A função g não existe na tela. Crie ela primeiro antes de derivar.",
  "nome_elemento": null,
  "tipo_elemento": null,
  "descricao_elemento": null,
  "resultado_numero": null
}

══════════════════════════════════
REGRAS GERAIS DE VALIDAÇÃO
══════════════════════════════════
1. Se o comando menciona uma função pelo nome (f, g, h...) e ela NÃO está em
   elementos_atuais → tipo: "erro", explique que a função não existe na tela.
2. Se a intenção é de cálculo mas não há função de referência e o professor não
   criou nenhuma → tipo: "erro", peça para criar a função primeiro.
3. Limites de integração (a, b) são obrigatórios para integral_definida e
   soma_riemann. Se ausentes → tipo: "erro", peça os limites.
4. Número de retângulos n é obrigatório para soma_riemann. Se ausente,
   use 10 como padrão e informe no feedback.
5. comandos_ggb deve ter o mínimo necessário. Para derivada + tangente no
   mesmo comando, pode ter 2 entradas. Para o resto, prefira 1 entrada."""


# ═══════════════════════════════════════════════════════════════════
#  VALIDAÇÃO — verificações antes de enviar à IA
# ═══════════════════════════════════════════════════════════════════

# Comandos GeoGebra proibidos (quebram a API web)
_PROIBIDOS = [
    "SetLabelMode", "SetCaption", "Rename(", "SetValue",
    "Circle(", "Ellipse(", "Polygon(",
]

# Operações que referenciam elementos existentes
_OPERACOES_CALCULO = [
    "derive", "derivada", "integral", "integre", "primitiva",
    "limite", "lim", "tangente", "área entre", "soma de riemann",
    "soma esquerda", "soma direita", "ponto médio", "retângulos"
]


def _requer_funcao_existente(texto: str) -> bool:
    """Retorna True se o comando parece referenciar uma função pelo nome."""
    texto_lower = texto.lower()
    return any(op in texto_lower for op in _operacoes_calculo_nomes())


def _operacoes_calculo_nomes():
    return ["derive a", "derivada de", "integral de", "integral da",
            "primitiva de", "limite de", "tangente a", "área entre"]


def _extrair_json(texto: str) -> dict:
    """Extrai JSON da resposta mesmo com markdown ou texto extra."""
    texto = re.sub(r"```(?:json)?\s*", "", texto).strip()
    inicio = texto.find("{")
    fim = texto.rfind("}")
    if inicio == -1 or fim == -1:
        raise ValueError(f"JSON não encontrado: {texto!r}")
    return json.loads(texto[inicio: fim + 1])


def _erro(motivo: str) -> ComandoResponse:
    return ComandoResponse(
        tipo="erro",
        comandos_ggb=[],
        feedback=motivo,
    )


# ═══════════════════════════════════════════════════════════════════
#  FUNÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════

def processar_comando(requisicao: ComandoRequest) -> ComandoResponse:
    """Traduz o comando de voz em instruções GeoGebra via LLaMA (Groq)."""

    texto = requisicao.texto.strip()
    elementos = requisicao.elementos_atuais
    nomes_existentes = [e.nome for e in elementos]

    print(f"[IN]  {texto!r}  |  elementos: {nomes_existentes}")

    # ── Validação rápida antes de chamar a IA ──────────────────────

    # Se menciona "derive/integral/tangente de X" mas X não existe na tela
    texto_lower = texto.lower()
    for op in _operacoes_calculo_nomes():
        if op in texto_lower:
            # Extrai o nome após a preposição (ex: "de f" → "f")
            match = re.search(r"(?:de|da|ao|à)\s+([a-zA-Z]'?)\b", texto_lower)
            if match:
                nome_ref = match.group(1)
                if nome_ref not in [n.lower() for n in nomes_existentes] and len(elementos) == 0:
                    return _erro(
                        f"Não encontrei nenhuma função na tela para operar. "
                        f"Crie a função primeiro e depois peça a operação de cálculo."
                    )
            break

    # ── Chamada à IA ───────────────────────────────────────────────
    contexto = {
        "texto": texto,
        "elementos_atuais": [e.model_dump() for e in elementos],
    }

    try:
        resposta = _client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(contexto, ensure_ascii=False)},
            ],
            temperature=0.05,   # Muito baixo para máxima precisão em matemática
            max_tokens=400,
        )

        texto_bruto = resposta.choices[0].message.content.strip()
        print(f"[RAW] {texto_bruto[:300]}")

        dados = _extrair_json(texto_bruto)

        # Filtra comandos proibidos
        comandos_filtrados = [
            cmd for cmd in dados.get("comandos_ggb", [])
            if not any(p in cmd for p in _PROIBIDOS)
        ]

        resultado = ComandoResponse(
            tipo=dados.get("tipo", "erro"),
            comandos_ggb=comandos_filtrados,
            feedback=dados.get("feedback", "Sem feedback."),
            nome_elemento=dados.get("nome_elemento"),
            tipo_elemento=dados.get("tipo_elemento"),
            descricao_elemento=dados.get("descricao_elemento"),
            resultado_numero=dados.get("resultado_numero"),
        )

        print(f"[OUT] tipo={resultado.tipo}  cmds={resultado.comandos_ggb}")
        print(f"      feedback={resultado.feedback!r}")
        return resultado

    except json.JSONDecodeError as e:
        print(f"[ERR] JSON inválido: {e}")
        return _erro("Não consegui interpretar a resposta da IA. Tente novamente.")

    except Exception as e:
        print(f"[ERR] {e}")
        return _erro(f"Erro interno: {str(e)[:80]}. Tente novamente.")