"""Gap scanner & news briefing.

Turns a ranked list of gappers into a neutral, readable pre-market briefing
written by Claude. This is informational only — not financial advice.
"""
from __future__ import annotations

from ..assistant.claude_client import ClaudeAssistant
from ..models import Gap


def build_prompt(gappers: list[Gap]) -> str:
    """Render the structured gap data into a prompt for the briefing."""
    if not gappers:
        return (
            "No symbols passed the pre-market gap filters today. Write one short, "
            "neutral sentence noting a quiet pre-market."
        )

    lines = [
        "Here are today's pre-market gappers (sorted by absolute gap size). "
        "Write a concise briefing of ~120-180 words that, for the most notable names, "
        "describes the move and any publicly reported catalyst (earnings, guidance, "
        "M&A, FDA, analyst actions, macro). Group by up-gaps and down-gaps. Stay "
        "neutral and do not recommend any action.",
        "",
        "| Symbol | Last | Prev close | Gap % | Rel. volume |",
        "| ------ | ---- | ---------- | ----- | ----------- |",
    ]
    for g in gappers:
        rv = f"{g.rel_volume:.2f}x" if g.rel_volume is not None else "n/a"
        lines.append(
            f"| {g.symbol} | {g.last:.2f} | {g.prev_close:.2f} | {g.gap_pct:+.2f}% | {rv} |"
        )
    return "\n".join(lines)


def write_briefing(
    gappers: list[Gap],
    *,
    assistant: ClaudeAssistant | None = None,
) -> str:
    """Generate the natural-language briefing. Requires an Anthropic API key."""
    assistant = assistant or ClaudeAssistant()
    return assistant.write(build_prompt(gappers))
