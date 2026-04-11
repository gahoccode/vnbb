from datetime import datetime

from app.controller import AppController
from app.models.market_data import Candle, ChartRequest, PromptAction
from app.services.quote_service import QuoteFetchError


class FakePromptSession:
    def __init__(
        self,
        request: ChartRequest | None,
        action: PromptAction | None,
        request_error: Exception | None = None,
        action_error: Exception | None = None,
    ) -> None:
        self.request = request
        self.action = action
        self.request_error = request_error
        self.action_error = action_error
        self.error_messages: list[str] = []
        self.info_messages: list[str] = []

    def collect_request(self) -> ChartRequest:
        if self.request_error is not None:
            raise self.request_error
        assert self.request is not None
        return self.request

    def collect_next_action(self) -> PromptAction:
        if self.action_error is not None:
            raise self.action_error
        assert self.action is not None
        return self.action

    def show_error(self, message: str) -> None:
        self.error_messages.append(message)

    def show_info(self, message: str) -> None:
        self.info_messages.append(message)


class FakeQuoteService:
    def __init__(self, candles: list[Candle] | None = None, error: Exception | None = None) -> None:
        self.candles = candles or []
        self.error = error

    def fetch_history(self, **_: str) -> list[Candle]:
        if self.error is not None:
            raise self.error
        return self.candles


class FakeRenderer:
    def __init__(self, output: str) -> None:
        self.output = output
        self.calls: list[tuple[int, int, str]] = []

    def render(self, candles: list[Candle], width: int, height: int, title: str) -> str:
        self.calls.append((width, height, title))
        return self.output


class FakeScreen:
    def __init__(self) -> None:
        self.chart_outputs: list[str] = []

    def terminal_size(self) -> tuple[int, int]:
        return (120, 40)

    def show_chart(self, chart_text: str, request: ChartRequest, candles: list[Candle]) -> None:
        self.chart_outputs.append(chart_text)


def build_request(renderer: str = "candlestick-chart") -> ChartRequest:
    return ChartRequest(
        symbol="ACB",
        source="VCI",
        interval="1D",
        start="2024-01-01",
        end="2024-01-10",
        renderer=renderer,
    )


def build_candles() -> list[Candle]:
    return [
        Candle(
            timestamp=datetime(2024, 1, 1),
            open=10.0,
            high=12.0,
            low=9.0,
            close=11.0,
            volume=100.0,
        )
    ]


def test_controller_fetches_and_renders_chart() -> None:
    prompt = FakePromptSession(request=build_request(), action=PromptAction.QUIT)
    renderer = FakeRenderer(output="chart")
    screen = FakeScreen()
    controller = AppController(
        prompt_session=prompt,
        quote_service=FakeQuoteService(candles=build_candles()),
        renderers={"candlestick-chart": renderer},
        screen=screen,
    )

    controller.run()

    assert renderer.calls == [(116, 28, "ACB 1D")]
    assert screen.chart_outputs == ["chart"]


def test_controller_shows_error_and_exits_on_fetch_failure() -> None:
    prompt = FakePromptSession(request=build_request(), action=PromptAction.QUIT)
    controller = AppController(
        prompt_session=prompt,
        quote_service=FakeQuoteService(error=QuoteFetchError("network down")),
        renderers={"candlestick-chart": FakeRenderer(output="chart")},
        screen=FakeScreen(),
    )

    controller.run()

    assert prompt.error_messages == [
        "Warning: unable to fetch vnstock data. "
        "Check your network connection or provider settings and try again.\n"
        "Details: network down"
    ]


def test_controller_shows_dependency_error_before_first_prompt() -> None:
    prompt = FakePromptSession(
        request=None,
        action=None,
        request_error=ModuleNotFoundError("No module named 'questionary'"),
    )
    controller = AppController(
        prompt_session=prompt,
        quote_service=FakeQuoteService(candles=build_candles()),
        renderers={"candlestick-chart": FakeRenderer(output="chart")},
        screen=FakeScreen(),
    )

    controller.run()

    assert prompt.error_messages == [
        "Warning: a required runtime dependency is missing. "
        "Install project dependencies before starting the TUI.\nDetails: questionary"
    ]
