"""
Motor de Engenharia de Prompts.

Carrega templates de prompts de arquivos externos e realiza substituicao de variaveis.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class PromptEngine:
    """Motor que carrega templates de prompts de arquivos externos."""

    def __init__(self, prompts_dir: str = "prompts"):
        self.version = "2.0.0"
        self.prompts_dir = Path(prompts_dir)

        if not self.prompts_dir.exists():
            raise RuntimeError(f"Diretorio de prompts nao encontrado: {self.prompts_dir}")

        self._template_cache: Dict[str, str] = {}

        logger.info(f"PromptEngine inicializado - versao {self.version}")

    def _load_template(self, template_name: str) -> str:
        """Carrega um template de prompt do arquivo."""
        if template_name in self._template_cache:
            return self._template_cache[template_name]

        template_path = self.prompts_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template nao encontrado: {template_path}")

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self._template_cache[template_name] = content
            logger.debug(f"Template carregado: {template_name}")

            return content

        except Exception as e:
            logger.error(f"Erro ao carregar template {template_name}: {e}")
            raise IOError(f"Falha ao ler template: {e}")

    def _build_student_context(self, student_profile: Dict[str, Any]) -> str:
        """Constroi o contexto do estudante usando template."""
        template = self._load_template("template_student_context.txt")

        context_vars = {
            'nome': student_profile.get('nome', 'Estudante'),
            'idade': student_profile.get('idade', 'Nao especificada'),
            'nivel': student_profile.get('nivel', 'Nao especificado'),
            'estilo_aprendizagem': student_profile.get('estilo_aprendizagem', 'Nao especificado'),
            'interesses': ', '.join(student_profile.get('interesses', [])),
            'descricao': student_profile.get('descricao', 'Nao especificada')
        }

        return template.format(**context_vars)

    def _render_prompt(self, template_content: str, variables: Dict[str, Any]) -> str:
        """Renderiza um template substituindo variaveis."""
        try:
            return template_content.format(**variables)
        except KeyError as e:
            logger.error(f"Variavel nao encontrada no template: {e}")
            raise ValueError(f"Variavel obrigatoria ausente: {e}")

    def build_conceptual_explanation_prompt(
        self,
        topic: str,
        student_profile: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Gera prompt para explicacao conceitual usando Chain-of-Thought."""
        if not topic or not topic.strip():
            raise ValueError("O topico nao pode estar vazio")

        logger.debug(f"Construindo prompt de explicacao conceitual para: {topic}")

        system_template = self._load_template("system_conceptual_explanation.txt")
        user_template = self._load_template("user_conceptual_explanation.txt")

        student_context = self._build_student_context(student_profile)

        variables = {
            'student_context': student_context,
            'topic': topic,
            'idade': student_profile.get('idade', 'X'),
            'nivel': student_profile.get('nivel', 'nao especificado')
        }

        system_prompt = system_template
        user_prompt = self._render_prompt(user_template, variables)

        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

    def build_practical_examples_prompt(
        self,
        topic: str,
        student_profile: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Gera prompt para exemplos praticos."""
        if not topic or not topic.strip():
            raise ValueError("O topico nao pode estar vazio")

        logger.debug(f"Construindo prompt de exemplos praticos para: {topic}")

        system_template = self._load_template("system_practical_examples.txt")
        user_template = self._load_template("user_practical_examples.txt")

        student_context = self._build_student_context(student_profile)

        interests_hint = ""
        if student_profile.get('interesses'):
            interesses_str = ', '.join(student_profile['interesses'])
            interests_hint = f"\nUSE OS INTERESSES DO ESTUDANTE ({interesses_str}) para criar exemplos mais engajadores."

        variables = {
            'student_context': student_context,
            'topic': topic,
            'idade': student_profile.get('idade', 'X'),
            'nivel': student_profile.get('nivel', 'Geral'),
            'estilo_aprendizagem': student_profile.get('estilo_aprendizagem', 'diversos'),
            'interests_hint': interests_hint
        }

        system_prompt = system_template
        user_prompt = self._render_prompt(user_template, variables)

        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

    def build_reflection_questions_prompt(
        self,
        topic: str,
        student_profile: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Gera prompt para questoes de reflexao."""
        if not topic or not topic.strip():
            raise ValueError("O topico nao pode estar vazio")

        logger.debug(f"Construindo prompt de questoes reflexivas para: {topic}")

        system_template = self._load_template("system_reflection_questions.txt")
        user_template = self._load_template("user_reflection_questions.txt")

        student_context = self._build_student_context(student_profile)

        variables = {
            'student_context': student_context,
            'topic': topic,
            'nivel': student_profile.get('nivel', 'Intermediario'),
            'idade': student_profile.get('idade', 'X'),
            'estilo_aprendizagem': student_profile.get('estilo_aprendizagem', 'geral')
        }

        system_prompt = system_template
        user_prompt = self._render_prompt(user_template, variables)

        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

    def build_visual_summary_prompt(
        self,
        topic: str,
        student_profile: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, str]]]:
        """Gera prompt para resumo visual."""
        if not topic or not topic.strip():
            raise ValueError("O topico nao pode estar vazio")

        logger.debug(f"Construindo prompt de resumo visual para: {topic}")

        system_template = self._load_template("system_visual_summary.txt")
        user_template = self._load_template("user_visual_summary.txt")

        student_context = self._build_student_context(student_profile)

        variables = {
            'student_context': student_context,
            'topic': topic,
            'nivel': student_profile.get('nivel', 'Intermediario'),
            'estilo_aprendizagem': student_profile.get('estilo_aprendizagem', 'Visual')
        }

        system_prompt = system_template
        user_prompt = self._render_prompt(user_template, variables)

        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

    def reload_templates(self) -> int:
        """Recarrega todos os templates, limpando o cache."""
        count = len(self._template_cache)
        self._template_cache.clear()
        logger.info(f"Cache de templates limpo: {count} templates removidos")
        return count
