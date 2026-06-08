"""Pre-market Scanner Pipeline.

End-to-end orchestration that runs before the US open:

    watchlist -> data provider -> gap scan -> (optional) Claude news briefing

The pipeline is deliberately provider-agnostic and side-effect free: it returns
a :class:`ScanResult` you can print, serve to the dashboard, or persist.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from ..models import ScanResult
from ..providers.base import DataProvider, get_provider
from .gap import scan_gaps

log = logging.getLogger(__name__)


class PremarketScanner:
    def __init__(
        self,
        provider: DataProvider | str = "yfinance",
        *,
        min_abs_gap_pct: float = 4.0,
        min_rel_volume: float | None = None,
        direction: str = "both",
        limit: int | None = 25,
    ) -> None:
        self.provider = provider if isinstance(provider, DataProvider) else get_provider(provider)
        self.min_abs_gap_pct = min_abs_gap_pct
        self.min_rel_volume = min_rel_volume
        self.direction = direction
        self.limit = limit

    def run(self, watchlist: list[str], *, with_briefing: bool = False) -> ScanResult:
        """Run the full pipeline over a watchlist of symbols."""
        log.info("Scanning %d symbols via %s ...", len(watchlist), self.provider.name)
        quotes = self.provider.get_quotes(watchlist, prepost=True)
        log.info("Priced %d / %d symbols.", len(quotes), len(watchlist))

        gappers = scan_gaps(
            quotes,
            min_abs_gap_pct=self.min_abs_gap_pct,
            min_rel_volume=self.min_rel_volume,
            direction=self.direction,
            limit=self.limit,
        )
        log.info("Found %d gappers above %.1f%%.", len(gappers), self.min_abs_gap_pct)

        result = ScanResult(generated_at=datetime.now(timezone.utc), gappers=gappers)

        if with_briefing:
            # Imported lazily so a scan without a briefing needs no API key.
            from ..news.briefing import write_briefing

            try:
                result.briefing = write_briefing(gappers)
            except Exception as exc:
                log.warning("Briefing skipped: %s", exc)
                result.briefing = None

        return result
