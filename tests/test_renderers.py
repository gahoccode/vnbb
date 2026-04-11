from datetime import datetime
from types import SimpleNamespace

from app.models.market_data import Candle
from app.renderers.candlestick_chart_renderer import PyCandlestickChartRenderer


def build_candles() -> list[Candle]:
    return [
        Candle(
            timestamp=datetime(2024, 1, 1),
            open=10.0,
            high=12.0,
            low=9.0,
            close=11.0,
            volume=100.0,
        ),
        Candle(
            timestamp=datetime(2024, 1, 2),
            open=11.0,
            high=13.0,
            low=10.0,
            close=12.0,
            volume=150.0,
        ),
    ]


class FakeChart:
    def __init__(self, candles: list[object], title: str, width: int, height: int) -> None:
        self.candles = candles
        self.title = title
        self.width = width
        self.height = height
        self.draw_called = False

    def set_volume_pane_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def draw(self) -> str:
        self.draw_called = True
        return "candlestick-chart"


def test_py_candlestick_renderer_adapts_candle_objects() -> None:
    fake_module = SimpleNamespace(Candle=SimpleNamespace, Chart=FakeChart)
    renderer = PyCandlestickChartRenderer(chart_module=fake_module)

    chart = renderer.render(build_candles(), width=100, height=24, title="ACB 1D")

    assert chart == "candlestick-chart"


class FakeStdoutChart(FakeChart):
    def draw(self) -> None:
        self.draw_called = True
        print("stdout-chart")
        return None


def test_py_candlestick_renderer_captures_chart_stdout() -> None:
    fake_module = SimpleNamespace(Candle=SimpleNamespace, Chart=FakeStdoutChart)
    renderer = PyCandlestickChartRenderer(chart_module=fake_module)

    chart = renderer.render(build_candles(), width=100, height=24, title="ACB 1D")

    assert chart == "stdout-chart"
