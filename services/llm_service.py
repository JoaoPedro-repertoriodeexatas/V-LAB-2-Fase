import json
import logging
import hashlib
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# IMPORTANTE: Usamos a biblioteca OpenAI para falar com o OpenRouter
from openai import OpenAI

logger = logging.getLogger(__name__)

class CacheEntry:
    """Entrada no cache com timestamp de expiracao."""
    def __init__(self, data: Any, expiration_seconds: int = 3600):
        self.data = data
        self.timestamp = datetime.utcnow()
        self.expiration = self.timestamp + timedelta(seconds=expiration_seconds)

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expiration

class LLMService:
    """Servico de comunicacao com OpenRouter (LLM) e gerenciamento de cache."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "meta-llama/llama-3.3-70b-instruct:free",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        cache_expiration: int = 3600
    ):
        if not api_key or "AIza" in api_key: # Alerta se estiver usando chave Google por engano
            raise ValueError("API Key invalida para OpenRouter. Use uma chave 'sk-or-v1-...'")

        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.cache_expiration = cache_expiration
        self.cache: Dict[str, CacheEntry] = {}

        # Configuração do Cliente para OpenRouter
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:5000", # Necessário para estatísticas do OpenRouter
                "X-Title": "Flask_LLM_App",            # Nome da sua aplicação
            }
        )

        logger.info(f"LLMService (OpenRouter) inicializado - Modelo: {model_name}")

    def _generate_cache_key(self, messages: List[Dict[str, str]]) -> str:
        messages_str = json.dumps(messages, sort_keys=True)
        return hashlib.md5(messages_str.encode()).hexdigest()

    def generate_content(self, messages: List[Dict[str, str]], use_cache: bool = True) -> Dict[str, Any]:
        if not messages:
            raise ValueError("Lista de mensagens nao pode estar vazia")

        cache_key = self._generate_cache_key(messages)

        if use_cache and cache_key in self.cache:
            entry = self.cache[cache_key]
            if not entry.is_expired():
                logger.info("Resposta recuperada do cache")
                result = entry.data.copy()
                result['from_cache'] = True
                return result

        try:
            logger.info(f"Chamando OpenRouter - Modelo: {self.model_name}")

            # Chamada padrão OpenAI compatível com OpenRouter
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages, # Passa a lista de mensagens diretamente
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
            )

            content = response.choices[0].message.content

            # Tenta tratar a resposta como JSON se o seu app esperar isso
            try:
                parsed_content = json.loads(content)
            except json.JSONDecodeError:
                parsed_content = content # Retorna texto puro se não for JSON

            result = {
                "content": parsed_content,
                "model": self.model_name,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens,
                },
                "from_cache": False
            }

            if use_cache:
                self.cache[cache_key] = CacheEntry(result, self.cache_expiration)

            return result

        except Exception as e:
            logger.error(f"Erro na API OpenRouter: {str(e)}", exc_info=True)
            raise RuntimeError(f"Falha na comunicacao: {e}")