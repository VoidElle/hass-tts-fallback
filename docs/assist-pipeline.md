# Assist pipeline

## Set the entity as the pipeline's voice

1. **Settings → Voice assistants**, open the pipeline
2. **Text-to-speech**: pick **Voce con fallback**
3. **Language**: pick Italian (`it-IT`)
4. Save

Every satellite that uses the pipeline (for example an ESPHome Echo Dot) now speaks through the entity. No change on the satellites is needed.

## Test without a satellite

From **Developer Tools → Actions**:

```yaml
action: tts.speak
target:
  entity_id: tts.voce_con_fallback
data:
  media_player_entity_id: media_player.<your_player>
  message: Prova della voce con fallback.
```

The primary voice should answer, and no `TTS engine ... failed` warning should appear in the log.

## Test the failover

Simulate a broken primary, then restore it. Pick one:

| Method | How | Expected warning |
|--------|-----|------------------|
| Wrong voice | **Configure** → Primary voice `it-IT-NonExistentNeural` | the Edge TTS error |
| Timeout | **Configure** → Primary timeout `0.5` s | `timeout after 0.5s` (only if the primary is slower than that) |
| No internet | Block the Home Assistant host's internet access | a connection error |

Use a **new sentence** for each test. A sentence already in the cache is played from it without calling any engine (see [How it works → Caching](how-it-works.md#caching)).

After the test, restore the setting with **Configure** and call `tts.clear_cache`, so sentences rendered by the fallback during the test do not keep the fallback voice.

## Read the timings

**Settings → Voice assistants**, open the pipeline, then **⋮ → Debug**. Each run lists its stages. The **Text-to-speech** stage shows the engine (`tts.voce_con_fallback`) and how long it took.

| What you see | Meaning |
|--------------|---------|
| TTS takes about the usual time | The primary answered |
| TTS takes the timeout plus the fallback's own time | The primary timed out, then the fallback answered |
| TTS ends quickly with an error | The primary errored and the fallback errored too: check both reasons in the error |

The log warning for that run tells which engine failed and why.
