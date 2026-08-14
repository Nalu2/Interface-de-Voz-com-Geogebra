from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import ComandoRequest, ComandoResponse
from app.services.groq_service import processar_comando

app = FastAPI(
    title="InsideVox API",
    description="Backend de acessibilidade para professores cegos em STEM — GeoGebra por voz.",
    version="2.0.0",
)

# Permite requisições do frontend local (Live Server, arquivo direto, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        # Adicionar aqui a URL de produção quando publicar
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", tags=["Saúde"])
def ping():
    """Verifica se o servidor está no ar."""
    return {"status": "ok", "servico": "InsideVox API"}


@app.post("/comando", response_model=ComandoResponse, tags=["Comandos"])
def receber_comando(requisicao: ComandoRequest):
    """
    Endpoint principal.

    Recebe o texto transcrito do comando de voz e o estado atual
    da tela do GeoGebra e retorna:
    - tipo: intenção detectada
    - comandos_ggb: lista de comandos para executar no GeoGebra
    - feedback: texto curto para leitura imediata em voz alta
    - nome/tipo/descricao do elemento para atualizar o estado local
    """
    if not requisicao.texto.strip():
        raise HTTPException(status_code=400, detail="Texto do comando está vazio.")

    return processar_comando(requisicao)

