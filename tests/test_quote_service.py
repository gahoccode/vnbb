from datetime import datetime

import pandas as pd
import pytest

from app.services.quote_service import QuoteFetchError, QuoteService


class FakeQuoteClient:
    def __init__(
        self,
        dataframe: pd.DataFrame | None = None,
        error: Exception | None = None,
    ) -> None:
        self.dataframe = dataframe
        self.error = error
        self.calls: list[dict[str, str]] = []

    def history(
        self,
        *,
        symbol: str,
        start: str,
        end: str,
        interval: str,
    ) -> pd.DataFrame:
        self.calls.append(
            {
                "symbol": symbol,
                "start": start,
                "end": end,
                "interval": interval,
            }
        )
        if self.error is not None:
            raise self.error
        assert self.dataframe is not None
        return self.dataframe


def test_fetch_history_normalizes_ohlcv_rows() -> None:
    created_with: list[tuple[str, str]] = []
    client = FakeQuoteClient(
        dataframe=pd.DataFrame(
            [
                {
                    "time": "2024-01-02",
                    "open": 10,
                    "high": 12,
                    "low": 9,
                    "close": 11,
                    "volume": 1000,
                },
                {
                    "time": "2024-01-01",
                    "open": 9,
                    "high": 11,
                    "low": 8,
                    "close": 10,
                    "volume": 900,
                },
            ]
        )
    )
    service = QuoteService(
        quote_factory=lambda source, symbol: created_with.append((source, symbol)) or client
    )

    candles = service.fetch_history(
        symbol="ACB",
        source="VCI",
        start="2024-01-01",
        end="2024-01-02",
        interval="1D",
    )

    assert [candle.timestamp for candle in candles] == [
        datetime(2024, 1, 1),
        datetime(2024, 1, 2),
    ]
    assert candles[0].close == 10.0
    assert client.calls == [
        {
            "symbol": "ACB",
            "start": "2024-01-01",
            "end": "2024-01-02",
            "interval": "1D",
        }
    ]
    assert created_with == [("VCI", "ACB")]


def test_fetch_history_raises_quote_fetch_error_on_missing_columns() -> None:
    client = FakeQuoteClient(
        dataframe=pd.DataFrame(
            [
                {
                    "time": "2024-01-01",
                    "open": 1,
                    "high": 2,
                    "low": 0.5,
                    "close": 1.5,
                }
            ]
        )
    )
    service = QuoteService(quote_factory=lambda source, symbol: client)

    with pytest.raises(QuoteFetchError):
        service.fetch_history(
            symbol="ACB",
            source="VCI",
            start="2024-01-01",
            end="2024-01-02",
            interval="1D",
        )


def test_fetch_history_wraps_provider_errors() -> None:
    service = QuoteService(
        quote_factory=lambda source, symbol: FakeQuoteClient(error=RuntimeError("dns failed"))
    )

    with pytest.raises(QuoteFetchError, match="dns failed"):
        service.fetch_history(
            symbol="ACB",
            source="VCI",
            start="2024-01-01",
            end="2024-01-02",
            interval="1D",
        )


def test_fetch_history_preserves_module_not_found_errors() -> None:
    service = QuoteService(
        quote_factory=lambda source, symbol: (_ for _ in ()).throw(
            ModuleNotFoundError("No module named 'vnstock'")
        )
    )

    with pytest.raises(ModuleNotFoundError, match="vnstock"):
        service.fetch_history(
            symbol="ACB",
            source="VCI",
            start="2024-01-01",
            end="2024-01-02",
            interval="1D",
        )


def test_fetch_history_rejects_msn_for_stock_symbols() -> None:
    service = QuoteService(quote_factory=lambda source, symbol: FakeQuoteClient())

    with pytest.raises(QuoteFetchError, match="MSN is not supported"):
        service.fetch_history(
            symbol="ACB",
            source="MSN",
            start="2024-01-01",
            end="2024-01-02",
            interval="1D",
        )
