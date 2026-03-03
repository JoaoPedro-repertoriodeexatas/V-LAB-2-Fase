"""
Servico de geracao de conteudo educativo.
"""

import logging
from typing import Dict, Any

from models import GenerationHistory, db

logger = logging.getLogger(__name__)


class ContentService:
    """Servico para geracao de conteudo educativo."""

    def __init__(self, prompt_engine, llm_service):
        self.prompt_engine = prompt_engine
        self.llm_service = llm_service

    def generate_content(self, topic: str, student: Any) -> Dict[str, Any]:
        """Gera conteudo educativo completo."""
        if not topic or len(topic.strip()) < 3:
            raise ValueError("Topico deve ter pelo menos 3 caracteres")

        if len(topic) > 200:
            raise ValueError("Topico nao pode exceder 200 caracteres")

        topic = topic.strip()
        student_profile = student.to_dict()

        logger.info(f"Gerando material - Topico: {topic}, Estudante: {student.nome}")

        results = {}

        # 1. Explicacao Conceitual
        results['explicacao_conceitual'] = self._generate_and_save(
            'conceptual', topic, student, student_profile
        )

        # 2. Exemplos Praticos
        results['exemplos_praticos'] = self._generate_and_save(
            'practical', topic, student, student_profile
        )

        # 3. Questoes Reflexivas
        results['questoes_reflexivas'] = self._generate_and_save(
            'reflection', topic, student, student_profile
        )

        # 4. Resumo Visual
        results['resumo_visual'] = self._generate_and_save(
            'visual', topic, student, student_profile
        )

        logger.info("Material gerado com sucesso")
        return results

    def _generate_and_save(
        self,
        prompt_type: str,
        topic: str,
        student: Any,
        student_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera conteudo e salva no historico."""
        builders = {
            'conceptual': self.prompt_engine.build_conceptual_explanation_prompt,
            'practical': self.prompt_engine.build_practical_examples_prompt,
            'reflection': self.prompt_engine.build_reflection_questions_prompt,
            'visual': self.prompt_engine.build_visual_summary_prompt
        }

        prompt = builders[prompt_type](topic, student_profile)
        response = self.llm_service.generate_content(prompt['messages'])

        try:
            history = GenerationHistory(
                student_id=student.id,
                topic=topic,
                prompt_type=prompt_type,
                prompt_version=self.prompt_engine.version,
                content=response.get('content', {}),
                tokens_used=response.get('tokens_used', {}).get('total', 0),
                cached=response.get('from_cache', False)
            )
            db.session.add(history)
            db.session.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar historico: {e}")

        return response
