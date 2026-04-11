"""Rich screen abstraction for chart display and status rendering."""

from __future__ import annotations

from rich.ansi import AnsiDecoder
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

from app.models.market_data import Candle, ChartRequest


class RichScreen:
    """Render charts and metadata using Rich panels."""

    def __init__(self, console: Console) -> None:
        """Initialize the screen with a Rich console."""
        self._console = console
        self._ansi_decoder = AnsiDecoder()

    def terminal_size(self) -> tuple[int, int]:
        """Return the current terminal width and height."""
        size = self._console.size
        return size.width, size.height

    def show_chart(self, chart_text: str, request: ChartRequest, candles: list[Candle]) -> None:
        """Render the chart panel with associated request metadata."""
        summary = Table.grid(expand=True)
        summary.add_column()
        summary.add_column()
        summary.add_row("Symbol", request.symbol)
        summary.add_row("Source", request.source)
        summary.add_row("Interval", request.interval)
        summary.add_row("Window", f"{request.start} to {request.end}")
        summary.add_row("X-axis", f"Displays {len(candles)} most recent records in range")
        summary.add_row("Chart", "Candlestick chart shows the selected historical range")

        group = Group(
            Panel(summary, title="Request", border_style="cyan"),
            Panel(
                Group(*self._ansi_decoder.decode(chart_text)),
                title="Candlestick Chart",
                border_style="green",
            ),
        )
        self._console.print(group)
