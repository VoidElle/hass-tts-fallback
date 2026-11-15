"""Constants for TTS Fallback."""

DOMAIN = "tts_fallback"

CONF_PRIMARY_ENGINE = "primary_engine"
CONF_PRIMARY_VOICE = "primary_voice"
CONF_FALLBACK_ENGINE = "fallback_engine"
CONF_FALLBACK_VOICE = "fallback_voice"
CONF_LANGUAGE = "language"
CONF_TIMEOUT = "timeout"

DEFAULT_TITLE = "Voce con fallback"
DEFAULTS = {
    CONF_PRIMARY_ENGINE: "tts.edge_tts",
    CONF_PRIMARY_VOICE: "it-IT-IsabellaNeural",
    CONF_FALLBACK_ENGINE: "tts.piper",
    CONF_FALLBACK_VOICE: "it_IT-serena-medium",
    CONF_LANGUAGE: "it-IT",
    CONF_TIMEOUT: 3,
}

# The last engine in the chain has nothing to fall back to, so it gets time.
FALLBACK_TIMEOUT = 30
