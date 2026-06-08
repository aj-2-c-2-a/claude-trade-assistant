"""Generate a ready-to-paste TradingView Pine Script alert template.

TradingView does not expose a data API; instead it fires *alerts* whose JSON
payload is delivered to a webhook. This helper emits a small Pine v5 study with
an `alertcondition` and a JSON message shaped for our webhook receiver.
"""
from __future__ import annotations


def alert_pine_script(secret_placeholder: str = "YOUR_WEBHOOK_SECRET") -> str:
    """Return Pine v5 source that fires a JSON alert our webhook understands.

    Paste it into the TradingView Pine Editor, add to chart, then create an alert
    with "Once Per Bar Close" and set the webhook URL to your receiver's /tv-alert.
    """
    return f'''//@version=5
indicator("Claude Trade Assistant — Alert Bridge", overlay=true)

// --- Example signal: a simple breakout above the prior day's high. ---
// Replace this with your own condition; only the alert payload matters.
prevHigh = request.security(syminfo.tickerid, "D", high[1], lookahead=barmerge.lookahead_on)
breakout = ta.crossover(close, prevHigh)
plotshape(breakout, title="Signal", style=shape.triangleup, location=location.belowbar, size=size.tiny)

// --- JSON payload sent to the Claude Trade Assistant webhook. ---
// {{ticker}} and {{close}} are TradingView placeholders, filled at alert time.
alertMsg = '{{"secret":"{secret_placeholder}","symbol":"{{{{ticker}}}}","price":{{{{close}}}},"signal":"breakout"}}'
alertcondition(breakout, title="CTA breakout", message=alertMsg)
'''
