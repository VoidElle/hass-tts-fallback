# TTS Fallback

Home Assistant custom integration: one TTS entity (`tts.voce_con_fallback`) that
speaks with a primary engine (e.g. `tts.edge_tts`, voice `it-IT-IsabellaNeural`) and
switches to a fallback engine (e.g. `tts.piper`, voice `it_IT-serena-medium`) when the
primary raises, returns no audio, or produces no audio within the timeout (default 3 s).
Usable as `tts_engine` in an Assist pipeline.

## Install

Copy `custom_components/tts_fallback` to `/config/custom_components/` (or add this repo
to HACS as a custom integration repository), restart, then
Settings → Devices & services → Add integration → **TTS Fallback**.
Engines, voices, language and timeout can be changed later from **Configure**.

## Notes

- Each failure is logged as a warning naming the engine and the reason.
- The returned format is the one of the engine that answered (Edge: mp3, Piper: wav);
  HA converts it to the pipeline's preferred format.
- HA caches this entity's output per message. If a message was rendered by the
  fallback, the cached fallback audio is reused until the TTS cache is cleared.
- Inner engines run without file cache, so audio is not stored twice.

## Check

```bash
python3 test_helpers.py
```
