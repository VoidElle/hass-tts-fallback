# How it works

## The engine chain

The entity holds a chain of two engines:

| Position | Engine | Options passed | Time limit |
|----------|--------|----------------|------------|
| 1 | Primary engine | Primary voice + primary extra options | **Primary timeout** (default 3 s) |
| 2 | Fallback engine | Fallback voice + fallback extra options | **Fallback timeout** (default 30 s) |

For each message the entity tries position 1, then position 2, and returns the first audio produced. The fallback gets a longer limit by default because nothing comes after it.

## When an engine counts as failed

| Condition | Logged reason |
|-----------|---------------|
| No audio before the time limit | `timeout after 3.0s` |
| The engine raises an error (no internet, bad voice, service down) | the error, e.g. `ClientConnectorError(...)` |
| The engine returns no audio at all | `StopAsyncIteration()` or `HomeAssistantError('empty audio')` |
| The engine entity does not exist or is not loaded | `HomeAssistantError('engine not found')` |
| The engine is this entity itself | `HomeAssistantError('engine points to this entity')` |

An error after the first audio, while the rest is still arriving, also counts as a failure: the message is rendered again by the fallback, so no truncated audio is played.

If both engines fail, the call raises `All TTS engines failed: <primary>: <reason>; <fallback>: <reason>`. In an Assist pipeline this shows as a TTS error in the pipeline debug view.

## Rendering a message with an engine

Each engine is called through Home Assistant's TTS manager, the same path `tts.speak` uses:

- **Language**: mapped to the engine's own spelling (see [Configuration → Language](configuration.md#language))
- **Options**: the configured extra options, plus `voice` when a voice is set. Options given by the caller are not passed on
- **File cache**: off for the inner engines. Home Assistant already caches this entity's result, so the audio is not stored twice

## Audio format

The entity returns the audio in the format of the engine that answered: mp3 from Edge TTS, wav from Piper. The caller does not need to handle both: Home Assistant converts the audio to the format the caller asks for. An Assist pipeline asks for the format its satellite needs, so the satellite always receives the same format.

## Caching

Home Assistant caches TTS output per engine, message, language and options. The cache key for this entity does not include which inner engine answered. As a result:

- A message rendered by the primary is served from the cache next time, with no engine call
- A message rendered by the fallback (for example during an internet outage) keeps the fallback voice from the cache after the primary is back

To get the primary voice back for those messages, clear the TTS cache: call the `tts.clear_cache` action from **Developer Tools → Actions**.

## Streaming

The entity does not take streaming input. It waits for the full text, then renders it. Engines that take streaming input, such as Piper over Wyoming, can start speaking an LLM answer before the agent has finished writing it; behind this entity they cannot. Short answers are unaffected. Long LLM answers start later.

## Logging

Every failover writes one warning, from the logger `custom_components.tts_fallback`:

```
WARNING (MainThread) [custom_components.tts_fallback.tts] TTS engine tts.edge_tts failed (timeout after 3.0s)
```

No warning means the primary answered. To find how often the fallback is used, search the log for `TTS engine` and `failed`.
