"""Network-free tests for the gap math and ranking."""
import pytest

from claude_trade_assistant.models import Quote
from claude_trade_assistant.scanner.gap import compute_gap, scan_gaps


def q(symbol, last, prev_close, volume=None, avg_volume=None):
    return Quote(symbol=symbol, last=last, prev_close=prev_close, volume=volume, avg_volume=avg_volume)


def test_compute_gap_up():
    g = compute_gap(q("AAA", 110.0, 100.0))
    assert g.gap_pct == 10.0
    assert g.direction == "up"


def test_compute_gap_down():
    g = compute_gap(q("BBB", 95.0, 100.0))
    assert g.gap_pct == -5.0
    assert g.direction == "down"


def test_compute_gap_rel_volume():
    g = compute_gap(q("CCC", 120.0, 100.0, volume=3_000_000, avg_volume=1_000_000))
    assert g.rel_volume == 3.0


def test_compute_gap_rejects_zero_prev_close():
    with pytest.raises(ValueError):
        compute_gap(q("DDD", 10.0, 0.0))


def test_scan_filters_by_min_gap():
    quotes = [q("AAA", 102.0, 100.0), q("BBB", 108.0, 100.0), q("CCC", 120.0, 100.0)]
    gaps = scan_gaps(quotes, min_abs_gap_pct=5.0)
    symbols = [g.symbol for g in gaps]
    assert symbols == ["CCC", "BBB"]  # sorted by absolute size, AAA filtered out


def test_scan_direction_filter():
    quotes = [q("UP", 110.0, 100.0), q("DOWN", 90.0, 100.0)]
    assert [g.symbol for g in scan_gaps(quotes, min_abs_gap_pct=1.0, direction="up")] == ["UP"]
    assert [g.symbol for g in scan_gaps(quotes, min_abs_gap_pct=1.0, direction="down")] == ["DOWN"]


def test_scan_limit_and_rel_volume():
    quotes = [
        q("HOT", 130.0, 100.0, volume=5_000_000, avg_volume=1_000_000),
        q("MILD", 130.0, 100.0, volume=500_000, avg_volume=1_000_000),
    ]
    gaps = scan_gaps(quotes, min_abs_gap_pct=1.0, min_rel_volume=2.0, limit=5)
    assert [g.symbol for g in gaps] == ["HOT"]
