"""
Configuracoes da aplicacao.

Centraliza todas as configuracoes carregadas de variaveis de ambiente.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Diretorios
BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Model Configuration (Atualizado para o Gemini como fallback)
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash").strip()
MODEL_TEMPERATURE = float(os.getenv('MODEL_TEMPERATURE', '0.7'))
MODEL_MAX_TOKENS = int(os.getenv('MODEL_MAX_TOKENS', '2000'))
MODEL_TOP_P = float(os.getenv('MODEL_TOP_P', '1.0'))
MODEL_FREQUENCY_PENALTY = float(os.getenv('MODEL_FREQUENCY_PENALTY', '0.0'))
MODEL_PRESENCE_PENALTY = float(os.getenv('MODEL_PRESENCE_PENALTY', '0.0'))

# Flask
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', f'sqlite:///{BASE_DIR}/educativa.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Cache
CACHE_EXPIRATION = int(os.getenv('CACHE_EXPIRATION', '3600'))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()


def validate_config():
    """Valida configuracoes obrigatorias."""
    # Alterado para validar a chave do Gemini
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'sua_chave_gemini_aqui':
        raise RuntimeError(
            "ERRO: GEMINI_API_KEY nao configurada. "
            "Configure a chave de API no arquivo .env"
        )
    
    if not PROMPTS_DIR.exists():
        raise RuntimeError(f"ERRO: Diretorio de prompts nao encontrado: {PROMPTS_DIR}")