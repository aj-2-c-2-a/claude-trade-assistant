"""Pure, network-free gap math so it can be unit-tested in isolation.

A "gap" is the percentage move of the latest (pre-market) price relative to the
previous regular-session close:

    gap_pct = (last - prev_close) / prev_close * 100
"""
from __future__ import annotations

from ..models import Gap, Quote


def compute_gap(quote: Quote) -> Gap:
    """Compute the gap for a single quote.

    Raises:
        ValueError: if prev_close is non-positive (cannot form a percentage).
    """
    if quote.prev_close <= 0:
        raise ValueError(f"{quote.symbol}: prev_close must be positive, got {quote.prev_close}")

    gap_pct = (quote.last - quote.prev_close) / quote.prev_close * 100.0
    rel_volume = None
    if quote.volume is not None and quote.avg_volume:
        rel_volume = quote.volume / quote.avg_volume

    return Gap(
        symbol=quote.symbol,
        last=quote.last,
        prev_close=quote.prev_close,
        gap_pct=round(gap_pct, 2),
        direction="up" if gap_pct >= 0 else "down",
        volume=quote.volume,
        rel_volume=round(rel_volume, 2) if rel_volume is not None else None,
    )


def scan_gaps(
    quotes: list[Quote],
    *,
    min_abs_gap_pct: float = 4.0,
    min_rel_volume: float | None = None,
    direction: str = "both",  # "up" | "down" | "both"
    limit: int | None = None,
) -> list[Gap]:
    """Filter and rank a list of quotes into the most significant gappers.

    Args:
        min_abs_gap_pct: keep only gaps whose absolute size is at least this.
        min_rel_volume: if set, require relative volume >= this value.
        direction: restrict to "up", "down", or "both".
        limit: cap the number of returned rows after ranking.

    Returns:
        Gaps sorted by absolute gap size, largest first.
    """
    gaps: list[Gap] = []
    for q in quotes:
        try:
            g = compute_gap(q)
        except ValueError:
            continue  # skip symbols we can't price
        if g.abs_gap_pct < min_abs_gap_pct:
            continue
        if direction != "both" and g.direction != direction:
            continue
        if min_rel_volume is not None and (g.rel_volume is None or g.rel_volume < min_rel_volume):
            continue
        gaps.append(g)

    gaps.sort(key=lambda g: g.abs_gap_pct, reverse=True)
    return gaps[:limit] if limit else gaps
