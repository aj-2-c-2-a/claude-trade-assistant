"""Default provider backed by `yfinance` — free and requires no API key.

Pre-market coverage from Yahoo is best-effort: it reports the latest available
price (which reflects pre/post-market for many US equities) plus the previous
regular-session close, which is exactly what the gap scanner needs.
"""
from __future__ import annotations

import logging

from ..models import Quote
from .base import DataProvider

log = logging.getLogger(__name__)


class YFinanceProvider(DataProvider):
    name = "yfinance"

    def __init__(self) -> None:
        try:
            import yfinance  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "yfinance is required for the default provider. Install with "
                "`pip install yfinance`."
            ) from exc

    def get_quotes(self, symbols: list[str], *, prepost: bool = True) -> list[Quote]:
        import yfinance as yf

        quotes: list[Quote] = []
        # Batch the symbols into a single Tickers object for fewer round-trips.
        tickers = yf.Tickers(" ".join(symbols))
        for sym in symbols:
            try:
                t = tickers.tickers.get(sym.upper())
                if t is None:
                    continue
                fi = t.fast_info
                last = float(fi.get("last_price") or fi.get("lastPrice") or 0.0)
                prev_close = float(fi.get("previous_close") or fi.get("previousClose") or 0.0)
                if last <= 0 or prev_close <= 0:
                    continue
                quotes.append(
                    Quote(
                        symbol=sym.upper(),
                        last=last,
                        prev_close=prev_close,
                        volume=_safe_int(fi.get("last_volume") or fi.get("lastVolume")),
                        avg_volume=_safe_int(fi.get("ten_day_average_volume")),
                        market_cap=_safe_float(fi.get("market_cap")),
                        session="pre" if prepost else "regular",
                    )
                )
            except Exception as exc:  # keep scanning even if one symbol fails
                log.debug("yfinance failed for %s: %s", sym, exc)
                continue
        return quotes


def _safe_int(value) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _safe_float(value) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
