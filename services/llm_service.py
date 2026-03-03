"""
Servico de integracao com LLM (OpenRouter) com sistema de cache.
"""

import json
import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from openai import OpenAI

logger = logging.getLogger(__name__)


class CacheEntry:
    """Entrada no cache com timestamp de expiracao."""

    def __init__(self, data: Any, expiration_seconds: int = 3600):
        self.data = data
        self.timestamp = datetime.utcnow()
        self.expiration = self.timestamp + timedelta(seconds=expiration_seconds)

    def is_expired(self) -> bool:
        """Verifica se a entrada expirou."""
        return datetime.utcnow() > self.expiration


class LLMService:
    """Servico de comunicacao com LLM e gerenciamento de cache."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        cache_expiration: int = 3600
    ):
        if not api_key or api_key == "your_openrouter_api_key_here":
            raise ValueError("API Key do OpenRouter nao configurada")

        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.cache_expiration = cache_expiration
        self.cache: Dict[str, CacheEntry] = {}

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Plataforma Educativa"
            }
        )

        logger.info(
            f"LLMService inicializado - Modelo: {model_name}, "
            f"Temp: {temperature}, Max Tokens: {max_tokens}"
        )

    def _generate_cache_key(self, messages: List[Dict[str, str]]) -> str:
        """Gera chave unica para o cache."""
        messages_str = json.dumps(messages, sort_keys=True)
        return hashlib.md5(messages_str.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Recupera dados do cache se disponivel e nao expirado."""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if not entry.is_expired():
                logger.debug(f"Cache HIT: {cache_key}")
                return entry.data
            else:
                logger.debug(f"Cache EXPIRED: {cache_key}")
                del self.cache[cache_key]

        logger.debug(f"Cache MISS: {cache_key}")
        return None

    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Salva dados no cache."""
        self.cache[cache_key] = CacheEntry(data, self.cache_expiration)
        logger.debug(f"Dados salvos no cache: {cache_key}")

    def generate_content(
        self,
        messages: List[Dict[str, str]],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Gera conteudo usando a LLM com suporte a cache.
        """
        if not messages:
            raise ValueError("Lista de mensagens nao pode estar vazia")

        cache_key = self._generate_cache_key(messages)

        # Tenta recuperar do cache
        if use_cache:
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                logger.info("Resposta recuperada do cache")
                cached_response['from_cache'] = True
                return cached_response

        # Chama a API
        try:
            logger.info(f"Chamando API OpenRouter - Modelo: {self.model_name}")

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
            )

            content = response.choices[0].message.content

            # Parse JSON
            try:
                parsed_content = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao fazer parse do JSON: {e}")
                parsed_content = {
                    "error": "Resposta nao esta em formato JSON valido",
                    "raw_content": content
                }

            result = {
                "content": parsed_content,
                "model": self.model_name,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                },
                "from_cache": False
            }

            # Salva no cache
            if use_cache:
                self._save_to_cache(cache_key, result)

            logger.info(f"Resposta gerada - Tokens: {result['tokens_used']['total']}")

            return result

        except Exception as e:
            logger.error(f"Erro ao chamar API OpenRouter: {e}", exc_info=True)
            raise RuntimeError(f"Falha na comunicacao com a API: {e}")

    def clear_cache(self) -> int:
        """Limpa todas as entradas do cache."""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cache limpo: {count} entradas removidas")
        return count

    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas do cache."""
        total = len(self.cache)
        expired = sum(1 for entry in self.cache.values() if entry.is_expired())
        valid = total - expired

        return {
            "total_entries": total,
            "valid_entries": valid,
            "expired_entries": expired,
            "expiration_seconds": self.cache_expiration
        }

    def get_model_config(self) -> Dict[str, Any]:
        """Retorna a configuracao atual do modelo."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        }
