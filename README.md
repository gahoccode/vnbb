# vnbb

vnbb giúp xem candlestick chứng khoán Việt Nam ngay trong terminal: `vnstock`

![vnstock](https://img.shields.io/badge/vnstock-3.x-green)

## vnbb dành cho ai? / Who is this for?

- Nhà đầu tư cá nhân muốn xem nhanh chart nến của mã Việt Nam mà không cần mở web
- Analyst cần kiểm tra dữ liệu `vnstock` theo symbol, source, interval, start date, end date trước khi đưa vào pipeline phân tích kỹ thuật.

## vnbb làm gì? / What does it do?

- Nhận symbol như `ACB`, `FPT`, `VCB`, chọn nguồn dữ liệu `VCI` hoặc `KBS`, interval, và khoảng ngày.
- Gọi `vnstock.Quote.history()` qua `QuoteService`, rồi chuẩn hóa OHLCV thành các `Candle` typed models.
- Render candlestick chart ngay trong terminal bằng `candlestick-chart`, wrap trong Rich layout.
- Hiển thị warning rõ ràng khi thiếu dependency, mất mạng, provider lỗi, hoặc nguồn dữ liệu không phù hợp.
- Giữ route entrypoint mỏng: `main.py` chỉ bootstrap controller, business logic nằm trong service/renderer layer.

## Demo

<!-- TODO: Add GIF showing: uv run python main.py -> select ACB/VCI/1D -> terminal candlestick chart -> reconfigure or quit -->

## Cài đặt / Installation

Yêu cầu Python `>=3.13`. Dự án dùng `uv`, và có `uv.lock` để đồng bộ môi trường.

```bash
git clone https://github.com/gahoccode/vnbb.git
cd vnbb
uv sync
```

## Quick Start

Chạy TUI:

```bash
uv run python main.py
```

Prompt mặc định:

```text
Symbol: ACB
Source: VCI
Interval: 1D
Start date: 2024-01-01
End date: 2024-12-31
```

Kết quả mong đợi:

```text
ACB 1D
<terminal candlestick chart rendered in a Rich panel>
Next action: reconfigure / quit
```

X-axis hiển thị khoảng thời gian lịch sử bạn chọn trong prompt. Chỉ các bản ghi do `vnstock` trả về cho đúng `symbol`, `source`, `interval`, `start`, và `end` đó được visualized.

Kiểm tra service trực tiếp trong test hoặc script nhỏ:

```python
from app.services.quote_service import QuoteService

service = QuoteService()
candles = service.fetch_history(
    symbol="ACB",
    source="VCI",
    start="2024-01-01",
    end="2024-01-31",
    interval="1D",
)
print(candles[0])
```

## Cấu hình / Configuration

Hiện tại `vnbb` cấu hình qua prompt, chưa có CLI flags hoặc config file.

| Prompt       |      Default | Ý nghĩa                                                           |
| ------------ | -----------: | ----------------------------------------------------------------- |
| `Symbol`     |        `ACB` | Mã chứng khoán Việt Nam                                           |
| `Source`     |        `VCI` | Nguồn dữ liệu `vnstock`, chọn `VCI` hoặc `KBS`                    |
| `Interval`   |         `1D` | Khung thời gian: `1D`, `1W`, `1M`, `1H`, `30m`, `15m`, `5m`, `1m` |
| `Start date` | `2024-01-01` | Ngày bắt đầu theo `YYYY-MM-DD`                                    |
| `End date`   | `2024-12-31` | Ngày kết thúc theo `YYYY-MM-DD`                                   |

                    |

## Documentation Links

- vnstock GitHub: https://github.com/thinh-vu/vnstock
- vnstock terms of use: https://vnstocks.com/docs/tai-lieu/dieu-khoan-su-dung
- Rich docs: https://context7.com/textualize/rich/llms.txt
- Questionary docs: https://questionary.readthedocs.io/en/stable/
- Python Candlestick Chart repo: https://github.com/BoboTiG/py-candlestick-chart
- candlestick-chart PyPI: https://pypi.org/project/candlestick-chart/

## Acknowledgements

Dự án sử dụng [vnstock](https://github.com/thinh-vu/vnstock) để tải dữ liệu chứng khoán Việt Nam.
Vui lòng tuân thủ [điều khoản sử dụng](https://vnstocks.com/docs/tai-lieu/dieu-khoan-su-dung) của vnstock khi sử dụng dữ liệu.

## Disclaimer

vnbb chỉ phục vụ mục đích nghiên cứu và học tập cá nhân, không phải lời khuyên đầu tư.
Dữ liệu từ vnstock phụ thuộc nguồn công khai và có thể không chính xác hoặc không đầy đủ.
