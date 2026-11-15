# TTS Fallback — Documentation

Home Assistant integration that adds one TTS entity. It renders speech with a **primary** engine and switches to a **fallback** engine when the primary fails, returns no audio, or is too slow.

---

## Contents

| Page | Description |
|------|-------------|
| [Configuration](configuration.md) | Setup form, every field, voices, extra engine options, timeouts |
| [How it works](how-it-works.md) | Failover rules, timeouts, language mapping, audio format, caching |
| [Assist pipeline](assist-pipeline.md) | Using the entity in a voice pipeline, testing the failover, timings |

---

## Quick Start

### Requirements
- Home Assistant ≥ 2026.11
- Two TTS engines set up as entities, for example `tts.edge_tts` (cloud) and `tts.piper` (local)

### Installation
Via the Marketplace: add `https://github.com/VoidElle/hass-tts-fallback` as a custom repository of type **Integration**, install **TTS Fallback**, restart Home Assistant.

Manual: copy `custom_components/tts_fallback/` into your Home Assistant `custom_components/` directory, restart.

### Adding the entity
1. **Settings → Devices & Services → + Add Integration**
2. Search **TTS Fallback**
3. Step 1: name, primary and fallback engines, language, timeouts. Step 2: voices and extra engine options
4. Use `tts.tts_fallback` as the TTS engine of your Assist pipeline

---

## Tested Setup

| Role | Engine | Voice |
|------|--------|-------|
| Primary | Microsoft Edge TTS (`hasscc/hass-edge-tts` 0.7.8) | `it-IT-IsabellaNeural` |
| Fallback | Piper over Wyoming | `it_IT-serena-medium` |

Home Assistant OS 18.5, Core 2026.11.1, Raspberry Pi 5.
