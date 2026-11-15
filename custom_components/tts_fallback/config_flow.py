"""Config and options flow for TTS Fallback."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
)

from .const import (
    CONF_FALLBACK_ENGINE,
    CONF_FALLBACK_VOICE,
    CONF_LANGUAGE,
    CONF_PRIMARY_ENGINE,
    CONF_PRIMARY_VOICE,
    CONF_TIMEOUT,
    DEFAULT_TITLE,
    DEFAULTS,
    DOMAIN,
)


def _schema(exclude: list[str]) -> vol.Schema:
    engine = EntitySelector(EntitySelectorConfig(domain="tts", exclude_entities=exclude))
    return vol.Schema(
        {
            vol.Required(CONF_PRIMARY_ENGINE): engine,
            vol.Optional(CONF_PRIMARY_VOICE): TextSelector(),
            vol.Required(CONF_FALLBACK_ENGINE): engine,
            vol.Optional(CONF_FALLBACK_VOICE): TextSelector(),
            vol.Required(CONF_LANGUAGE): TextSelector(),
            vol.Required(CONF_TIMEOUT): NumberSelector(
                NumberSelectorConfig(
                    min=0.5,
                    max=30,
                    step=0.5,
                    unit_of_measurement="s",
                    mode=NumberSelectorMode.BOX,
                )
            ),
        }
    )


def _validate(user_input: dict[str, Any]) -> dict[str, str]:
    if user_input[CONF_PRIMARY_ENGINE] == user_input[CONF_FALLBACK_ENGINE]:
        return {"base": "same_engine"}
    return {}


class TTSFallbackConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create a fallback voice."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick primary and fallback engines."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not (errors := _validate(user_input)):
                return self.async_create_entry(
                    title=DEFAULT_TITLE, data={}, options=user_input
                )
        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                _schema([]), user_input or DEFAULTS
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> TTSFallbackOptionsFlow:
        """Return the options flow."""
        return TTSFallbackOptionsFlow()


class TTSFallbackOptionsFlow(OptionsFlowWithReload):
    """Change engines, voices and timeout."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Edit the chain."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not (errors := _validate(user_input)):
                return self.async_create_entry(data=user_input)
        own = er.async_get(self.hass).async_get_entity_id(
            "tts", DOMAIN, self.config_entry.entry_id
        )
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                _schema([own] if own else []),
                user_input or self.config_entry.options,
            ),
            errors=errors,
        )
