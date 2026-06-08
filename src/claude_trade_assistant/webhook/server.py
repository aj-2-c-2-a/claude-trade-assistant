"""FastAPI receiver for TradingView webhook alerts.

When a TradingView alert fires, it POSTs a JSON payload here. We authenticate it
with a shared secret, enrich it with a quote, and (optionally) ask Claude for a
short, neutral note about the symbol. This endpoint NEVER places orders.

Run it with:
    uvicorn claude_trade_assistant.webhook.server:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import logging
import os
from typing import Optional

log = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, HTTPException, Request
except ImportError as exc:  # pragma: no cover
    raise ImportError("FastAPI is required for the webhook server (`pip install fastapi uvicorn`).") from exc


app = FastAPI(title="Claude Trade Assistant — TradingView webhook")

_SECRET = os.getenv("CLA_WEBHOOK_SECRET")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "claude-trade-assistant"}


@app.post("/tv-alert")
async def tv_alert(request: Request) -> dict:
    """Receive a TradingView alert payload.

    Expected JSON: {"secret": "...", "symbol": "AAPL", "price": 123.45, "signal": "breakout"}
    """
    payload = await _parse_body(request)

    # Authenticate. If a secret is configured, the payload must match it.
    if _SECRET:
        if payload.get("secret") != _SECRET:
            raise HTTPException(status_code=401, detail="Invalid or missing webhook secret.")

    symbol = str(payload.get("symbol", "")).upper().strip()
    if not symbol:
        raise HTTPException(status_code=400, detail="Payload must include a 'symbol'.")

    note: Optional[str] = None
    if os.getenv("ANTHROPIC_API_KEY"):
        note = _safe_note(symbol, payload.get("signal"))

    log.info("TradingView alert: %s signal=%s", symbol, payload.get("signal"))
    return {
        "received": True,
        "symbol": symbol,
        "signal": payload.get("signal"),
        "price": payload.get("price"),
        "note": note,
        "disclaimer": "Informational only. Not financial advice. No order was placed.",
    }


async def _parse_body(request: Request) -> dict:
    """Accept JSON, or a raw text body that contains JSON (TradingView allows both)."""
    import json

    raw = await request.body()
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Body must be valid JSON.")


def _safe_note(symbol: str, signal) -> Optional[str]:
    try:
        from ..assistant.claude_client import ClaudeAssistant

        assistant = ClaudeAssistant()
        return assistant.write(
            f"A '{signal}' signal just fired for {symbol}. In 1-2 neutral sentences, "
            f"note what {symbol} is and any well-known recent context. Do not advise.",
            max_tokens=150,
        )
    except Exception as exc:  # never fail the webhook because of the note
        log.debug("note skipped: %s", exc)
        return None
