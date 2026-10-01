"""Central configuration loaded from environment / .env file."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ROOT_DIR / "data"
CACHE_DIR = DATA_DIR / "cache"
RECORDINGS_DIR = DATA_DIR / "recordings"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
KB_DIR = DATA_DIR / "kb"

for _d in (DATA_DIR, CACHE_DIR, RECORDINGS_DIR, TRANSCRIPTS_DIR, KB_DIR):
    _d.mkdir(parents=True, exist_ok=True)


def _env(name: str, default: str = "") -> str:
    val = os.getenv(name)
    return default if val is None or val.strip() == "" else val.strip()


def _env_bool(name: str, default: bool) -> bool:
    return _env(name, str(default)).lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    openai_api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY"))
    openai_base_url: str = field(default_factory=lambda: _env("OPENAI_BASE_URL"))
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", "gpt-4o-mini"))
    asr_model: str = field(default_factory=lambda: _env("ASR_MODEL", "whisper-1"))
    embedding_model: str = field(default_factory=lambda: _env("EMBEDDING_MODEL", "text-embedding-3-small"))
    openai_tts_model: str = field(default_factory=lambda: _env("OPENAI_TTS_MODEL", "tts-1"))
    openai_tts_voice: str = field(default_factory=lambda: _env("OPENAI_TTS_VOICE", "alloy"))

    tts_provider: str = field(default_factory=lambda: _env("TTS_PROVIDER", "edge"))
    tts_voice_en: str = field(default_factory=lambda: _env("TTS_VOICE_EN", "en-US-AriaNeural"))
    tts_voice_fil: str = field(default_factory=lambda: _env("TTS_VOICE_FIL", "fil-PH-BlessicaNeural"))
    tts_voice_id: str = field(default_factory=lambda: _env("TTS_VOICE_ID", "id-ID-GadisNeural"))

    host: str = field(default_factory=lambda: _env("HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(_env("PORT", "8000")))
    log_level: str = field(default_factory=lambda: _env("LOG_LEVEL", "INFO"))

    escalation_webhook_url: str = field(default_factory=lambda: _env("ESCALATION_WEBHOOK_URL"))
    crm_file: Path = field(default_factory=lambda: ROOT_DIR / _env("CRM_FILE", "data/crm/leads.jsonl"))

    q4_chunk_seconds: float = field(default_factory=lambda: float(_env("Q4_CHUNK_SECONDS", "3")))
    q4_confidence_threshold: float = field(default_factory=lambda: float(_env("Q4_CONFIDENCE_THRESHOLD", "0.65")))
    q4_cooldown_seconds: float = field(default_factory=lambda: float(_env("Q4_COOLDOWN_SECONDS", "45")))
    q4_nudge_ttl_seconds: float = field(default_factory=lambda: float(_env("Q4_NUDGE_TTL_SECONDS", "60")))
    q4_use_llm_signals: bool = field(default_factory=lambda: _env_bool("Q4_USE_LLM_SIGNALS", True))

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)


settings = Settings()
