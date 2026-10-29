"""UAE PII Patterns — detection rules for UAE identifiers."""
from .detectors import Match, detect, iban_valid, load_patterns, luhn_valid, mask

__all__ = ["Match", "detect", "iban_valid", "load_patterns", "luhn_valid", "mask"]
__version__ = "1.0.0"
