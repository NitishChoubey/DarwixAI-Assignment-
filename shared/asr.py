"""Speech-to-text wrapper.

Design notes
------------
* Provider: OpenAI Whisper (`whisper-1`). Whisper is multilingual and handles
  code-switching (Taglish, Bahasa + English loanwords) reasonably well when it
  is *not* forced to a single language. We therefore expose two knobs:
    - `language`: ISO-639-1 hint ("en", "tl", "id"). Pass None to auto-detect,
      which is what we use for code-switched markets.
    - `vocabulary_prompt`: domain glossary injected as Whisper's `prompt`
      (e.g. "cicilan, tenor, denda, jatuh tempo") which strongly biases
      recognition of finance terms and local words.
* Every call returns latency in ms so Q4 can report per-chunk ASR latency.
"""
from __future__ import annotations

import io
import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional

from .config import settings
from .llm import get_client

log = logging.getLogger(__name__)


@dataclass
class ASRResult:
    text: str
    language: Optional[str]
    latency_ms: float
    segments: List[dict] = field(default_factory=list)
    fallback: bool = False


def transcribe_bytes(
    audio: bytes,
    filename: str = "audio.wav",
    *,
    language: Optional[str] = None,
    vocabulary_prompt: Optional[str] = None,
    verbose: bool = True,
) -> ASRResult:
    client = get_client()
    t0 = time.perf_counter()
    if client is None:
        return ASRResult(text="", language=language, latency_ms=0.0, fallback=True)

    buf = io.BytesIO(audio)
    buf.name = filename  # the SDK infers the container from the name
    kwargs = {"model": settings.asr_model, "file": buf}
    if language:
        kwargs["language"] = language
    if vocabulary_prompt:
        kwargs["prompt"] = vocabulary_prompt[:800]
    if verbose:
        kwargs["response_format"] = "verbose_json"

    try:
        resp = client.audio.transcriptions.create(**kwargs)
    except Exception as exc:  # noqa: BLE001
        log.error("ASR failed: %s", exc)
        return ASRResult(text="", language=language, latency_ms=(time.perf_counter() - t0) * 1000, fallback=True)

    latency = (time.perf_counter() - t0) * 1000.0
    text = (getattr(resp, "text", "") or "").strip()
    detected = getattr(resp, "language", None) or language
    segments = []
    for seg in getattr(resp, "segments", None) or []:
        segments.append(
            {
                "start": getattr(seg, "start", None),
                "end": getattr(seg, "end", None),
                "text": getattr(seg, "text", ""),
                "no_speech_prob": getattr(seg, "no_speech_prob", None),
                "avg_logprob": getattr(seg, "avg_logprob", None),
            }
        )
    return ASRResult(text=text, language=detected, latency_ms=latency, segments=segments)


def transcribe_file(path: str, **kw) -> ASRResult:
    with open(path, "rb") as fh:
        return transcribe_bytes(fh.read(), filename=path.split("/")[-1].split("\\")[-1], **kw)
