"""
Modelos do banco de dados usando SQLAlchemy.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

logger = logging.getLogger(__name__)

db = SQLAlchemy()


class Student(db.Model):
    """Modelo representando um estudante."""
    
    __tablename__ = 'students'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(db.String(200), nullable=False)
    idade: Mapped[int] = mapped_column(nullable=False)
    nivel: Mapped[str] = mapped_column(db.String(50), nullable=False)
    estilo_aprendizagem: Mapped[str] = mapped_column(db.String(50), nullable=False)
    interesses: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            'id': self.id,
            'nome': self.nome,
            'idade': self.idade,
            'nivel': self.nivel,
            'estilo_aprendizagem': self.estilo_aprendizagem,
            'interesses': self.interesses,
            'descricao': self.descricao,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def validate_data(data: Dict[str, Any]) -> None:
        """Valida dados do estudante."""
        if not data.get('nome') or len(data['nome'].strip()) < 3:
            raise ValueError("Nome deve ter pelo menos 3 caracteres")
        
        idade = data.get('idade')
        if not isinstance(idade, int) or idade < 1 or idade > 120:
            raise ValueError("Idade deve ser entre 1 e 120")
        
        niveis_validos = ['Iniciante', 'Intermediario', 'Avancado']
        if data.get('nivel') not in niveis_validos:
            raise ValueError(f"Nivel deve ser: {', '.join(niveis_validos)}")
        
        estilos_validos = ['Visual', 'Auditivo', 'Cinestesico', 'Leitura/Escrita']
        if data.get('estilo_aprendizagem') not in estilos_validos:
            raise ValueError(f"Estilo deve ser: {', '.join(estilos_validos)}")
        
        interesses = data.get('interesses', [])
        if not isinstance(interesses, list) or len(interesses) == 0:
            raise ValueError("Deve ter pelo menos um interesse")
        
        if len(interesses) > 10:
            raise ValueError("Maximo de 10 interesses")


class GenerationHistory(db.Model):
    """Historico de geracoes de conteudo."""
    
    __tablename__ = 'generation_history'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(db.ForeignKey('students.id'), nullable=False)
    topic: Mapped[str] = mapped_column(db.String(500), nullable=False)
    prompt_type: Mapped[str] = mapped_column(db.String(50), nullable=False)
    prompt_version: Mapped[str] = mapped_column(db.String(20), nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    tokens_used: Mapped[int] = mapped_column(nullable=True)
    cached: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    student: Mapped["Student"] = db.relationship("Student", backref="generations")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.nome if self.student else None,
            'topic': self.topic,
            'prompt_type': self.prompt_type,
            'prompt_version': self.prompt_version,
            'content': self.content,
            'tokens_used': self.tokens_used,
            'cached': self.cached,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
