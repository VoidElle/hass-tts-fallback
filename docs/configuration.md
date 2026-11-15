# Configuration

All configuration is done in the Home Assistant UI. There is no YAML option.

## Setup form

**Settings → Devices & Services → + Add Integration → TTS Fallback**

The form has two steps. Step 2 is built from the engines picked in step 1, so it can list their voices and options.

### Step 1: Engines

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| Name | ✅ | `Voce con fallback` | Name of the entry and of the entity. The default gives `tts.voce_con_fallback` |
| Primary engine | ✅ | `tts.edge_tts` | TTS entity tried first for every message |
| Fallback engine | ✅ | `tts.piper` | TTS entity used when the primary fails. Must differ from the primary |
| Language | ✅ | `it-IT` | Language this entity speaks. See [Language](#language) |
| Primary timeout | ✅ | `3` s | Longest wait for the primary's **first** audio, 0.5–30 s in steps of 0.5 |
| Fallback timeout | ✅ | `30` s | Longest wait for the fallback's first audio, 1–120 s in steps of 0.5 |

The step shows an error if the primary and fallback engines are the same entity.

### Step 2: Voices and engine options

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| Primary voice | | `it-IT-IsabellaNeural` | Voice passed to the primary as the `voice` option. Empty = the engine's default voice. See [Voices](#voices) |
| Primary extra options | | | Any other option the primary accepts. See [Extra options](#extra-options) |
| Fallback voice | | `it_IT-serena-medium` | Voice passed to the fallback. Empty = the engine's default voice |
| Fallback extra options | | | Any other option the fallback accepts |

The step's description lists the options each engine accepts.

## Changing settings after setup

Open the entry and select **Configure**. It shows the same two steps, filled with the current values, without the name. The integration's own entity is not offered as an engine, which would make it call itself. If you pick a different engine in step 1, its voice and extra options start empty in step 2, because they belong to the old engine. Saving reloads the entry, so the change applies to the next message.

| Setting | Where |
|---------|-------|
| Engines, language, timeouts | **Configure**, step 1 |
| Voices, extra options | **Configure**, step 2 |
| Name | Rename the entry or the entity in Home Assistant |

## Language

The **Language** field sets the languages the entity accepts from callers. For `it-IT` these are `it`, `it-IT` and `it_IT`, so an Assist pipeline set to either Italian spelling can use it.

Engines spell languages differently: Edge TTS lists `it-IT`, Piper over Wyoming lists `it_IT`. The integration passes each engine the closest language it supports:

1. the requested language exactly, if the engine lists it
2. otherwise the same language with `-`/`_` and case ignored (`it-IT` → `it_IT`)
3. otherwise the first language with the same base (`it-IT` → `it`)
4. otherwise nothing, so the engine uses its default language

The same mapping picks the voice list shown in step 2. The voice name usually decides the accent anyway, so step 4 still gives the right voice when the voice is set.

## Voices

When the engine publishes its voices for the language (Piper over Wyoming does), the voice field is a dropdown. When it does not (Edge TTS does not), the dropdown is empty and you type the name. A typed name is always accepted, also for engines with a list.

Voice names are not checked against the engine. A wrong name shows up as an engine error in the log at the first message, and that message goes to the fallback.

| Engine | Format | Examples |
|--------|--------|----------|
| Microsoft Edge TTS | `<language>-<Name>Neural` | `it-IT-IsabellaNeural`, `it-IT-ElsaNeural`, `it-IT-DiegoNeural` |
| Piper (Wyoming) | `<language>-<name>-<quality>` | `it_IT-serena-medium`, `it_IT-serena-high`, `it_IT-paola-medium` |

On a Raspberry Pi, Piper `medium` voices render noticeably faster than `high` ones, which matters for the fallback.

## Extra options

Extra options are passed to the engine as they are, together with the voice. Enter them as a YAML mapping. Only options the engine declares are accepted: the form shows **The engine does not accept one of these options** otherwise. If the engine is not loaded when you save, the check is skipped and an unknown option shows up as an engine error at the first message.

If the mapping has a `voice` key and the voice field is set too, the voice field wins.

| Engine | Options | Example |
|--------|---------|---------|
| Microsoft Edge TTS | `rate`, `pitch`, `volume` | `rate: "+10%"`, `pitch: "-5Hz"`, `volume: "+20%"` |
| Piper (Wyoming) | `speaker`, `audio_output` | `speaker: "0"` (multi-speaker voices only) |

Example for Edge, slightly faster and lower:

```yaml
rate: "+10%"
pitch: "-5Hz"
```

## Choosing the timeouts

Each timeout covers only the time until that engine sends its first audio. Once audio has started arriving, the rest of the message is collected without a time limit.

**Primary timeout**
- Too low: a working primary is skipped on longer sentences or a slow connection, and the fallback voice is heard more often than needed.
- Too high: when the primary hangs, the satellite stays silent for that long before the fallback starts.

**Fallback timeout**
- Nothing comes after the fallback, so this only bounds how long a hung fallback can block the call before it fails. Keep it well above the time the fallback needs for a long sentence.

Start with the defaults (3 s and 30 s), then look at the failover warnings in the log (see [How it works](how-it-works.md#logging)).
