# Security Policy

## Keys and secrets
- API keys (`ANTHROPIC_API_KEY`, `FINNHUB_API_KEY`) are read from the environment
  or a local `.env` file that is **git-ignored**. Never commit real keys.
- The TradingView webhook is authenticated with a shared secret (`CLA_WEBHOOK_SECRET`).
  Use a long random value and serve the endpoint over HTTPS (e.g. behind a reverse
  proxy or tunnel). Requests with a wrong/missing secret are rejected with HTTP 401.

## No trade execution
By design, this project does not connect to brokers and cannot place orders. This
limits blast radius: a compromised webhook cannot move money.

## Reporting a vulnerability
Please open a private [security advisory](https://github.com/aj-2-c-2-a/claude-trade-assistant/security/advisories/new)
rather than a public issue. We aim to respond within 72 hours.
