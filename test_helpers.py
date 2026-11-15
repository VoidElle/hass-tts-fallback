"""Self-check for language mapping; runs without Home Assistant."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "helpers", Path(__file__).parent / "custom_components/tts_fallback/helpers.py"
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
pick, variants = helpers.pick_language, helpers.language_variants

assert pick("it-IT", ["en-US", "it-IT"]) == "it-IT"
assert pick("it-IT", ["en_US", "it_IT"]) == "it_IT"  # Wyoming/Piper spelling
assert pick("it", ["en-US", "it-IT"]) == "it-IT"  # base language
assert pick("it-IT", ["it"]) == "it"
assert pick("it-IT", ["en-US"]) is None  # engine default
assert pick("it-IT", []) is None
assert variants("it-IT") == ["it", "it-IT", "it_IT"]
print("ok")
