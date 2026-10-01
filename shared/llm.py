"""Thin LLM wrapper around the OpenAI chat API.

Features:
- JSON-mode helper that always returns a dict (never raises on malformed JSON)
- call latency recorded in milliseconds
- deterministic, clearly-labelled fallback when no API key is configured so the
  rest of the system (KB, dashboards, test harnesses) still runs end-to-end.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .config import settings

log = logging.getLogger(__name__)

_client = None


def get_client():
    """Lazily construct the OpenAI client. Returns None when no key is set."""
    global _client
    if _client is not None:
        return _client
    if not settings.has_openai:
        return None
    from openai import OpenAI

    kwargs: Dict[str, Any] = {"api_key": settings.openai_api_key}
    if settings.openai_base_url:
        kwargs["base_url"] = settings.openai_base_url
    _client = OpenAI(**kwargs)
    return _client


@dataclass
class LLMResult:
    text: str
    latency_ms: float
    model: str
    usage: Dict[str, int]
    fallback: bool = False


def chat(
    messages: List[Dict[str, str]],
    *,
    temperature: float = 0.2,
    max_tokens: int = 400,
    json_mode: bool = False,
    model: Optional[str] = None,
) -> LLMResult:
    client = get_client()
    model = model or settings.llm_model
    t0 = time.perf_counter()
    if client is None:
        log.warning("OPENAI_API_KEY not set - returning fallback LLM response")
        text = "{}" if json_mode else "[LLM unavailable: OPENAI_API_KEY not configured]"
        return LLMResult(text=text, latency_ms=0.0, model="none", usage={}, fallback=True)

    kwargs: Dict[str, Any] = dict(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    latency = (time.perf_counter() - t0) * 1000.0
    text = resp.choices[0].message.content or ""
    usage = {}
    if resp.usage:
        usage = {"prompt_tokens": resp.usage.prompt_tokens, "completion_tokens": resp.usage.completion_tokens}
    return LLMResult(text=text, latency_ms=latency, model=model, usage=usage)


def chat_json(messages: List[Dict[str, str]], **kw) -> Dict[str, Any]:
    """Call the LLM in JSON mode and parse; returns {} on any parse failure."""
    result = chat(messages, json_mode=True, **kw)
    try:
        data = json.loads(result.text)
        if isinstance(data, dict):
            data["_latency_ms"] = result.latency_ms
            data["_fallback"] = result.fallback
            return data
    except json.JSONDecodeError:
        log.warning("LLM returned non-JSON in json_mode: %s", result.text[:200])
    return {"_latency_ms": result.latency_ms, "_fallback": result.fallback}
