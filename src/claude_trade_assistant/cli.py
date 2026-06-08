"""Command-line interface for Claude Trade Assistant.

    cta scan                 Run the pre-market gap scan and print a table
    cta scan --briefing      Add a Claude-written news briefing
    cta serve                Start the TradingView webhook receiver
    cta pine                 Print a ready-to-paste Pine Script alert template
"""
from __future__ import annotations

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .config import Settings
from .models import ScanResult
from .scanner.premarket import PremarketScanner

app = typer.Typer(add_completion=False, help="Claude Trade Assistant — pre-market scanner & TradingView bridge.")
console = Console()

DEFAULT_WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "TSLA", "AMD", "AMZN", "META", "GOOGL",
    "NFLX", "INTC", "PLTR", "COIN", "SOFI", "BABA", "DIS", "BA",
]


def _resolve_watchlist(watchlist_file: Path | None, settings: Settings) -> list[str]:
    if watchlist_file:
        symbols = [
            line.strip().upper()
            for line in watchlist_file.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        return symbols
    if settings.watchlist:
        return settings.watchlist
    return DEFAULT_WATCHLIST


def _render(result: ScanResult) -> None:
    table = Table(title="Pre-market gappers", header_style="bold")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Symbol", style="bold cyan")
    table.add_column("Last", justify="right")
    table.add_column("Prev close", justify="right")
    table.add_column("Gap %", justify="right")
    table.add_column("Dir")
    table.add_column("Rel vol", justify="right")

    for i, g in enumerate(result.gappers, 1):
        color = "green" if g.direction == "up" else "red"
        arrow = "▲" if g.direction == "up" else "▼"
        rv = f"{g.rel_volume:.2f}x" if g.rel_volume is not None else "—"
        table.add_row(
            str(i), g.symbol, f"{g.last:.2f}", f"{g.prev_close:.2f}",
            f"[{color}]{g.gap_pct:+.2f}%[/{color}]", f"[{color}]{arrow}[/{color}]", rv,
        )

    if result.gappers:
        console.print(table)
    else:
        console.print("[yellow]No symbols passed the gap filters. Quiet pre-market.[/yellow]")

    if result.briefing:
        console.print(Panel(result.briefing, title="📰 News briefing", border_style="cyan"))

    console.print("[dim]Informational only. Not financial advice. See DISCLAIMER.md.[/dim]")


@app.command()
def scan(
    watchlist_file: Path = typer.Option(None, "--watchlist", "-w", help="File with one ticker per line."),
    config: Path = typer.Option(None, "--config", "-c", help="Path to config.yaml."),
    min_gap: float = typer.Option(None, "--min-gap", help="Minimum absolute gap %% to keep."),
    direction: str = typer.Option(None, "--direction", help="up | down | both."),
    limit: int = typer.Option(None, "--limit", help="Max rows to show."),
    briefing: bool = typer.Option(False, "--briefing", "-b", help="Add a Claude news briefing (needs ANTHROPIC_API_KEY)."),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose logging."),
):
    """Run the Pre-market Scanner Pipeline."""
    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING, format="%(message)s")
    settings = Settings.load(config)
    symbols = _resolve_watchlist(watchlist_file, settings)

    scanner = PremarketScanner(
        provider=settings.provider,
        min_abs_gap_pct=min_gap if min_gap is not None else settings.min_abs_gap_pct,
        min_rel_volume=settings.min_rel_volume,
        direction=direction or settings.direction,
        limit=limit or settings.limit,
    )
    with console.status("Scanning the pre-market…"):
        result = scanner.run(symbols, with_briefing=briefing)
    _render(result)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind host."),
    port: int = typer.Option(8000, help="Bind port."),
):
    """Start the TradingView webhook receiver."""
    try:
        import uvicorn
    except ImportError:
        console.print("[red]uvicorn is required: pip install 'claude-trade-assistant[web]'[/red]")
        raise typer.Exit(1)
    console.print(f"[cyan]TradingView webhook listening on http://{host}:{port}/tv-alert[/cyan]")
    uvicorn.run("claude_trade_assistant.webhook.server:app", host=host, port=port)


@app.command()
def pine(
    secret: str = typer.Option("YOUR_WEBHOOK_SECRET", help="Shared secret placeholder for the alert payload."),
):
    """Print a ready-to-paste Pine Script alert template for TradingView."""
    from .tradingview.pine import alert_pine_script

    console.print(Panel(alert_pine_script(secret), title="Pine Script — paste into TradingView", border_style="green"))


@app.command()
def version():
    """Print the version."""
    console.print(f"claude-trade-assistant {__version__}")


if __name__ == "__main__":
    app()
