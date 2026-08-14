from pydantic import BaseModel
from typing import Optional


class ElementoAtual(BaseModel):
    """Representa um elemento já presente na tela do GeoGebra."""
    nome: str
    tipo: str
    descricao: str


class ComandoRequest(BaseModel):
    """Payload enviado pelo frontend a cada comando de voz."""
    texto: str
    elementos_atuais: list[ElementoAtual] = []


class ComandoResponse(BaseModel):
    """Resposta estruturada retornada ao frontend."""

    # Intenção detectada
    tipo: str
    # "novo_elemento" | "modificacao" | "ler_tudo" | "limpar" | "erro"
    # "derivada" | "integral_definida" | "integral_indefinida"
    # "limite" | "tangente" | "area_entre_curvas" | "soma_riemann"

    # Comandos GeoGebra para executar via evalCommand()
    comandos_ggb: list[str] = []

    # Texto curto lido em voz alta imediatamente
    feedback: str

    # Dados do elemento criado/modificado
    nome_elemento: Optional[str] = None
    tipo_elemento: Optional[str] = None
    descricao_elemento: Optional[str] = None

    # NOVO — resultado numérico (integrais definidas, limites, somas)
    resultado_numero: Optional[float] = None