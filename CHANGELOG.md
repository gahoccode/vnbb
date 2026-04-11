# Changelog

## Unreleased

### Added

- Terminal candlestick explorer built with `rich`, `questionary`, `plotext`, and `candlestick-chart`
- Typed market-data models and a `vnstock.Quote` normalization service
- Tests for controller flow, service normalization, renderer adapters, and warning behavior
- Project packaging metadata, lockfile generation, and exported `requirements.txt`

### Changed

- Replaced the placeholder CLI with a controller-driven TUI bootstrap
- Added explicit warning messages for upstream data failures and missing runtime dependencies
- Removed `plotext` from the candlestick rendering path and standardized on `candlestick-chart`

### Scope Of Impact

- Affected files:
  `main.py`, `pyproject.toml`, `requirements.txt`, `uv.lock`, `README.md`, `llms.txt`, `app/`, `tests/`
- Impacted functions by file:
  `main.py`: `main()`
  `app/bootstrap.py`: `build_application()`
  `app/controller.py`: `AppController.run()`
  `app/services/quote_service.py`: `QuoteService.fetch_history()`, `QuoteService._build_quote()`, `QuoteService._normalize_history()`, `QuoteService._to_datetime()`
  `app/renderers/candlestick_chart_renderer.py`: `PyCandlestickChartRenderer.render()`
  `app/ui/prompts.py`: `PromptSession.collect_request()`, `PromptSession.collect_next_action()`, `PromptSession.show_error()`, `PromptSession.show_info()`
  `app/ui/layout.py`: `RichScreen.terminal_size()`, `RichScreen.show_chart()`
  `app/models/market_data.py`: `Candle.__post_init__()`
