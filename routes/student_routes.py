"""
Rotas para gerenciamento de estudantes.
"""

import logging
from flask import Blueprint, request, jsonify

from models import db, Student

logger = logging.getLogger(__name__)

student_bp = Blueprint('students', __name__, url_prefix='/api/students')


@student_bp.route('', methods=['GET'])
def list_students():
    """Lista todos os estudantes."""
    try:
        students = Student.query.order_by(Student.created_at.desc()).all()
        return jsonify({
            'success': True,
            'students': [s.to_dict() for s in students]
        })
    except Exception as e:
        logger.error(f"Erro ao listar estudantes: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@student_bp.route('', methods=['POST'])
def create_student():
    """Cria um novo estudante."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados nao fornecidos'}), 400

        Student.validate_data(data)

        student = Student(
            nome=data['nome'].strip(),
            idade=data['idade'],
            nivel=data['nivel'],
            estilo_aprendizagem=data['estilo_aprendizagem'],
            interesses=data['interesses'],
            descricao=data.get('descricao', '').strip()
        )

        db.session.add(student)
        db.session.commit()

        logger.info(f"Estudante criado: {student.nome}")

        return jsonify({
            'success': True,
            'student': student.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar estudante: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500


@student_bp.route('/<int:student_id>', methods=['GET'])
def get_student(student_id: int):
    """Recupera um estudante."""
    try:
        student = db.session.get(Student, student_id)
        if not student:
            return jsonify({'error': 'Estudante nao encontrado'}), 404

        return jsonify({
            'success': True,
            'student': student.to_dict()
        })
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@student_bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id: int):
    """Atualiza um estudante."""
    try:
        student = db.session.get(Student, student_id)
        if not student:
            return jsonify({'error': 'Estudante nao encontrado'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados nao fornecidos'}), 400

        Student.validate_data(data)

        student.nome = data['nome'].strip()
        student.idade = data['idade']
        student.nivel = data['nivel']
        student.estilo_aprendizagem = data['estilo_aprendizagem']
        student.interesses = data['interesses']
        student.descricao = data.get('descricao', '').strip()

        db.session.commit()

        logger.info(f"Estudante atualizado: {student.nome}")

        return jsonify({
            'success': True,
            'student': student.to_dict()
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500


@student_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id: int):
    """Remove um estudante."""
    try:
        student = db.session.get(Student, student_id)
        if not student:
            return jsonify({'error': 'Estudante nao encontrado'}), 404

        nome = student.nome
        db.session.delete(student)
        db.session.commit()

        logger.info(f"Estudante removido: {nome}")

        return jsonify({
            'success': True,
            'message': f'Estudante {nome} removido com sucesso'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
