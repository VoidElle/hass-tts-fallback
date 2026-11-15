# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-11-15

First release.

### Added
- **Fallback TTS entity** (`tts.voce_con_fallback` by default), usable as the TTS engine of an Assist pipeline, with `tts.speak`, or with a media player.
- **Automatic failover**: the fallback engine renders the message when the primary raises an error, returns no audio, or sends no audio within the timeout. An error after the first audio also triggers the fallback, so truncated audio is never played.
- **Two timeouts**: primary (default 3 s) and fallback (default 30 s). Both measure only the time to the first audio.
- **Two-step UI setup and Configure flow**:
  - Step 1: name, primary and fallback engines, language, both timeouts
  - Step 2: voice for each engine (dropdown when the engine lists its voices, otherwise typed) and extra engine options as YAML (e.g. Edge `rate`, `pitch`, `volume`; Piper `speaker`), checked against the options each engine supports
- **Language mapping**: each engine gets the language in its own spelling (`it-IT`, `it_IT`, `it`), or its default language when none matches.
- **Loop protection**: Configure refuses engines that would close a loop between TTS Fallback entities and names the chain; at runtime a loop missed by the form fails that engine instead of recursing.
- **Logging**: every failover writes a warning with the engine and the reason; when both engines fail, the error lists both reasons.
- Inner engines run without file cache, so audio is not stored twice.
- English and Italian translations.
- Documentation: README and `docs/` (configuration, how it works, Assist pipeline).

### Known limitations
- No streaming input: the entity waits for the full text, so long LLM answers start speaking later than with a streaming engine such as Piper over Wyoming.
- Home Assistant caches this entity's output per message: a message once rendered by the fallback keeps the fallback voice until `tts.clear_cache` is called.
- Options cannot be passed per call; voices and options come from the entry.
- The chain has two engines; longer chains are built by using another TTS Fallback entity as an engine.

[0.1.0]: https://github.com/VoidElle/hass-tts-fallback/releases/tag/v0.1.0
