"""Application bootstrap helpers."""

from __future__ import annotations

from rich.console import Console

from app.controller import AppController
from app.renderers.candlestick_chart_renderer import PyCandlestickChartRenderer
from app.services.quote_service import QuoteService
from app.ui.layout import RichScreen
from app.ui.prompts import PromptSession


def build_application() -> AppController:
    """Construct the application controller with runtime dependencies."""
    console = Console()
    return AppController(
        prompt_session=PromptSession(console=console),
        quote_service=QuoteService(),
        renderers={
            "candlestick-chart": PyCandlestickChartRenderer(),
        },
        screen=RichScreen(console=console),
    )
