"""TTS entity that falls back to a second engine."""

from __future__ import annotations

import asyncio
from contextvars import ContextVar
import logging
from typing import Any

from homeassistant.components.tts import ATTR_VOICE, TextToSpeechEntity, TtsAudioType
from homeassistant.components.tts.const import DATA_TTS_MANAGER
from homeassistant.components.tts.helper import get_engine_instance
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_FALLBACK_ENGINE,
    CONF_FALLBACK_OPTIONS,
    CONF_FALLBACK_TIMEOUT,
    CONF_FALLBACK_VOICE,
    CONF_LANGUAGE,
    CONF_PRIMARY_ENGINE,
    CONF_PRIMARY_OPTIONS,
    CONF_PRIMARY_VOICE,
    CONF_TIMEOUT,
    DEFAULTS,
)
from .helpers import language_variants, pick_language

_LOGGER = logging.getLogger(__name__)

# TTS Fallback entities rendering the current message. HA renders inner engines
# in tasks created from our call, and tasks copy the context, so a nested call
# sees the entities above it. Catches loops the config flow could not see.
_ACTIVE: ContextVar[frozenset[str]] = ContextVar("tts_fallback_active", default=frozenset())


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the fallback TTS entity."""
    async_add_entities([FallbackTTSEntity(entry)])


class FallbackTTSEntity(TextToSpeechEntity):
    """Speak with the primary engine; on error or timeout use the fallback."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize from the entry options."""
        opts = DEFAULTS | dict(entry.options)
        self._attr_name = entry.title
        self._attr_unique_id = entry.entry_id
        self._attr_default_language = opts[CONF_LANGUAGE]
        self._attr_supported_languages = language_variants(opts[CONF_LANGUAGE])
        # (engine, engine options, time to first audio); voice wins over extra options
        self._chain = [
            (
                opts[engine],
                dict(entry.options.get(extra) or {})
                | ({ATTR_VOICE: entry.options[voice]} if entry.options.get(voice) else {}),
                float(opts[timeout]),
            )
            for engine, voice, extra, timeout in (
                (CONF_PRIMARY_ENGINE, CONF_PRIMARY_VOICE, CONF_PRIMARY_OPTIONS, CONF_TIMEOUT),
                (CONF_FALLBACK_ENGINE, CONF_FALLBACK_VOICE, CONF_FALLBACK_OPTIONS, CONF_FALLBACK_TIMEOUT),
            )
        ]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Try each engine in order and return the first audio produced."""
        active = _ACTIVE.get()
        if self.entity_id in active:
            raise HomeAssistantError(f"loop: {self.entity_id} is already rendering this message")
        token = _ACTIVE.set(active | {self.entity_id})
        try:
            failures: list[str] = []
            for engine, engine_options, timeout in self._chain:
                try:
                    return await self._generate(engine, engine_options, message, language, timeout)
                except Exception as err:  # noqa: BLE001 - any engine failure means fall back
                    reason = f"timeout after {timeout}s" if isinstance(err, TimeoutError) else repr(err)
                    _LOGGER.warning("TTS engine %s failed (%s)", engine, reason)
                    failures.append(f"{engine}: {reason}")
            raise HomeAssistantError(f"All TTS engines failed: {'; '.join(failures)}")
        finally:
            _ACTIVE.reset(token)

    async def _generate(
        self,
        engine: str,
        engine_options: dict[str, Any],
        message: str,
        language: str,
        timeout: float,
    ) -> tuple[str, bytes]:
        """Render the message with one engine, bounded by time to first audio."""
        if engine in _ACTIVE.get():
            raise HomeAssistantError(f"loop: {engine} is already rendering this message")
        if (instance := get_engine_instance(self.hass, engine)) is None:
            raise HomeAssistantError("engine not found")
        stream = self.hass.data[DATA_TTS_MANAGER].async_create_result_stream(
            engine=engine,
            # This entity's own output is cached by HA; skip a second copy.
            use_file_cache=False,
            language=pick_language(language, instance.supported_languages or []),
            options=engine_options,
        )
        stream.async_set_message(message)
        chunks = stream.async_stream_result()
        try:
            async with asyncio.timeout(timeout):
                first = await anext(chunks)
            data = first + b"".join([chunk async for chunk in chunks])
        finally:
            await chunks.aclose()
        if not data:
            raise HomeAssistantError("empty audio")
        return stream.extension, data
