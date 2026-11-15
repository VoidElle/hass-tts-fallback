"""Pure helpers, importable without Home Assistant."""

from __future__ import annotations


def _norm(language: str) -> str:
    return language.replace("_", "-").lower()


def pick_language(requested: str, supported: list[str]) -> str | None:
    """Map a language like "it-IT" onto the spelling an engine supports.

    Engines disagree on spelling ("it-IT", "it_IT", "it"): try exact, then
    normalized, then same base language. None means use the engine default.
    """
    if requested in supported:
        return requested
    by_norm = {_norm(lang): lang for lang in supported}
    if match := by_norm.get(_norm(requested)):
        return match
    base = _norm(requested).split("-")[0]
    return next((lang for lang in supported if _norm(lang).split("-")[0] == base), None)


def language_variants(language: str) -> list[str]:
    """Spellings of a language this entity accepts from callers."""
    return sorted({language, language.replace("-", "_"), language.split("-")[0]})
