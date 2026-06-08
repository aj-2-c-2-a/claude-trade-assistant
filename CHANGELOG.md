# Changelog

All notable changes are documented here, following Keep a Changelog and SemVer.

## [0.1.0] - 2026-06-08
### Added
- **Pre-market Scanner Pipeline**: watchlist -> data provider -> gap scan -> result.
- **Gap scanner & news briefing**: ranked gappers plus a Claude-written, neutral briefing.
- Pluggable data providers: `yfinance` (free, default) and `finnhub` (optional).
- Anthropic Claude integration (default model `claude-sonnet-4-6`).
- TradingView webhook receiver (FastAPI) with shared-secret auth.
- Pine Script alert-template generator (`cta pine`).
- `cta` CLI with rich tables (`scan`, `serve`, `pine`, `version`).
- Lightweight Charts demo dashboard.
- Unit tests for the gap math.
- One-command Windows installer.
