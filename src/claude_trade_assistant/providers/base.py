"""Pluggable market-data providers.

TradingView itself does not expose a public market-data API — it generates
*alerts* that are delivered via webhooks. So for scanning we read quotes from a
separate data source. Providers normalize their responses into :class:`Quote`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Quote


class DataProvider(ABC):
    """Interface every data provider must implement."""

    name: str = "base"

    @abstractmethod
    def get_quotes(self, symbols: list[str], *, prepost: bool = True) -> list[Quote]:
        """Return a normalized quote for each symbol that can be priced.

        Args:
            symbols: ticker symbols (e.g. ["AAPL", "TSLA"]).
            prepost: include pre/post-market pricing when the source supports it.

        Symbols that cannot be priced should simply be omitted from the result.
        """
        raise NotImplementedError


def get_provider(name: str, **kwargs) -> DataProvider:
    """Factory: resolve a provider by name.

    Supported: "yfinance" (default, free, no key), "finnhub" (needs FINNHUB_API_KEY).
    """
    name = (name or "yfinance").lower()
    if name == "yfinance":
        from .yfinance_provider import YFinanceProvider
        return YFinanceProvider(**kwargs)
    if name == "finnhub":
        from .finnhub_provider import FinnhubProvider
        return FinnhubProvider(**kwargs)
    raise ValueError(f"Unknown data provider: {name!r}. Use 'yfinance' or 'finnhub'.")
