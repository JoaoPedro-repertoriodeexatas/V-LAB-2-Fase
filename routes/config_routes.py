"""
Rotas para configuracoes e gerenciamento de cache.
"""

import logging
from flask import Blueprint, jsonify

import config

logger = logging.getLogger(__name__)

config_bp = Blueprint('config', __name__, url_prefix='/api')

# llm_service sera injetado no app.py
llm_service = None


def init_config_routes(service):
    """Inicializa as rotas com o servico de LLM."""
    global llm_service
    llm_service = service


@config_bp.route('/config', methods=['GET'])
def get_config():
    """Visualiza configuracoes do modelo."""
    try:
        return jsonify({
            'success': True,
            'config': {
                'model_name': config.MODEL_NAME,
                'temperature': config.MODEL_TEMPERATURE,
                'max_tokens': config.MODEL_MAX_TOKENS,
                'top_p': config.MODEL_TOP_P,
                'frequency_penalty': config.MODEL_FREQUENCY_PENALTY,
                'presence_penalty': config.MODEL_PRESENCE_PENALTY,
                'cache_expiration': config.CACHE_EXPIRATION
            }
        })
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@config_bp.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Estatisticas do cache."""
    try:
        stats = llm_service.get_cache_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@config_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Limpa o cache."""
    try:
        count = llm_service.clear_cache()
        logger.info(f"Cache limpo: {count} entradas")
        return jsonify({'success': True, 'entries_removed': count})
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
