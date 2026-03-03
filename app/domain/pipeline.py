from __future__ import annotations

import json
from datetime import datetime, timezone

from app.domain.models import (
    LessonSpec,
    ConceptualExplanation,
    PracticalExample,
    VisualSummary,
    GeneratedContent,
    PromptVersionInfo,
    LLMCallDebug,
    AutomaticScores,
    HumanFeedback,
    Evaluation,
    RunMetadata,
    RunResult,
)
from app.services.llm_client import LLMClient


def _build_full_lesson_prompt(spec: LessonSpec) -> str:
    profile = spec.student_profile
    return (
        "Você é um professor pedagógico e cuidadoso.\n\n"
        f"Aluno:\n"
        f"- Idade: {profile.age}\n"
        f"- Nível: {profile.level}\n"
        f"- Estilos de aprendizado: {', '.join(profile.learning_styles)}\n\n"
        f"Tópico: {spec.topic}\n"
        f"Nível de profundidade: {spec.parameters.depth}\n"
        f"Idioma: {spec.parameters.language}\n\n"
        "Tarefa:\n"
        "Gere uma lição completa com 4 partes:\n"
        "1) Explicação conceitual\n"
        "2) 2 exemplos práticos contextualizados\n"
        "3) 3 perguntas de reflexão\n"
        "4) Um resumo visual em ASCII\n\n"
        "Regras importantes:\n"
        "- Pense passo a passo, mas NÃO revele o raciocínio completo.\n"
        "- Forneça somente um resumo curto do raciocínio (2 a 5 bullets).\n\n"
        "Formato de resposta (OBRIGATÓRIO):\n"
        "Responda APENAS em JSON válido, sem texto extra, neste formato:\n"
        "{\n"
        '  "conceptual_explanation": {\n'
        '    "text": "explicação final para o aluno",\n'
        '    "reasoning_summary": ["bullet 1", "bullet 2"]\n'
        "  },\n"
        '  "practical_examples": [\n'
        '    {"context": "contexto do exemplo 1", "example": "exemplo 1"},\n'
        '    {"context": "contexto do exemplo 2", "example": "exemplo 2"}\n'
        "  ],\n"
        '  "reflection_questions": ["pergunta 1", "pergunta 2", "pergunta 3"],\n'
        '  "visual_summary": {"format": "ascii_diagram", "content": "diagrama ASCII"}\n'
        "}\n"
    )


def _build_explanation_prompt(spec: LessonSpec) -> str:
    profile = spec.student_profile
    return (
        "Você é um professor de matemática pedagógico e cuidadoso.\n\n"
        f"Aluno:\n"
        f"- Idade: {profile.age}\n"
        f"- Nível: {profile.level}\n"
        f"- Estilos de aprendizado: {', '.join(profile.learning_styles)}\n\n"
        f"Tópico: {spec.topic}\n"
        f"Nível de profundidade: {spec.parameters.depth}\n"
        f"Idioma: {spec.parameters.language}\n\n"
        "Tarefa:\n"
        "- Pense passo a passo (chain-of-thought), mas NÃO revele o raciocínio completo.\n"
        "- Depois, produza uma explicação final clara e acessível para esse aluno.\n"
        "- Por fim, forneça um resumo curto do raciocínio (2 a 5 bullets) sem detalhes sensíveis.\n\n"
        "Formato de resposta (IMPORTANTE):\n"
        "Responda APENAS em JSON válido, sem texto extra, com o seguinte formato:\n"
        '{\n'
        '  "explanation": "explicação final para o aluno em linguagem simples",\n'
        '  "reasoning_summary": ["bullet 1", "bullet 2"]\n'
        "}\n"
    )


def _build_examples_prompt(spec: LessonSpec) -> str:
    profile = spec.student_profile
    return (
        "Você criará exemplos práticos contextualizados.\n\n"
        f"Aluno:\n"
        f"- Idade: {profile.age}\n"
        f"- Nível: {profile.level}\n"
        f"- Estilos de aprendizado: {', '.join(profile.learning_styles)}\n\n"
        f"Tópico: {spec.topic}\n\n"
        "Tarefa:\n"
        "Gere 2 exemplos práticos do dia a dia que ajudem esse aluno a entender o tópico.\n"
        "Retorne em texto corrido, numerando os exemplos (1., 2.).\n"
    )


def _build_reflection_prompt(spec: LessonSpec) -> str:
    return (
        "Você criará perguntas de reflexão para reforçar o aprendizado.\n\n"
        f"Tópico: {spec.topic}\n\n"
        "Tarefa:\n"
        "Crie 3 perguntas abertas que façam o aluno pensar sobre o conceito, "
        "sem dar a resposta diretamente.\n"
        "Liste-as em formato de lista simples (1., 2., 3.).\n"
    )


def _build_visual_summary_prompt(spec: LessonSpec) -> str:
    return (
        "Você criará um resumo visual em ASCII para o conceito abaixo.\n\n"
        f"Tópico: {spec.topic}\n\n"
        "Tarefa:\n"
        "Produza um diagrama em ASCII simples que destaque os pontos-chave do tópico.\n"
        "Use caixas e setas simples, mantendo o conteúdo em português.\n"
    )


def generate_lesson_with_llm(
    spec: LessonSpec,
    *,
    llm: LLMClient | None = None,
    mode: str = "single_call",
) -> RunResult:
    """
    Pipeline simples:
    - monta prompts
    - chama LLMClient para cada parte
    - monta um RunResult completo
    """
    client = llm or LLMClient()
    llm_calls: list[LLMCallDebug] = []

    if mode == "single_call":
        lesson_prompt = _build_full_lesson_prompt(spec)
        lesson_res = client.generate(
            lesson_prompt,
            max_tokens=spec.parameters.max_tokens,
            temperature=0.6,
        )
        llm_calls.append(
            LLMCallDebug(
                name="lesson",
                provider=getattr(client, "provider", "unknown"),
                model=lesson_res.model,
                prompt_tokens=lesson_res.prompt_tokens,
                completion_tokens=lesson_res.completion_tokens,
                total_tokens=lesson_res.total_tokens,
                error=(
                    lesson_res.raw.get("error")
                    if isinstance(lesson_res.raw, dict)
                    else None
                ),
            )
        )

        # defaults (fallback) caso parsing falhe
        explanation = ConceptualExplanation(text=lesson_res.text, chain_of_thought=None)
        practical_examples = [
            PracticalExample(context="exemplos_praticos_gerados", example=lesson_res.text)
        ]
        reflection_questions = [lesson_res.text]
        visual_summary = VisualSummary(format="ascii_diagram", content=lesson_res.text)

        try:
            parsed = json.loads(lesson_res.text)
            if isinstance(parsed, dict):
                ce = parsed.get("conceptual_explanation", {})
                if isinstance(ce, dict):
                    exp_text = ce.get("text")
                    rs = ce.get("reasoning_summary")
                    cot_text = None
                    if isinstance(rs, list):
                        bullets = [b for b in rs if isinstance(b, str)]
                        if bullets:
                            cot_text = "\n".join(f"- {b}" for b in bullets)
                    if isinstance(exp_text, str):
                        explanation = ConceptualExplanation(
                            text=exp_text, chain_of_thought=cot_text
                        )

                pe = parsed.get("practical_examples")
                if isinstance(pe, list):
                    exs: list[PracticalExample] = []
                    for item in pe:
                        if isinstance(item, dict):
                            ctx = item.get("context")
                            ex = item.get("example")
                            if isinstance(ctx, str) and isinstance(ex, str):
                                exs.append(PracticalExample(context=ctx, example=ex))
                    if exs:
                        practical_examples = exs

                rq = parsed.get("reflection_questions")
                if isinstance(rq, list):
                    qs = [q for q in rq if isinstance(q, str)]
                    if qs:
                        reflection_questions = qs

                vs = parsed.get("visual_summary")
                if isinstance(vs, dict):
                    fmt = vs.get("format")
                    content = vs.get("content")
                    if fmt in ("ascii_diagram", "structured_json") and isinstance(
                        content, str
                    ):
                        visual_summary = VisualSummary(format=fmt, content=content)
        except json.JSONDecodeError:
            pass

        generated = GeneratedContent(
            conceptual_explanation=explanation,
            practical_examples=practical_examples,
            reflection_questions=reflection_questions,
            visual_summary=visual_summary,
        )

    else:
    # explicação conceitual
    explanation_prompt = _build_explanation_prompt(spec)
    explanation_res = client.generate(
        explanation_prompt,
        max_tokens=spec.parameters.max_tokens,
        temperature=0.5,
    )
    llm_calls.append(
        LLMCallDebug(
            name="explanation",
            provider=getattr(client, "provider", "unknown"),
            model=explanation_res.model,
            prompt_tokens=explanation_res.prompt_tokens,
            completion_tokens=explanation_res.completion_tokens,
            total_tokens=explanation_res.total_tokens,
            error=(explanation_res.raw.get("error") if isinstance(explanation_res.raw, dict) else None),
        )
    )

    # tenta extrair explicação e chain-of-thought do JSON retornado
    explanation_text = explanation_res.text
    cot_text = None
    try:
        parsed = json.loads(explanation_res.text)
        if isinstance(parsed, dict):
            explanation_text = parsed.get("explanation", explanation_text)
            # mantemos compatibilidade com o campo existente do modelo (`chain_of_thought`),
            # mas agora guardamos apenas um resumo curto do raciocínio
            rs = parsed.get("reasoning_summary")
            if isinstance(rs, list):
                bullets = [b for b in rs if isinstance(b, str)]
                if bullets:
                    cot_text = "\n".join(f"- {b}" for b in bullets)
    except json.JSONDecodeError:
        # se não vier JSON válido, usamos o texto bruto como explicação
        cot_text = None

    explanation = ConceptualExplanation(
        text=explanation_text,
        chain_of_thought=cot_text,
    )

    # exemplos práticos
    examples_prompt = _build_examples_prompt(spec)
    examples_res = client.generate(
        examples_prompt,
        max_tokens=spec.parameters.max_tokens // 2,
        temperature=0.7,
    )
    llm_calls.append(
        LLMCallDebug(
            name="examples",
            provider=getattr(client, "provider", "unknown"),
            model=examples_res.model,
            prompt_tokens=examples_res.prompt_tokens,
            completion_tokens=examples_res.completion_tokens,
            total_tokens=examples_res.total_tokens,
            error=(examples_res.raw.get("error") if isinstance(examples_res.raw, dict) else None),
        )
    )

    # por enquanto, tratamos tudo como um único bloco de texto;
    # o parsing em vários exemplos pode ser refinado depois
    practical_examples = [
        PracticalExample(
            context="exemplos_praticos_gerados",
            example=examples_res.text,
        )
    ]

    # perguntas de reflexão
    reflection_prompt = _build_reflection_prompt(spec)
    reflection_res = client.generate(
        reflection_prompt,
        max_tokens=256,
        temperature=0.6,
    )
    llm_calls.append(
        LLMCallDebug(
            name="reflection",
            provider=getattr(client, "provider", "unknown"),
            model=reflection_res.model,
            prompt_tokens=reflection_res.prompt_tokens,
            completion_tokens=reflection_res.completion_tokens,
            total_tokens=reflection_res.total_tokens,
            error=(reflection_res.raw.get("error") if isinstance(reflection_res.raw, dict) else None),
        )
    )

    reflection_questions = [reflection_res.text]

    # resumo visual
    visual_prompt = _build_visual_summary_prompt(spec)
    visual_res = client.generate(
        visual_prompt,
        max_tokens=256,
        temperature=0.4,
    )
    llm_calls.append(
        LLMCallDebug(
            name="visual_summary",
            provider=getattr(client, "provider", "unknown"),
            model=visual_res.model,
            prompt_tokens=visual_res.prompt_tokens,
            completion_tokens=visual_res.completion_tokens,
            total_tokens=visual_res.total_tokens,
            error=(visual_res.raw.get("error") if isinstance(visual_res.raw, dict) else None),
        )
    )

    visual_summary = VisualSummary(
        format="ascii_diagram",
        content=visual_res.text,
    )

    generated = GeneratedContent(
        conceptual_explanation=explanation,
        practical_examples=practical_examples,
        reflection_questions=reflection_questions,
        visual_summary=visual_summary,
    )

    prompt_versions = PromptVersionInfo(
        explanation="explanation_v1",
        examples="examples_v1",
        reflection="reflection_v1",
        visual_summary="visual_summary_v1",
    )

    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%SZ") + "_lesson"

    metadata = RunMetadata(
        run_id=run_id,
        timestamp=now,
        model=client.default_model,
        prompt_version=prompt_versions,
        cache_key=None,
        llm_calls=llm_calls,
    )

    evaluation = Evaluation(
        automatic_scores=AutomaticScores(
            clarity=0.0,
            depth=0.0,
            age_appropriateness=0.0,
        ),
        human_feedback=HumanFeedback(
            rating=None,
            comments=None,
        ),
    )

    return RunResult(
        metadata=metadata,
        input=spec,
        output=generated,
        evaluation=evaluation,
    )

