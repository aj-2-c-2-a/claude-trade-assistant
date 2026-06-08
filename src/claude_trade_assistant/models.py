"""Core data models shared across the assistant.

Claude Trade Assistant is an *analysis and briefing* tool. It does NOT place
orders and does NOT give financial advice. See DISCLAIMER.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Quote:
    """A normalized snapshot for a single symbol from any data provider."""

    symbol: str
    last: float
    prev_close: float
    # Optional context used for ranking and the news briefing.
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    market_cap: Optional[float] = None
    session: str = "regular"  # one of: pre, regular, post
    as_of: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Gap:
    """A computed gap for a symbol relative to the previous close."""

    symbol: str
    last: float
    prev_close: float
    gap_pct: float            # signed percentage, e.g. +6.42 or -3.10
    direction: str            # "up" or "down"
    volume: Optional[int] = None
    rel_volume: Optional[float] = None  # volume / avg_volume

    @property
    def abs_gap_pct(self) -> float:
        return abs(self.gap_pct)


@dataclass
class ScanResult:
    """The output of a pre-market scan: ranked gappers plus an optional briefing."""

    generated_at: datetime
    gappers: list[Gap]
    briefing: Optional[str] = None  # natural-language summary written by Claude
