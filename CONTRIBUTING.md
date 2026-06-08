# Contributing

Thanks for helping improve Claude Trade Assistant! 🦅

## Setup
```bash
git clone https://github.com/aj-2-c-2-a/claude-trade-assistant.git
cd claude-trade-assistant
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[web,dev]"
pytest -q
```

## Guidelines
- Keep the project **analysis-only**: do not add broker order execution or anything
  that turns it into financial advice. See [DISCLAIMER.md](./DISCLAIMER.md).
- Add tests for new logic (the gap math is fully unit-tested — keep it that way).
- Run `ruff check .` and `pytest` before opening a PR.

## Good first issues
- New data provider (Polygon, Alpha Vantage, Tiingo).
- Sector/ETF watchlist presets.
- Persist scan results to JSON for the dashboard.
- More Pine Script alert templates.
