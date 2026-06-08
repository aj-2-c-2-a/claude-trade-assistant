"""Optional provider backed by Finnhub (https://finnhub.io).

Finnhub's free tier returns a clean quote with current price (`c`) and previous
close (`pc`), which maps directly onto the gap calculation. Set FINNHUB_API_KEY.
"""
from __future__ import annotations

import logging
import os

from ..models import Quote
from .base import DataProvider

log = logging.getLogger(__name__)

_BASE = "https://finnhub.io/api/v1"


class FinnhubProvider(DataProvider):
    name = "finnhub"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "FinnhubProvider needs an API key. Set FINNHUB_API_KEY or pass api_key=..."
            )
        try:
            import httpx  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            raise ImportError("httpx is required for the Finnhub provider (`pip install httpx`).") from exc

    def get_quotes(self, symbols: list[str], *, prepost: bool = True) -> list[Quote]:
        import httpx

        quotes: list[Quote] = []
        with httpx.Client(timeout=10.0) as client:
            for sym in symbols:
                try:
                    resp = client.get(
                        f"{_BASE}/quote",
                        params={"symbol": sym.upper(), "token": self.api_key},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    last = float(data.get("c") or 0.0)
                    prev_close = float(data.get("pc") or 0.0)
                    if last <= 0 or prev_close <= 0:
                        continue
                    quotes.append(
                        Quote(
                            symbol=sym.upper(),
                            last=last,
                            prev_close=prev_close,
                            session="pre" if prepost else "regular",
                        )
                    )
                except Exception as exc:
                    log.debug("finnhub failed for %s: %s", sym, exc)
                    continue
        return quotes
