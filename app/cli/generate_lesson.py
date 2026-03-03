import argparse
import json
from pathlib import Path
from typing import List

from app.domain.models import (
    StudentProfile,
    LessonParameters,
    LessonSpec,
    RunResult,
)
from app.domain.pipeline import generate_lesson_with_llm


def parse_learning_styles(raw: str) -> List[str]:
    return [s.strip() for s in raw.split(",") if s.strip()]


def build_run_id(topic: str) -> str:
    slug = topic.lower().replace(" ", "-").replace("/", "-").replace("\\", "-")
    return slug[:40] or "lesson"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera uma lição personalizada via LLM (Gemini/OpenAI)."
    )

    parser.add_argument(
        "--topic",
        required=True,
        help="Tópico a ser ensinado.",
    )
    parser.add_argument(
        "--age",
        type=int,
        required=True,
        help="Idade do aluno.",
    )
    parser.add_argument(
        "--level",
        choices=["fundamental", "ensino_medio", "graduacao", "pos_graduacao"],
        required=True,
        help="Nível do aluno.",
    )
    parser.add_argument(
        "--learning-styles",
        type=str,
        default="visual,pratico",
        help="Estilos de aprendizado separados por vírgula.",
    )
    parser.add_argument(
        "--depth",
        choices=["intro", "intermediario", "avancado"],
        default="intro",
        help="Profundidade da explicação.",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="pt-BR",
        help="Idioma principal do conteúdo.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1500,
        help="Limite aproximado de tokens.",
    )
    parser.add_argument(
        "--mode",
        choices=["single_call", "multi_call"],
        default="single_call",
        help="Modo de geração: 1 chamada (reduz quota) ou 4 chamadas (multi_call).",
    )

    args = parser.parse_args()

    learning_styles = parse_learning_styles(args.learning_styles)

    profile = StudentProfile(
        age=args.age,
        level=args.level,  # type: ignore[arg-type]
        learning_styles=learning_styles,  # type: ignore[arg-type]
    )

    params = LessonParameters(
        language=args.language,
        depth=args.depth,  # type: ignore[arg-type]
        max_tokens=args.max_tokens,
    )

    spec = LessonSpec(
        student_profile=profile,
        topic=args.topic,
        parameters=params,
    )
    run: RunResult = generate_lesson_with_llm(spec, mode=args.mode)

    data = run.to_dict()

    runs_dir = Path("data") / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    # usa o run_id vindo do pipeline para nomear o arquivo
    output_path = runs_dir / f"{run.metadata.run_id}.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Lição gerada com LLM salva em: {output_path}")


if __name__ == "__main__":
    main()

