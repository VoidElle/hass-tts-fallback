"""Config and options flow for TTS Fallback.

Two steps, the same in setup and in Configure:
1. engines, language and timeouts
2. voices and extra options, with the voice lists of the engines picked in step 1
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.tts.helper import get_engine_instance
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    ObjectSelector,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .const import (
    CONF_FALLBACK_ENGINE,
    CONF_FALLBACK_OPTIONS,
    CONF_FALLBACK_TIMEOUT,
    CONF_FALLBACK_VOICE,
    CONF_LANGUAGE,
    CONF_NAME,
    CONF_PRIMARY_ENGINE,
    CONF_PRIMARY_OPTIONS,
    CONF_PRIMARY_VOICE,
    CONF_TIMEOUT,
    DEFAULTS,
    DOMAIN,
)
from .helpers import find_loop, pick_language

# (engine key, voice key, extra options key) per position in the chain
_ENGINES = (
    (CONF_PRIMARY_ENGINE, CONF_PRIMARY_VOICE, CONF_PRIMARY_OPTIONS),
    (CONF_FALLBACK_ENGINE, CONF_FALLBACK_VOICE, CONF_FALLBACK_OPTIONS),
)


def _seconds(minimum: float, maximum: float) -> NumberSelector:
    return NumberSelector(
        NumberSelectorConfig(
            min=minimum,
            max=maximum,
            step=0.5,
            unit_of_measurement="s",
            mode=NumberSelectorMode.BOX,
        )
    )


def _engines_schema(exclude: list[str], with_name: bool) -> vol.Schema:
    engine = EntitySelector(EntitySelectorConfig(domain="tts", exclude_entities=exclude))
    fields: dict[Any, Any] = {vol.Required(CONF_NAME): TextSelector()} if with_name else {}
    fields |= {
        vol.Required(CONF_PRIMARY_ENGINE): engine,
        vol.Required(CONF_FALLBACK_ENGINE): engine,
        vol.Required(CONF_LANGUAGE): TextSelector(),
        vol.Required(CONF_TIMEOUT): _seconds(0.5, 30),
        vol.Required(CONF_FALLBACK_TIMEOUT): _seconds(1, 120),
    }
    return vol.Schema(fields)


def _validate_engines(user_input: dict[str, Any]) -> dict[str, str]:
    if user_input[CONF_PRIMARY_ENGINE] == user_input[CONF_FALLBACK_ENGINE]:
        return {"base": "same_engine"}
    return {}


def _find_loop(
    hass: HomeAssistant, own_entry_id: str, user_input: dict[str, Any]
) -> list[str] | None:
    """Loop this entry would close among TTS Fallback entities, with user_input applied."""
    registry = er.async_get(hass)
    graph: dict[str, list[str]] = {}
    own = None
    for entry in hass.config_entries.async_entries(DOMAIN):
        if (entity_id := registry.async_get_entity_id("tts", DOMAIN, entry.entry_id)) is None:
            continue
        options = user_input if entry.entry_id == own_entry_id else entry.options
        graph[entity_id] = [
            engine
            for key in (CONF_PRIMARY_ENGINE, CONF_FALLBACK_ENGINE)
            if (engine := options.get(key))
        ]
        if entry.entry_id == own_entry_id:
            own = entity_id
    return find_loop(graph, own) if own else None


def _voice_selector(hass: HomeAssistant, engine: str, language: str) -> SelectSelector:
    """Dropdown of the engine's voices; any other name can still be typed."""
    voices = []
    instance = get_engine_instance(hass, engine)
    if instance is not None and (lang := pick_language(language, instance.supported_languages or [])):
        voices = instance.async_get_supported_voices(lang) or []
    return SelectSelector(
        SelectSelectorConfig(
            options=[SelectOptionDict(value=v.voice_id, label=v.name) for v in voices],
            custom_value=True,
            sort=True,
            mode=SelectSelectorMode.DROPDOWN,
        )
    )


def _supported_options(hass: HomeAssistant, engine: str) -> list[str]:
    instance = get_engine_instance(hass, engine)
    return list(instance.supported_options or []) if instance else []


def _voices_schema(hass: HomeAssistant, data: dict[str, Any]) -> vol.Schema:
    fields: dict[Any, Any] = {}
    for engine_key, voice_key, options_key in _ENGINES:
        fields[vol.Optional(voice_key)] = _voice_selector(
            hass, data[engine_key], data[CONF_LANGUAGE]
        )
        fields[vol.Optional(options_key)] = ObjectSelector()
    return vol.Schema(fields)


def _voices_placeholders(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    return {
        f"{options_key}_supported": ", ".join(_supported_options(hass, data[engine_key])) or "-"
        for engine_key, _, options_key in _ENGINES
    }


def _validate_voices(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Extra options must be a mapping of options the engine accepts."""
    for engine_key, _, options_key in _ENGINES:
        extra = data.get(options_key) or {}
        if not isinstance(extra, dict):
            return {options_key: "not_a_mapping"}
        supported = _supported_options(hass, data[engine_key])
        if get_engine_instance(hass, data[engine_key]) and set(extra) - set(supported):
            return {options_key: "unsupported_options"}
    return {}


def _suggested_voices(engines: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    """Keep voice and options of an engine that did not change."""
    suggested = {}
    for engine_key, voice_key, options_key in _ENGINES:
        if previous.get(engine_key) == engines[engine_key]:
            for key in (voice_key, options_key):
                if previous.get(key):
                    suggested[key] = previous[key]
    return suggested


class TTSFallbackConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create a fallback voice."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick engines, language and timeouts."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not (errors := _validate_engines(user_input)):
                self._data = user_input
                return await self.async_step_voices()
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                _engines_schema([], with_name=True), user_input or DEFAULTS
            ),
            errors=errors,
        )

    async def async_step_voices(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick a voice and extra options per engine."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not (errors := _validate_voices(self.hass, self._data | user_input)):
                options = self._data | user_input
                title = options.pop(CONF_NAME)
                return self.async_create_entry(title=title, data={}, options=options)
        return self.async_show_form(
            step_id="voices",
            data_schema=self.add_suggested_values_to_schema(
                _voices_schema(self.hass, self._data),
                user_input or _suggested_voices(self._data, DEFAULTS),
            ),
            description_placeholders=_voices_placeholders(self.hass, self._data),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> TTSFallbackOptionsFlow:
        """Return the options flow."""
        return TTSFallbackOptionsFlow()


class TTSFallbackOptionsFlow(OptionsFlowWithReload):
    """Change engines, voices, options and timeouts."""

    def __init__(self) -> None:
        """Initialize."""
        self._data: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Edit engines, language and timeouts."""
        errors: dict[str, str] = {}
        placeholders = {"loop": ""}
        if user_input is not None:
            errors = _validate_engines(user_input)
            if not errors and (
                loop := _find_loop(self.hass, self.config_entry.entry_id, user_input)
            ):
                errors = {"base": "loop"}
                placeholders["loop"] = " → ".join(loop)
            if not errors:
                self._data = user_input
                return await self.async_step_voices()
        own = er.async_get(self.hass).async_get_entity_id(
            "tts", DOMAIN, self.config_entry.entry_id
        )
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                _engines_schema([own] if own else [], with_name=False),
                user_input or (DEFAULTS | dict(self.config_entry.options)),
            ),
            description_placeholders=placeholders,
            errors=errors,
        )

    async def async_step_voices(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Edit voices and extra options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not (errors := _validate_voices(self.hass, self._data | user_input)):
                return self.async_create_entry(data=self._data | user_input)
        return self.async_show_form(
            step_id="voices",
            data_schema=self.add_suggested_values_to_schema(
                _voices_schema(self.hass, self._data),
                user_input or _suggested_voices(self._data, self.config_entry.options),
            ),
            description_placeholders=_voices_placeholders(self.hass, self._data),
            errors=errors,
        )
