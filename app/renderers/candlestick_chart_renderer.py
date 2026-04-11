"""py-candlestick-chart adapter."""

from __future__ import annotations

from contextlib import redirect_stdout
from importlib import import_module
from io import StringIO

from app.models.market_data import Candle


class PyCandlestickChartRenderer:
    """Render candle data using the candlestick-chart package."""

    def __init__(self, chart_module: object | None = None) -> None:
        """Initialize the renderer with an optional injected chart module."""
        self._chart_module = chart_module

    def render(self, candles: list[Candle], width: int, height: int, title: str) -> str:
        """Build a terminal chart string from normalized candle data."""
        module = self._chart_module or import_module("candlestick_chart")
        chart_candles = [
            module.Candle(
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                timestamp=candle.timestamp.timestamp(),
            )
            for candle in candles
        ]
        chart = module.Chart(chart_candles, title=title, width=width, height=height)
        if hasattr(chart, "set_volume_pane_enabled"):
            chart.set_volume_pane_enabled(True)
        sink = StringIO()
        with redirect_stdout(sink):
            rendered = chart.draw()
        if isinstance(rendered, str):
            return rendered
        return sink.getvalue().strip()
