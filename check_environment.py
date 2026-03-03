#!/usr/bin/env python3
"""
Script de validação e teste do ambiente.

Verifica se todas as dependências estão instaladas e se a configuração está correta.
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Verifica se a versão do Python é adequada."""
    print("Verificando versão do Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"   [OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   [ERRO] Python {version.major}.{version.minor}.{version.micro} - Requer Python 3.9+")
        return False


def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    print("\nVerificando dependências...")
    dependencies = {
        'flask': 'Flask',
        'openai': 'OpenAI',
        'dotenv': 'python-dotenv',
        'sqlalchemy': 'SQLAlchemy',
        'flask_sqlalchemy': 'Flask-SQLAlchemy'
    }
    
    all_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"   [OK] {name} - Instalado")
        except ImportError:
            print(f"   [ERRO] {name} - NAO instalado")
            all_ok = False
    
    return all_ok


def check_env_file():
    """Verifica se o arquivo .env existe."""
    print("\nVerificando arquivo .env...")
    env_file = Path('.env')
    
    if not env_file.exists():
        print("   [ERRO] Arquivo .env nao encontrado")
        print("   [DICA] Execute: cp .env.example .env")
        return False
    
    print("   [OK] Arquivo .env encontrado")
    
    # Verifica se a API key está configurada
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_openrouter_api_key_here' in content:
            print("   [AVISO] API Key do OpenRouter ainda nao configurada")
            print("   [DICA] Edite o arquivo .env e adicione sua chave de API")
            return False
    
    print("   [OK] API Key configurada")
    return True


def check_file_structure():
    """Verifica se todos os arquivos necessários existem."""
    print("\nVerificando estrutura de arquivos...")
    required_files = [
        'app.py',
        'models.py',
        'prompt_engine.py',
        'llm_service.py',
        'requirements.txt',
        'templates/index.html',
        '.env.example'
    ]
    
    all_ok = True
    for file in required_files:
        if Path(file).exists():
            print(f"   [OK] {file}")
        else:
            print(f"   [ERRO] {file} - NAO encontrado")
            all_ok = False
    
    return all_ok


def test_imports():
    """Testa se os módulos principais podem ser importados."""
    print("\nTestando imports dos modulos...")
    
    try:
        from models import db, Student, GenerationHistory
        print("   [OK] models.py")
    except Exception as e:
        print(f"   [ERRO] models.py - {e}")
        return False
    
    try:
        from prompt_engine import PromptEngine
        print("   [OK] prompt_engine.py")
    except Exception as e:
        print(f"   [ERRO] prompt_engine.py - {e}")
        return False
    
    try:
        from llm_service import LLMService
        print("   [OK] llm_service.py")
    except Exception as e:
        print(f"   [ERRO] llm_service.py - {e}")
        return False
    
    return True


def main():
    """Executa todas as verificações."""
    print("=" * 60)
    print("VERIFICACAO DO AMBIENTE - Plataforma Educativa com IA")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_file_structure(),
        check_env_file(),
        test_imports()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("[OK] TODAS AS VERIFICACOES PASSARAM!")
        print("\nPara iniciar a aplicacao, execute:")
        print("   python app.py")
        print("\n   Acesse: http://localhost:5000")
        print("=" * 60)
        return 0
    else:
        print("[ERRO] ALGUMAS VERIFICACOES FALHARAM")
        print("\nCorreja os problemas acima e tente novamente.")
        print("\nConsulte o README.md para instrucoes detalhadas.")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(main())
