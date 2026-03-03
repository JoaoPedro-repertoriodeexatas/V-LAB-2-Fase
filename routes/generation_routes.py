"""
Rotas para geracao de conteudo educativo.
"""

import logging
from flask import Blueprint, request, jsonify

from models import db, Student

logger = logging.getLogger(__name__)

generation_bp = Blueprint('generation', __name__, url_prefix='/api')

# content_service sera injetado no app.py
content_service = None


def init_generation_routes(service):
    """Inicializa as rotas com o servico de conteudo."""
    global content_service
    content_service = service


@generation_bp.route('/generate', methods=['POST'])
def generate_material():
    """Gera material educativo."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Requisicao invalida'}), 400

        topic = data.get('topic', '').strip()
        student_id = data.get('student_id')

        if not student_id:
            return jsonify({'error': 'ID do estudante nao fornecido'}), 400

        student = db.session.get(Student, student_id)
        if not student:
            return jsonify({'error': 'Estudante nao encontrado'}), 404

        results = content_service.generate_content(topic, student)

        return jsonify({
            'success': True,
            'topic': topic,
            'student': student.nome,
            'student_id': student.id,
            'results': results
        })

    except ValueError as e:
        logger.warning(f"Erro de validacao: {e}")
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        logger.error(f"Erro ao gerar material: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
