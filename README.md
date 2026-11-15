<div align="center">
  <h1>🗣️ TTS Fallback</h1>
  <p><em>Home Assistant text-to-speech entity that switches to a backup engine when the main one fails</em></p>
  <br>
  <a href="https://github.com/VoidElle/hass-tts-fallback/releases"><img src="https://img.shields.io/github/v/release/VoidElle/hass-tts-fallback?style=flat-square&label=version" alt="version"></a>
  <a href="https://github.com/VoidElle/hass-tts-fallback/commits"><img src="https://img.shields.io/github/last-commit/VoidElle/hass-tts-fallback?style=flat-square" alt="last commit"></a>
  <br>
  <a href="https://my.home-assistant.io/redirect/marketplace_repository/?owner=VoidElle&repository=hass-tts-fallback&category=integration"><img src="https://img.shields.io/badge/Marketplace-custom%20repository-41BDF5?style=flat-square&logo=home-assistant" alt="Marketplace"></a>
  <a href="https://www.home-assistant.io/"><img src="https://img.shields.io/badge/Home%20Assistant-%E2%89%A52026.11-41BDF5?style=flat-square&logo=home-assistant" alt="Home Assistant"></a>
</div>

Home Assistant has no built-in way to fall back from one TTS engine to another. If a cloud voice stops answering, or the internet is down, an Assist satellite stays silent.

TTS Fallback adds one TTS entity, **Voce con fallback** (`tts.voce_con_fallback`). It renders each message with a **primary** engine. If that engine fails or is too slow, it renders the same message with a **fallback** engine. The entity can be used anywhere a TTS engine is accepted: an Assist pipeline, `tts.speak`, or a media player.

Typical setup: [Microsoft Edge TTS](https://github.com/hasscc/hass-edge-tts) (`it-IT-IsabellaNeural`) as primary, a local [Piper](https://github.com/rhasspy/piper) voice (`it_IT-serena-medium`) as fallback.

## Features ✨
- 🔁 **Automatic fallback**: on an error, on empty audio, or when the primary produces no audio within the timeout
- ⏱️ **Time-to-first-audio timeout**: a slow primary is abandoned after a set time (3 s by default), not after the whole message
- 🌍 **Language mapping**: each engine gets the language in its own spelling (`it-IT`, `it_IT`, `it`)
- 🎙️ **Per-engine voice and options**: voice picked from the engine's list (or typed), plus any other option the engine accepts (rate, pitch, speaker, ...)
- 🧩 **UI configuration**: engines, voices, options, language and both timeouts set up and changed from **Settings**, no YAML
- 🪵 **Logged failures**: every failover writes a warning with the engine and the reason

## Requirements 📋
- Home Assistant **2026.11** or newer
- Two TTS engines already set up as entities (for example `tts.edge_tts` and `tts.piper`)

## Installation 📦
### Via the Marketplace (custom repository) ⭐
1. Go to **Settings** > **Marketplace** (admin users only)
2. Add `https://github.com/VoidElle/hass-tts-fallback` as a custom repository of type **Integration**
3. Search for "TTS Fallback", select **Install**
4. Restart Home Assistant 🔄

### Manual Installation 🔧
1. Copy the `custom_components/tts_fallback/` folder into your Home Assistant `custom_components` directory (keep the folder name `tts_fallback`)
2. Restart Home Assistant

## Add the Integration to Home Assistant 🧩
1. Go to **Settings -> Devices & Services**
2. Click **+ Add Integration**
3. Search for **"TTS Fallback"**
4. Fill in the two steps of the form:

**Step 1: Engines**

| Field | Default | Description |
|---|---|---|
| Name | `Voce con fallback` | Name of the entity (gives `tts.voce_con_fallback`) |
| Primary engine | `tts.edge_tts` | TTS entity tried first |
| Fallback engine | `tts.piper` | TTS entity used when the primary fails |
| Language | `it-IT` | Language this entity speaks |
| Primary timeout | `3` s | Longest wait for the primary's first audio (0.5–30 s) |
| Fallback timeout | `30` s | Longest wait for the fallback's first audio (1–120 s) |

**Step 2: Voices and engine options**

| Field | Default | Description |
|---|---|---|
| Primary voice | `it-IT-IsabellaNeural` | Dropdown of the engine's voices when it lists them, or any typed name. Empty = engine default |
| Primary extra options | | Other options for the primary, as YAML (e.g. Edge `rate`, `pitch`, `volume`) |
| Fallback voice | `it_IT-serena-medium` | As above, for the fallback |
| Fallback extra options | | Other options for the fallback (e.g. Piper `speaker`) |

The form lists the options each engine accepts and rejects the others. Everything except the name can be changed later with **Configure** on the integration entry; saving reloads the entry.

Full field reference: [Configuration](docs/configuration.md).

## Use it in Assist 🎤
1. Go to **Settings -> Voice assistants** and open your pipeline
2. Under **Text-to-speech**, pick **Voce con fallback** and the language
3. Save

Testing the failover and reading pipeline timings: [Assist pipeline](docs/assist-pipeline.md).

## How it works ⚙️
For each message:
1. The primary engine renders it, with the configured voice and options and with file caching off.
2. If the primary raises an error, returns no audio, or sends no audio before the timeout, a warning is logged and the fallback engine renders the message, within its own timeout (30 s by default).
3. The audio of the engine that answered is returned in that engine's format (Edge: mp3, Piper: wav). Home Assistant converts it to the format the caller asks for.
4. If both engines fail, the call fails with an error that lists both reasons.

Details: [How it works](docs/how-it-works.md).

## Limitations ⚠️
- **No streaming input.** The entity waits for the full text before speaking. With an LLM conversation agent, a pipeline that used a streaming engine (such as Piper over Wyoming) starts speaking long answers later.
- **Cached fallback audio.** Home Assistant caches this entity's output per message. A message once rendered by the fallback keeps the fallback voice until the TTS cache is cleared.
- **No per-call options.** A call to the entity cannot pass options such as `voice`; it uses the voices and options set in the entry. Only Home Assistant's preferred-format options (`preferred_format`, sample rate, and so on) pass through.
- **Two engines.** The chain is one primary and one fallback. For a third voice, chain a second TTS Fallback entity as the fallback of the first. Loops (A falls back to B, B falls back to A) are refused by **Configure** and stopped at runtime: see [How it works](docs/how-it-works.md#loops).
- **Edge TTS is unofficial.** It relies on a Microsoft service that is not a public API and can stop working, which is the reason this integration exists.

## Documentation 📖
[Index](docs/index.md) · [Configuration](docs/configuration.md) · [How it works](docs/how-it-works.md) · [Assist pipeline](docs/assist-pipeline.md)

## Troubleshooting 🔍

### Integration not found after installation
Restart Home Assistant fully after installing. Reloading the Marketplace is not enough.

### The fallback voice is always used
- Check the log for `TTS engine tts.edge_tts failed (...)`: the reason says why the primary was skipped.
- `timeout after 3.0s`: the primary is too slow for the timeout. Raise **Primary timeout** with **Configure**.
- `engine not found`: the primary entity ID is wrong or the engine is not loaded yet.
- A voice error: check the voice name. Edge voices look like `it-IT-IsabellaNeural`, Piper voices like `it_IT-serena-medium`.
- If the message was answered by the fallback once, it may be served from the cache: see [Limitations](#limitations-).

### "All TTS engines failed"
Both engines failed for that message. The error lists the reason for each one. Test each engine on its own with `tts.speak` from **Developer Tools → Actions**.

### Wrong language or accent
Set **Language** to the language of the voices (for example `it-IT`). Each engine receives the closest spelling it supports; when none matches, the engine uses its default language and the voice name decides the accent.

## Debugging / Logging 🪵
Failovers are logged as warnings by default. For more detail, add to `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.tts_fallback: debug
    homeassistant.components.tts: debug
```

| Logger | Covers |
|---|---|
| `custom_components.tts_fallback` | This integration (failover warnings) |
| `homeassistant.components.tts` | Home Assistant TTS manager, cache and audio conversion |

Log levels can also be changed at runtime with the `logger.set_level` action.

## Tested On 🧪
- Home Assistant OS 18.5, Core 2026.11.1, Raspberry Pi 5
- Primary: Microsoft Edge TTS (`hasscc/hass-edge-tts` 0.7.8), voice `it-IT-IsabellaNeural`
- Fallback: Piper (Wyoming), voice `it_IT-serena-medium`

## Contributing 🤝
Contributions are welcome.
- 🐛 **Report bugs** via [GitHub Issues](https://github.com/VoidElle/hass-tts-fallback/issues)
- 🌍 **Translate** to more languages (`custom_components/tts_fallback/translations/`)
- 🔧 **Submit PRs** via [GitHub Pull requests](https://github.com/VoidElle/hass-tts-fallback/pulls)

### Development
1. Fork and clone the repository
2. Create a feature branch: `git checkout -b feature/name`
3. Follow the [Home Assistant dev guidelines](https://developers.home-assistant.io/)
4. Run the self-check, which needs no Home Assistant install:

```bash
python3 test_helpers.py
```

5. Submit a PR with a clear description
