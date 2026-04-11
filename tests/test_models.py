from datetime import datetime

import pytest

from app.models.market_data import Candle


def test_candle_rejects_invalid_price_range() -> None:
    with pytest.raises(ValueError):
        Candle(
            timestamp=datetime(2024, 1, 1),
            open=10.0,
            high=9.0,
            low=8.0,
            close=8.5,
            volume=100.0,
        )


def test_candle_allows_missing_volume() -> None:
    candle = Candle(
        timestamp=datetime(2024, 1, 1),
        open=10.0,
        high=12.0,
        low=9.0,
        close=11.0,
        volume=None,
    )

    assert candle.volume is None
