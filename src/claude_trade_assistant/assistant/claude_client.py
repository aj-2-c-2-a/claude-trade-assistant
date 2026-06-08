"""Thin wrapper around the official Anthropic Python SDK.

Used to turn structured scan data into a readable, neutral market briefing.
The assistant is explicitly instructed to describe — not to recommend trades.
"""
from __future__ import annotations

import logging
import os

log = logging.getLogger(__name__)

# Sensible default. Override via config or CLA_MODEL.
#   claude-opus-4-8    -> most capable
#   claude-sonnet-4-6  -> best balance of cost/quality (default)
#   claude-haiku-4-5-20251001 -> fastest/cheapest
DEFAULT_MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = (
    "You are a markets desk assistant that writes concise, neutral pre-market "
    "briefings for an informed reader. Summarize what is moving and the publicly "
    "reported reasons. Be factual and balanced. Do NOT give buy/sell/hold "
    "recommendations, price targets, or position sizing. Do NOT predict prices. "
    "If a reason is unknown, say so plainly. Always assume the reader makes their "
    "own decisions."
)


class ClaudeAssistant:
    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:  # pragma: no cover
            raise ImportError("The `anthropic` package is required (`pip install anthropic`).") from exc

        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("Set ANTHROPIC_API_KEY (get one at https://console.anthropic.com).")

        self.client = Anthropic(api_key=key)
        self.model = model or os.getenv("CLA_MODEL") or DEFAULT_MODEL

    def write(self, prompt: str, *, max_tokens: int = 900) -> str:
        """Send a single prompt and return Claude's text response."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = [block.text for block in message.content if getattr(block, "type", None) == "text"]
        return "\n".join(parts).strip()
