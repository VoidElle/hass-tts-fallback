# Configuration

All configuration is done in the Home Assistant UI. There is no YAML option.

## Setup form

**Settings → Devices & Services → + Add Integration → TTS Fallback**

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| Primary engine | ✅ | `tts.edge_tts` | TTS entity tried first for every message |
| Primary voice | | `it-IT-IsabellaNeural` | Voice name passed to the primary as the `voice` option. Empty = the engine's default voice |
| Fallback engine | ✅ | `tts.piper` | TTS entity used when the primary fails. Must differ from the primary |
| Fallback voice | | `it_IT-serena-medium` | Voice name passed to the fallback. Empty = the engine's default voice |
| Language | ✅ | `it-IT` | Language this entity speaks. See [Language](#language) |
| Primary timeout | ✅ | `3` s | Longest wait for the primary's **first** audio, 0.5–30 s in steps of 0.5 |

The form shows an error if the primary and fallback engines are the same entity.

The entry is created with the title **Voce con fallback**, so the entity is `tts.voce_con_fallback`. Both can be renamed in Home Assistant as usual.

## Changing settings after setup

Open the entry and select **Configure**. The form has the same fields as setup, filled with the current values. The integration's own entity is not offered as an engine, which would make it call itself. Saving reloads the entry, so the change applies to the next message.

| Setting | Where |
|---------|-------|
| Engines, voices, language, timeout | **Configure** |
| Entity name or ID | Entity settings |

## Language

The **Language** field sets the languages the entity accepts from callers. For `it-IT` these are `it`, `it-IT` and `it_IT`, so an Assist pipeline set to either Italian spelling can use it.

Engines spell languages differently: Edge TTS lists `it-IT`, Piper over Wyoming lists `it_IT`. The integration passes each engine the closest language it supports:

1. the requested language exactly, if the engine lists it
2. otherwise the same language with `-`/`_` and case ignored (`it-IT` → `it_IT`)
3. otherwise the first language with the same base (`it-IT` → `it`)
4. otherwise nothing, so the engine uses its default language

The voice name usually decides the accent anyway, so step 4 still gives the right voice when the voice is set.

## Voice names

Voice names belong to each engine and are not checked when you save the form. A wrong name shows up as an engine error in the log at the first message.

| Engine | Format | Examples |
|--------|--------|----------|
| Microsoft Edge TTS | `<language>-<Name>Neural` | `it-IT-IsabellaNeural`, `it-IT-ElsaNeural`, `it-IT-DiegoNeural` |
| Piper (Wyoming) | `<language>-<name>-<quality>` | `it_IT-serena-medium`, `it_IT-serena-high`, `it_IT-paola-medium` |

On a Raspberry Pi, Piper `medium` voices render noticeably faster than `high` ones, which matters for the fallback.

## Choosing the timeout

The timeout covers only the time until the primary sends its first audio. Once audio has started arriving, the rest of the message is collected without a time limit.

- Too low: a working primary is skipped on longer sentences or a slow connection, and the fallback voice is heard more often than needed.
- Too high: when the primary hangs, the satellite stays silent for that long before the fallback starts.

Start with the default 3 s, then look at the failover warnings in the log (see [How it works](how-it-works.md#logging)).
