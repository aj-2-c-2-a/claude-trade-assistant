"""Configuration loading from a YAML file and environment variables.

Precedence: explicit kwargs > YAML file > environment > built-in defaults.
Secrets (API keys) are read from the environment, never from YAML.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    provider: str = "yfinance"
    model: str = "claude-sonnet-4-6"
    min_abs_gap_pct: float = 4.0
    min_rel_volume: float | None = None
    direction: str = "both"          # up | down | both
    limit: int = 25
    watchlist: list[str] = field(default_factory=list)
    webhook_secret: str | None = None  # shared token to authenticate TradingView alerts

    @classmethod
    def load(cls, path: str | os.PathLike | None = None) -> "Settings":
        data: dict = {}
        candidate = Path(path) if path else Path("config.yaml")
        if candidate.exists():
            try:
                import yaml

                data = yaml.safe_load(candidate.read_text()) or {}
            except ImportError:  # PyYAML optional; fall back to defaults
                data = {}

        s = cls(
            provider=os.getenv("CLA_PROVIDER", data.get("provider", cls.provider)),
            model=os.getenv("CLA_MODEL", data.get("model", cls.model)),
            min_abs_gap_pct=float(data.get("min_abs_gap_pct", cls.min_abs_gap_pct)),
            min_rel_volume=data.get("min_rel_volume", None),
            direction=data.get("direction", cls.direction),
            limit=int(data.get("limit", cls.limit)),
            watchlist=[str(x).upper() for x in (data.get("watchlist") or [])],
            webhook_secret=os.getenv("CLA_WEBHOOK_SECRET", data.get("webhook_secret")),
        )
        return s
