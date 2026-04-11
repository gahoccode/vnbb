"""Domain models for terminal chart rendering."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class Candle:
    """Normalized OHLCV record used by all chart renderers."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None

    def __post_init__(self) -> None:
        """Validate a candle price range after initialization."""
        if self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            raise ValueError("Candle high/low values must contain open and close prices.")
        if self.low > self.high:
            raise ValueError("Candle low value cannot be greater than the high value.")


@dataclass(frozen=True, slots=True)
class ChartRequest:
    """User-selected parameters for a chart request."""

    symbol: str
    source: str
    interval: str
    start: str
    end: str
    renderer: str


class PromptAction(StrEnum):
    """Actions available after a chart render completes."""

    RECONFIGURE = "reconfigure"
    QUIT = "quit"
