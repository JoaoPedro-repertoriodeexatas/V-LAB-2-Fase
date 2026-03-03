from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import List, Literal, Optional, Dict, Any


LearningStyle = Literal["visual", "auditivo", "pratico", "leitura_escrita"]
Level = Literal["fundamental", "ensino_medio", "graduacao", "pos_graduacao"]
Depth = Literal["intro", "intermediario", "avancado"]


@dataclass
class StudentProfile:
    age: int
    level: Level
    learning_styles: List[LearningStyle]


@dataclass
class LessonParameters:
    language: str = "pt-BR"
    depth: Depth = "intro"
    max_tokens: int = 1500


@dataclass
class LessonSpec:
    student_profile: StudentProfile
    topic: str
    parameters: LessonParameters


@dataclass
class ConceptualExplanation:
    text: str
    chain_of_thought: Optional[str] = None


@dataclass
class PracticalExample:
    context: str
    example: str


@dataclass
class VisualSummary:
    format: Literal["ascii_diagram", "structured_json"]
    content: str


@dataclass
class GeneratedContent:
    conceptual_explanation: ConceptualExplanation
    practical_examples: List[PracticalExample]
    reflection_questions: List[str]
    visual_summary: VisualSummary


@dataclass
class PromptVersionInfo:
    explanation: str
    examples: str
    reflection: str
    visual_summary: str


@dataclass
class LLMCallDebug:
    """
    Dados de debug por chamada ao LLM para diagnosticar por que caiu em mock.
    Não inclui segredos (chaves).
    """

    name: str  # ex: "explanation", "examples"
    provider: str  # "gemini" | "openai" | "mock-offline"
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    error: Optional[str] = None


@dataclass
class AutomaticScores:
    clarity: float
    depth: float
    age_appropriateness: float


@dataclass
class HumanFeedback:
    rating: Optional[float] = None
    comments: Optional[str] = None


@dataclass
class Evaluation:
    automatic_scores: Optional[AutomaticScores] = None
    human_feedback: Optional[HumanFeedback] = None


@dataclass
class RunMetadata:
    run_id: str
    timestamp: datetime
    model: str
    prompt_version: PromptVersionInfo
    cache_key: Optional[str] = None
    llm_calls: Optional[List[LLMCallDebug]] = None


@dataclass
class RunResult:
    metadata: RunMetadata
    input: LessonSpec
    output: GeneratedContent
    evaluation: Evaluation = field(default_factory=Evaluation)

    def to_dict(self) -> Dict[str, Any]:
        raw = asdict(self)

        raw["metadata"]["timestamp"] = self.metadata.timestamp.astimezone(
            timezone.utc
        ).isoformat()

        return {
            "metadata": raw["metadata"],
            "input": {
                "student_profile": raw["input"]["student_profile"],
                "topic": raw["input"]["topic"],
                "parameters": raw["input"]["parameters"],
            },
            "output": raw["output"],
            "evaluation": raw["evaluation"],
        }

