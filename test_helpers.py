"""Self-check for language mapping; runs without Home Assistant."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "helpers", Path(__file__).parent / "custom_components/tts_fallback/helpers.py"
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
pick, variants, loop = helpers.pick_language, helpers.language_variants, helpers.find_loop

g = {"tts.a": ["tts.edge", "tts.b"], "tts.b": ["tts.piper", "tts.a"]}
assert loop(g, "tts.a") == ["tts.a", "tts.b", "tts.a"]
assert loop({"tts.a": ["tts.edge", "tts.b"], "tts.b": ["tts.piper", "tts.c"]}, "tts.a") is None
assert loop({"tts.a": ["tts.b", "tts.c"], "tts.b": ["tts.c"], "tts.c": ["tts.b", "tts.a"]}, "tts.a") is not None
assert loop({"tts.a": ["tts.b"], "tts.b": ["tts.c"], "tts.c": ["tts.b"]}, "tts.a") is None  # loop not through a
assert loop({"tts.a": ["tts.a"]}, "tts.a") == ["tts.a", "tts.a"]

assert pick("it-IT", ["en-US", "it-IT"]) == "it-IT"
assert pick("it-IT", ["en_US", "it_IT"]) == "it_IT"  # Wyoming/Piper spelling
assert pick("it", ["en-US", "it-IT"]) == "it-IT"  # base language
assert pick("it-IT", ["it"]) == "it"
assert pick("it-IT", ["en-US"]) is None  # engine default
assert pick("it-IT", []) is None
assert variants("it-IT") == ["it", "it-IT", "it_IT"]

default = helpers.default_language
assert default("it", "IT") == "it-IT"
assert default("en", "us") == "en-US"
assert default("en-GB", "IT") == "en-GB"  # already regional
assert default("de", None) == "de"
norm = helpers.normalize_text
assert norm("la luce è accesa.Vuoi altro?") == "la luce è accesa. Vuoi altro?"
assert norm("Fatto.Serve altro?Dimmi!Ok") == "Fatto. Serve altro? Dimmi! Ok"
assert norm("alle 18.La sveglia") == "alle 18. La sveglia"
assert norm("È così.Perché?") == "È così. Perché?"
assert norm("Ciao. Come stai?") == "Ciao. Come stai?"  # already spaced
assert norm("Ci sono 23.5 gradi") == "Ci sono 23.5 gradi"  # decimal
assert norm("Rossi S.p.A. e U.S.A.") == "Rossi S.p.A. e U.S.A."  # abbreviations
assert norm("apri config.yaml ora") == "apri config.yaml ora"  # lowercase after
assert norm("Attendi...Poi") == "Attendi...Poi"  # ellipsis left as is
print("ok")
