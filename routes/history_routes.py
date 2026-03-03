"""
Rotas para historico de geracoes.
"""

import logging
from flask import Blueprint, request, jsonify

from models import db, GenerationHistory

logger = logging.getLogger(__name__)

history_bp = Blueprint('history', __name__, url_prefix='/api')


@history_bp.route('/history', methods=['GET'])
def get_history():
    """Recupera historico de geracoes."""
    try:
        limit = request.args.get('limit', type=int, default=50)
        student_id = request.args.get('student_id', type=int)

        query = GenerationHistory.query

        if student_id:
            query = query.filter_by(student_id=student_id)

        history = query.order_by(
            GenerationHistory.created_at.desc()
        ).limit(limit).all()

        return jsonify({
            'success': True,
            'history': [entry.to_dict() for entry in history]
        })
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@history_bp.route('/history/<int:generation_id>', methods=['GET'])
def get_generation(generation_id: int):
    """Recupera uma geracao especifica."""
    try:
        generation = db.session.get(GenerationHistory, generation_id)
        if not generation:
            return jsonify({'error': 'Geracao nao encontrada'}), 404

        return jsonify({
            'success': True,
            'generation': generation.to_dict()
        })
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
