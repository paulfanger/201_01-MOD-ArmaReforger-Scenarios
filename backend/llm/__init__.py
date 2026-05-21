"""
LLM integration layer with Anthropic Prompt Caching.

Uses ephemeral cache_control for stable system-prompt prefixes to reduce
repeat costs during multi-turn mission authoring sessions.

Model: claude-sonnet-4-6 for generation, claude-haiku-* for fast classification.
"""

import os
from typing import Any

import anthropic

# ---------------------------------------------------------------------------
# Client singleton (re-used across calls to maximise cache warm-up)
# ---------------------------------------------------------------------------

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        _client = anthropic.Anthropic(api_key=api_key)  # None = use ANTHROPIC_API_KEY
    return _client


# ---------------------------------------------------------------------------
# System-prompt prefix (stable across session → gets cached)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_PREFIX = """You are a mission-authoring specialist for the Arma Reforger
game engine (Enfusion). You produce structured JSON outputs only.
Your outputs will be validated against JSON schemas before being written to disk.
Never include prose outside JSON unless the caller explicitly requests it.
Always preserve existing mission intent unless the revision instruction explicitly
changes it."""


def _make_cached_system(extra: str = "") -> list[dict]:
    """Build a system-content list where the prefix block is marked for caching."""
    blocks: list[dict] = [
        {
            "type": "text",
            "text": SYSTEM_PROMPT_PREFIX,
            "cache_control": {"type": "ephemeral"},  # Anthropic prompt caching
        }
    ]
    if extra:
        blocks.append({"type": "text", "text": extra})
    return blocks


# ---------------------------------------------------------------------------
# cached_completion — primary public API
# ---------------------------------------------------------------------------

def cached_completion(
    messages: list[dict],
    *,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 4096,
    system_extra: str = "",
    temperature: float = 0.3,
) -> str:
    """
    Run a completion with prompt caching on the stable system prefix.

    Args:
        messages:     List of {"role": "user"|"assistant", "content": str} dicts.
        model:        Anthropic model ID.
        max_tokens:   Maximum output tokens.
        system_extra: Optional additional system context (NOT cached — mission-specific).
        temperature:  Sampling temperature.

    Returns:
        The assistant reply as a plain string.
    """
    client = _get_client()
    system_blocks = _make_cached_system(system_extra)

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_blocks,
        messages=messages,
        temperature=temperature,
    )

    # Extract first text block
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


def quick_classify(
    prompt: str,
    *,
    model: str = "claude-haiku-4-5",
    max_tokens: int = 256,
) -> str:
    """
    Lightweight classify call (no caching — too short to benefit).
    Used by ui-tester, loop-detector, etc.
    """
    client = _get_client()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""
