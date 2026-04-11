from datetime import datetime

from rich.console import Console

from app.models.market_data import Candle, ChartRequest
from app.ui.layout import RichScreen


def test_rich_screen_decodes_ansi_chart_output() -> None:
    console = Console(record=True, width=120)
    screen = RichScreen(console=console)
    request = ChartRequest(
        symbol="ACB",
        source="KBS",
        interval="1D",
        start="2024-01-01",
        end="2024-01-10",
        renderer="candlestick-chart",
    )
    candles = [
        Candle(
            timestamp=datetime(2024, 1, 2),
            open=16.81,
            high=17.38,
            low=16.81,
            close=17.16,
            volume=13883500.0,
        )
    ]

    screen.show_chart("\x1b[31mANSI chart\x1b[0m", request, candles)

    rendered = console.export_text()
    assert "ANSI chart" in rendered
    assert "\x1b[31m" not in rendered
