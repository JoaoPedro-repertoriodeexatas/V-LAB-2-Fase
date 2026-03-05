"""
Aplicacao Flask - Plataforma Educativa com IA.

Entry point da aplicacao com inicializacao e registro de rotas modularizadas.
"""

import logging
from flask import Flask, render_template

import config
from models import db
from services.content_service import ContentService
from services.llm_service import LLMService
from services.prompt_engine import PromptEngine

# Importa blueprints
from routes.student_routes import student_bp
from routes.generation_routes import generation_bp, init_generation_routes
from routes.history_routes import history_bp
from routes.config_routes import config_bp, init_config_routes

# Configuracao de logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Valida configuracoes
config.validate_config()


def create_app():
    """
    Factory para criar e configurar a aplicacao Flask.
    
    Returns:
        Aplicacao Flask configurada
    """
    # Inicializa Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.secret_key = config.SECRET_KEY

    # Inicializa banco
    db.init_app(app)

    # Inicializa servicos
    prompt_engine = PromptEngine(str(config.PROMPTS_DIR))
    llm_service = LLMService(
        api_key=config.GEMINI_API_KEY,
        model_name=config.MODEL_NAME,
        temperature=config.MODEL_TEMPERATURE,
        max_tokens=config.MODEL_MAX_TOKENS,
        top_p=config.MODEL_TOP_P,
        frequency_penalty=config.MODEL_FREQUENCY_PENALTY,
        presence_penalty=config.MODEL_PRESENCE_PENALTY,
        cache_expiration=config.CACHE_EXPIRATION
    )
    content_service = ContentService(prompt_engine, llm_service)

    # Injeta dependencias nas rotas
    init_generation_routes(content_service)
    init_config_routes(llm_service)

    # Registra blueprints
    app.register_blueprint(student_bp)
    app.register_blueprint(generation_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(config_bp)

    # Rota principal
    @app.route('/')
    def index():
        """Pagina inicial."""
        return render_template('index.html')

    # Handlers de erro
    @app.errorhandler(404)
    def not_found(error):
        """Handler 404."""
        return {'error': 'Endpoint nao encontrado'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handler 500."""
        logger.error(f"Erro interno: {error}", exc_info=True)
        return {'error': 'Erro interno do servidor'}, 500

    logger.info(f"Aplicacao criada - Modelo: {config.MODEL_NAME}")

    return app


def init_db(app):
    """Inicializa o banco de dados."""
    with app.app_context():
        db.create_all()
        logger.info("Banco de dados inicializado")


# Cria aplicacao
app = create_app()


if __name__ == '__main__':
    init_db(app)
    logger.info(f"Iniciando servidor - Debug: {config.FLASK_DEBUG}")
    app.run(debug=config.FLASK_DEBUG, host='0.0.0.0', port=8000)
