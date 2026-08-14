import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
AI_MODEL: str = os.getenv("AI_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY não encontrada. "
        "Crie um arquivo .env com: GROQ_API_KEY=sua_chave_aqui\n"
        "Chave gratuita em: https://console.groq.com"
    )