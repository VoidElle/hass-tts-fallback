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


def find_loop(graph: dict[str, list[str]], start: str) -> list[str] | None:
    """Return a chain of engines leading from start back to start, if any.

    graph maps each TTS Fallback entity to the engines it calls; engines not in
    the graph are plain engines and end the chain.
    """
    stack = [(start, [start])]
    seen = set()
    while stack:
        node, path = stack.pop()
        for engine in graph.get(node, []):
            if engine == start:
                return [*path, engine]
            if engine not in seen:
                seen.add(engine)
                stack.append((engine, [*path, engine]))
    return None


def default_language(language: str, country: str | None) -> str:
    """Home Assistant's language, with its country added when it has none.

    "it" in Italy gives "it-IT", the form voice pipelines and most engines use.
    """
    if "-" in language or "_" in language or not country:
        return language
    return f"{language}-{country.upper()}"


def language_variants(language: str) -> list[str]:
    """Spellings of a language this entity accepts from callers."""
    return sorted({language, language.replace("-", "_"), language.split("-")[0]})
