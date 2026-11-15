"""Constants for TTS Fallback."""

DOMAIN = "tts_fallback"

CONF_NAME = "name"
CONF_PRIMARY_ENGINE = "primary_engine"
CONF_PRIMARY_VOICE = "primary_voice"
CONF_PRIMARY_OPTIONS = "primary_options"
CONF_FALLBACK_ENGINE = "fallback_engine"
CONF_FALLBACK_VOICE = "fallback_voice"
CONF_FALLBACK_OPTIONS = "fallback_options"
CONF_LANGUAGE = "language"
CONF_TIMEOUT = "timeout"
CONF_FALLBACK_TIMEOUT = "fallback_timeout"

DEFAULTS = {
    CONF_NAME: "Voce con fallback",
    CONF_PRIMARY_ENGINE: "tts.edge_tts",
    CONF_PRIMARY_VOICE: "it-IT-IsabellaNeural",
    CONF_FALLBACK_ENGINE: "tts.piper",
    CONF_FALLBACK_VOICE: "it_IT-serena-medium",
    CONF_LANGUAGE: "it-IT",
    CONF_TIMEOUT: 3,
    CONF_FALLBACK_TIMEOUT: 30,
}
