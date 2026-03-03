from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


Provider = Literal["openrouter", "gemini", "openai"]


def _load_environment() -> None:
    loaded = load_dotenv()
    if not loaded:
        load_dotenv(".env.dev")


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variável de ambiente obrigatória não definida: {name}.")
    return value


_load_environment()


@dataclass(slots=True)
class LLMResponse:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    raw: Dict[str, Any]


class LLMClient:
    def __init__(
        self,
        request_timeout: float = 60.0,
    ) -> None:
        self._timeout = request_timeout

        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if not openrouter_key and openai_key and openai_key.startswith("sk-or-"):
            openrouter_key = openai_key
            openai_key = None

        if not gemini_key and openai_key and openai_key.startswith("AIza"):
            gemini_key = openai_key
            openai_key = None

        self._provider: Provider
        self._default_model: str
        self._openai: Optional[OpenAI]
        self._gemini_key: Optional[str]

        if openrouter_key:
            self._init_openrouter(openrouter_key)
        elif gemini_key:
            self._init_gemini(gemini_key)
        elif openai_key:
            self._init_openai(openai_key)
        else:
            raise RuntimeError(
                "Nenhuma API key encontrada. Defina OPENROUTER_API_KEY, "
                "GEMINI_API_KEY/GOOGLE_API_KEY ou OPENAI_API_KEY no .env/.env.dev."
            )

    def _init_openrouter(self, api_key: str) -> None:
        self._provider = "openrouter"
        self._default_model = _get_required_env("OPENROUTER_DEFAULT_MODEL")

        headers: Dict[str, str] = {}
        app_url = os.getenv("OPENROUTER_APP_URL")
        if app_url:
            headers["HTTP-Referer"] = app_url
        app_name = os.getenv("OPENROUTER_APP_NAME")
        if app_name:
            headers["X-Title"] = app_name

        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        self._openai = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=headers or None,
        )
        self._gemini_key = None

    def _init_gemini(self, api_key: str) -> None:
        self._provider = "gemini"
        self._gemini_key = api_key
        self._default_model = _get_required_env("GEMINI_DEFAULT_MODEL")
        self._openai = None

    def _init_openai(self, api_key: str) -> None:
        self._provider = "openai"
        self._default_model = _get_required_env("OPENAI_DEFAULT_MODEL")
        self._openai = OpenAI(api_key=api_key)
        self._gemini_key = None

    @property
    def default_model(self) -> str:
        return self._default_model

    @property
    def provider(self) -> Provider:
        return self._provider

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[list[str]] = None,
    ) -> LLMResponse:
        chosen_model = model or self._default_model

        if self._provider == "gemini":
            return self._generate_with_gemini(
                prompt=prompt,
                model=chosen_model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )

        if not self._openai:
            raise RuntimeError("Cliente OpenAI não inicializado para o provider atual.")

        try:
            response = self._openai.chat.completions.create(
                model=chosen_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                timeout=self._timeout,
            )
        except OpenAIError as exc:
            return self._handle_openai_error(exc, chosen_model)

        choice = response.choices[0]
        text = choice.message.content or ""

        usage = response.usage or None
        prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
        total_tokens = getattr(usage, "total_tokens", 0) if usage else 0

        return LLMResponse(
            text=text,
            model=chosen_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            raw=response.model_dump(),
        )

    def _generate_with_gemini(
        self,
        *,
        prompt: str,
        model: str,
        max_tokens: Optional[int],
        temperature: float,
        top_p: float,
    ) -> LLMResponse:
        if not self._gemini_key:
            raise RuntimeError("Chave do Gemini não configurada.")

        try:
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(
                "Dependência do Gemini não encontrada. Rode: pip install -r requirements.txt"
            ) from exc

        client = genai.Client(api_key=self._gemini_key)

        def _call_gemini(request_model: str):
            return client.models.generate_content(
                model=request_model,
                contents=types.Part.from_text(text=prompt),
                config={
                    "temperature": temperature,
                    "top_p": top_p,
                    **(
                        {"max_output_tokens": max_tokens}
                        if max_tokens is not None
                        else {}
                    ),
                },
            )

        chosen_model = model

        try:
            response = _call_gemini(chosen_model)
        except Exception as exc:  # pragma: no cover
            msg = str(exc)
            if "NOT_FOUND" in msg and "models/" in msg:
                candidates: list[str] = []
                if chosen_model.endswith("-latest"):
                    candidates.append(chosen_model.replace("-latest", ""))
                else:
                    candidates.append(f"{chosen_model}-latest")

                response = None
                for cand in dict.fromkeys(candidates):
                    try:
                        response = _call_gemini(cand)
                        chosen_model = cand
                        break
                    except Exception as inner_exc:
                        msg = str(inner_exc)

                if response is None:
                    try:
                        for m in client.models.list():
                            m_name = getattr(m, "name", None)
                            if not isinstance(m_name, str):
                                continue
                            try:
                                response = _call_gemini(m_name)
                                chosen_model = m_name
                                break
                            except Exception as inner_exc:
                                msg = str(inner_exc)
                    except Exception as list_exc:
                        msg = f"{msg} | list_models_failed: {list_exc}"
            else:
                response = None

            mock_text = (
                "[MOCK LLM RESPONSE]\n"
                "Não foi possível chamar a API do Gemini.\n"
                "Esta é uma resposta simulada para fins de desenvolvimento."
            )
            if response is None:
                return LLMResponse(
                    text=mock_text,
                    model=chosen_model,
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    raw={"error": msg, "provider": "gemini", "mocked": True},
                )

        text = getattr(response, "text", "") or ""
        usage_md = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage_md, "prompt_token_count", 0) if usage_md else 0
        completion_tokens = getattr(usage_md, "candidates_token_count", 0) if usage_md else 0
        total_tokens = getattr(usage_md, "total_token_count", 0) if usage_md else 0

        raw: Dict[str, Any]
        try:
            raw = response.model_dump()  # type: ignore[attr-defined]
        except Exception:
            raw = {"provider": "gemini"}

        return LLMResponse(
            text=text,
            model=chosen_model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            raw=raw,
        )

    def _handle_openai_error(self, exc: OpenAIError, model: str) -> LLMResponse:
        msg = str(exc)
        provider_label = self._provider
        quota_markers = [
            "insufficient_quota",
            "You exceeded your current quota",
            "exceeded your current quota",
            "rate limit",
            "429",
        ]
        if any(marker.lower() in msg.lower() for marker in quota_markers):
            mock_text = (
                "[MOCK LLM RESPONSE]\n"
                f"Não foi possível chamar a API da {provider_label} por limite de uso/quota.\n"
                "Esta é uma resposta simulada para fins de desenvolvimento."
            )
            return LLMResponse(
                text=mock_text,
                model=model,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                raw={"error": msg, "provider": provider_label, "mocked": True},
            )

        raise RuntimeError(f"Erro ao chamar {provider_label}: {exc}") from exc


if __name__ == "__main__":
    client = LLMClient()
    print(f"Provider: {client.provider}")
    print(f"Default model: {client.default_model}")
    response = client.generate("Responda apenas com a palavra 'OK'.")
    print("Resposta do LLM:")
    print(response.text)

