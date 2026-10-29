"""Regex + validation + keyword-proximity detection for UAE PII."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from functools import lru_cache
from importlib import resources
from typing import Callable, Iterable, Optional

import yaml

CONFIDENCE_ORDER = {"low": 1, "medium": 2, "high": 3}
_LEVELS = ["low", "medium", "high"]


@dataclass(frozen=True)
class Match:
    entity: str
    name: str
    value: str
    start: int
    end: int
    confidence: str
    keyword_found: bool

    def to_dict(self) -> dict:
        return asdict(self)


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def luhn_valid(value: str) -> bool:
    """Luhn (mod-10) check on all digits in value."""
    digits = _digits(value)
    if not digits:
        return False
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def iban_valid(value: str) -> bool:
    """ISO 13616 mod-97 check for a UAE IBAN."""
    s = re.sub(r"\s", "", value).upper()
    if len(s) != 23 or not s.startswith("AE") or not s[2:].isdigit():
        return False
    rearranged = s[4:] + s[:4]
    numeric = "".join(str(int(c, 36)) for c in rearranged)
    return int(numeric) % 97 == 1


VALIDATORS: dict[str, Callable[[str], bool]] = {
    "luhn": luhn_valid,
    "iban_mod97": iban_valid,
}


@lru_cache(maxsize=1)
def load_patterns() -> dict:
    text = resources.files("uae_pii").joinpath("patterns.yaml").read_text(encoding="utf-8")
    return yaml.safe_load(text)


@lru_cache(maxsize=None)
def _compiled(regex: str) -> re.Pattern:
    return re.compile(regex)


def _bump(level: str) -> str:
    return _LEVELS[min(_LEVELS.index(level) + 1, len(_LEVELS) - 1)]


def detect(
    text: str,
    min_confidence: str = "low",
    entities: Optional[Iterable[str]] = None,
) -> list[Match]:
    """Find UAE PII in text.

    - Matches are dropped if a validator (Luhn, mod-97) fails.
    - Entities marked keyword_required need a keyword within `proximity` chars.
    - A nearby keyword raises confidence by one level for other entities.
    """
    cfg = load_patterns()
    proximity = int(cfg.get("proximity", 300))
    wanted = set(entities) if entities else None
    lowered = text.lower()
    results: list[Match] = []

    for ent in cfg["entities"]:
        if wanted and ent["id"] not in wanted:
            continue
        validator = VALIDATORS.get(ent.get("validator") or "")
        keywords = [k.lower() for k in ent.get("keywords", [])]

        for m in _compiled(ent["regex"]).finditer(text):
            value = m.group(0)
            if validator and not validator(value):
                continue
            window = lowered[max(0, m.start() - proximity): m.end() + proximity]
            keyword_found = any(k in window for k in keywords)
            if ent.get("keyword_required") and not keyword_found:
                continue
            confidence = ent["confidence"]
            if keyword_found and not ent.get("keyword_required"):
                confidence = _bump(confidence)
            if CONFIDENCE_ORDER[confidence] < CONFIDENCE_ORDER[min_confidence]:
                continue
            results.append(
                Match(ent["id"], ent["name"], value, m.start(), m.end(), confidence, keyword_found)
            )

    results.sort(key=lambda r: r.start)
    return results


def mask(value: str, visible: int = 4, char: str = "*") -> str:
    """Mask all but the last `visible` alphanumeric characters, keeping separators."""
    total = sum(c.isalnum() for c in value)
    keep_from = max(total - visible, 0)
    out, seen = [], 0
    for c in value:
        if c.isalnum():
            out.append(c if seen >= keep_from else char)
            seen += 1
        else:
            out.append(c)
    return "".join(out)
