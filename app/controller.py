"""Main application controller for the chart exploration loop."""

from __future__ import annotations

from app.models.market_data import PromptAction
from app.services.quote_service import QuoteFetchError, QuoteService


class AppController:
    """Coordinate prompt input, market data fetching, and chart rendering."""

    def __init__(
        self,
        *,
        prompt_session: object,
        quote_service: QuoteService,
        renderers: dict[str, object],
        screen: object,
    ) -> None:
        """Initialize the controller with injected collaborators."""
        self._prompt_session = prompt_session
        self._quote_service = quote_service
        self._renderers = renderers
        self._screen = screen

    def run(self) -> None:
        """Run the prompt-fetch-render loop until the user quits."""
        try:
            request = self._prompt_session.collect_request()
        except ModuleNotFoundError as exc:
            self._show_missing_dependency_error(exc)
            return

        while True:
            try:
                candles = self._quote_service.fetch_history(
                    symbol=request.symbol,
                    source=request.source,
                    start=request.start,
                    end=request.end,
                    interval=request.interval,
                )
                renderer = self._renderers[request.renderer]
                width, height = self._screen.terminal_size()
                chart_text = renderer.render(
                    candles,
                    width=max(width - 4, 20),
                    height=max(height - 12, 10),
                    title=f"{request.symbol} {request.interval}",
                )
                self._screen.show_chart(chart_text, request, candles)
            except QuoteFetchError as exc:
                self._prompt_session.show_error(
                    "Warning: unable to fetch vnstock data. "
                    "Check your network connection or provider settings and try again.\n"
                    f"Details: {exc}"
                )
                return
            except ModuleNotFoundError as exc:
                self._show_missing_dependency_error(exc)
                return

            try:
                action = self._prompt_session.collect_next_action()
            except ModuleNotFoundError as exc:
                self._show_missing_dependency_error(exc)
                return
            if action is PromptAction.QUIT:
                return
            if action is PromptAction.RECONFIGURE:
                try:
                    request = self._prompt_session.collect_request()
                except ModuleNotFoundError as exc:
                    self._show_missing_dependency_error(exc)
                    return

    def _show_missing_dependency_error(self, exc: ModuleNotFoundError) -> None:
        """Display a consistent missing-dependency message."""
        dependency_name = exc.name or str(exc).split("'")[1]
        self._prompt_session.show_error(
            "Warning: a required runtime dependency is missing. "
            f"Install project dependencies before starting the TUI.\nDetails: {dependency_name}"
        )
