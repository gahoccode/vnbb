"""questionary-backed prompt session for chart configuration."""

from __future__ import annotations

from importlib import import_module

from rich.console import Console

from app.models.market_data import ChartRequest, PromptAction


class PromptSession:
    """Collect user input and display prompt-level errors."""

    def __init__(self, console: Console, questionary_module: object | None = None) -> None:
        """Initialize the prompt session with injectable dependencies."""
        self._console = console
        self._questionary = questionary_module

    def collect_request(self) -> ChartRequest:
        """Prompt for the chart configuration."""
        questionary = self._questionary or import_module("questionary")
        symbol = str(questionary.text("Symbol", default="ACB").ask()).upper()
        source = str(
            questionary.select("Source", choices=["VCI", "KBS"], default="VCI").ask()
        ).upper()
        interval = str(
            questionary.select(
                "Interval",
                choices=["1D", "1W", "1M", "1H", "30m", "15m", "5m", "1m"],
                default="1D",
            ).ask()
        )
        start = str(questionary.text("Start date (YYYY-MM-DD)", default="2024-01-01").ask())
        end = str(questionary.text("End date (YYYY-MM-DD)", default="2024-12-31").ask())
        return ChartRequest(
            symbol=symbol,
            source=source,
            interval=interval,
            start=start,
            end=end,
            renderer="candlestick-chart",
        )

    def collect_next_action(self) -> PromptAction:
        """Prompt for the next loop action after a chart render."""
        questionary = self._questionary or import_module("questionary")
        action = str(
            questionary.select(
                "Next action",
                choices=[
                    PromptAction.RECONFIGURE.value,
                    PromptAction.QUIT.value,
                ],
                default=PromptAction.QUIT.value,
            ).ask()
        )
        return PromptAction(action)

    def show_error(self, message: str) -> None:
        """Display an error message in the console."""
        self._console.print(f"[red]{message}[/red]")

    def show_info(self, message: str) -> None:
        """Display an informational message in the console."""
        self._console.print(message)
