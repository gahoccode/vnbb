"""vnstock-backed quote retrieval with normalization and error handling."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import ExitStack, contextmanager, redirect_stderr, redirect_stdout
from datetime import datetime
from importlib import import_module
from io import StringIO

import pandas as pd

from app.models.market_data import Candle


class QuoteFetchError(RuntimeError):
    """Raised when quote data cannot be fetched or normalized."""


class QuoteService:
    """Fetch and normalize OHLCV history records from vnstock."""

    def __init__(
        self,
        quote_factory: Callable[[str, str], object] | None = None,
    ) -> None:
        """Initialize the service with an injectable quote factory."""
        self._quote_factory = quote_factory or self._build_quote

    def fetch_history(
        self,
        *,
        symbol: str,
        source: str,
        start: str,
        end: str,
        interval: str,
    ) -> list[Candle]:
        """Return normalized candles sorted by timestamp ascending."""
        if source.upper() == "MSN":
            raise QuoteFetchError(
                "MSN is not supported for Vietnamese stock symbols in this TUI. "
                "Use VCI or KBS for stock candlestick charts."
            )

        try:
            with self._suppress_provider_output():
                quote_client = self._quote_factory(source, symbol)
                dataframe = quote_client.history(
                    symbol=symbol,
                    start=start,
                    end=end,
                    interval=interval,
                )
        except ModuleNotFoundError:
            raise
        except Exception as exc:  # pragma: no cover - exercised via tests with fake provider
            raise QuoteFetchError(str(exc)) from exc

        return self._normalize_history(dataframe)

    def _build_quote(self, source: str, symbol: str) -> object:
        """Create the vnstock quote client for a given source and symbol."""
        quote_class = import_module("vnstock").Quote
        return quote_class(source=source, symbol=symbol, show_log=False)

    @staticmethod
    @contextmanager
    def _suppress_provider_output():
        """Silence third-party provider banners and startup notices."""
        sink = StringIO()
        with ExitStack() as stack:
            stack.enter_context(redirect_stdout(sink))
            stack.enter_context(redirect_stderr(sink))
            yield

    def _normalize_history(self, dataframe: pd.DataFrame) -> list[Candle]:
        """Validate provider columns and convert rows into candle models."""
        required_columns = {"time", "open", "high", "low", "close", "volume"}
        if not required_columns.issubset(set(dataframe.columns)):
            raise QuoteFetchError(
                "Quote data is missing one or more required OHLCV columns."
            )

        normalized = dataframe.copy()
        normalized["time"] = pd.to_datetime(normalized["time"])
        normalized = normalized.sort_values("time")

        candles = [
            Candle(
                timestamp=self._to_datetime(row.time),
                open=float(row.open),
                high=float(row.high),
                low=float(row.low),
                close=float(row.close),
                volume=None if pd.isna(row.volume) else float(row.volume),
            )
            for row in normalized.itertuples(index=False)
        ]
        if not candles:
            raise QuoteFetchError("Quote data returned no rows.")
        return candles

    @staticmethod
    def _to_datetime(value: pd.Timestamp) -> datetime:
        """Convert pandas timestamps to native datetimes for renderer portability."""
        return value.to_pydatetime()
