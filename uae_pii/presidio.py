"""Microsoft Presidio recognizers built from patterns.yaml.

Usage:
    from presidio_analyzer import AnalyzerEngine
    from uae_pii.presidio import get_recognizers

    analyzer = AnalyzerEngine()
    for r in get_recognizers():
        analyzer.registry.add_recognizer(r)
    analyzer.analyze(text="Emirates ID 784-...", language="en")

Note: Presidio uses keywords as context to boost scores; it does not enforce
`keyword_required`. Filter low scores for TRN and passport in your pipeline.
"""
from __future__ import annotations

from typing import Optional

from presidio_analyzer import Pattern, PatternRecognizer

from .detectors import VALIDATORS, load_patterns

SCORES = {"low": 0.3, "medium": 0.5, "high": 0.8}


class UAEPatternRecognizer(PatternRecognizer):
    def __init__(self, entity: dict, language: str = "en"):
        self._validator = VALIDATORS.get(entity.get("validator") or "")
        super().__init__(
            supported_entity=entity["presidio_entity"],
            name=f"UAE_{entity['id'].upper()}_RECOGNIZER",
            patterns=[Pattern(entity["id"], entity["regex"], SCORES[entity["confidence"]])],
            context=entity.get("keywords", []),
            supported_language=language,
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        if self._validator is None:
            return None
        return self._validator(pattern_text)


def get_recognizers(language: str = "en") -> list[UAEPatternRecognizer]:
    return [UAEPatternRecognizer(e, language) for e in load_patterns()["entities"]]
