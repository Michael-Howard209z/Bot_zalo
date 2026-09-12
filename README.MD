# FUCK ZALO

Bot Zalo tích hợp nhiều tính năng quản lý nhóm và tiện ích, xây dựng trên thư viện `zlapi`.

> Phiên bản này đã được sửa lỗi **crash mất kết nối WebSocket** (chi tiết ở mục [Báo cáo thay đổi](#-bao-cao-thay-doi)).

---

## Cài đặt

### Bước 1: Chuẩn bị môi trường

Yêu cầu Python 3.8 trở lên. Nên dùng virtual environment:

```bash
# Tạo môi trường ảo (Windows)
python -m venv venv

# Kích hoạt
.\venv\Scripts\activate
```

### Bước 2: Cài thư viện

```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình

Tạo file `config.py` trong thư mục gốc (dự án đã có sẵn) và điền thông tin tài khoản:

```python
# config.py

# Thông tin xác thực Zalo
IMEI = "YOUR_IMEI_HERE"
SESSION_COOKIES = "YOUR_SESSION_COOKIES_HERE"

# API Keys (nếu dùng dịch vụ ngoài)
API_KEY = ""
SECRET_KEY = ""

# Cấu hình bot
PREFIX = "..."        # Ký tự bắt đầu lệnh (vd: ...help, ...menu)
ADMIN = "YOUR_ADMIN_ID"  # ID admin của bot
```

Cookie/Zalo của bạn sẽ hết hạn sau một thời gian (thường vài ngày tới vài tuần). Khi bot không đăng nhập được nữa, hãy lấy lại Cookie mới từ trình duyệt (đăng nhập [chat.zalo.me](https://chat.zalo.me)).

### Bước 4: Chạy bot

```bash
python main.py
```

---

## Tiện ích mở rộng Zalo

Để lấy **IMEI** và **Cookie** dễ dàng hơn, dùng extension kèm theo dự án:

[**Hướng dẫn cài extension Zalo cookie (Material 3)**](./zlapi-extension-obfuscated/README.md)

---

## Danh sách lệnh cơ bản

- `...menu` — xem danh sách lệnh
- `...help` — trợ giúp
- Các lệnh quản lý nhóm khác được load động từ thư mục `modules/`

---

## Hướng dẫn lấy Cookie (khi hết hạn)

1. Mở trình duyệt (Chrome/Edge/Firefox), đăng nhập vào [chat.zalo.me](https://chat.zalo.me).
2. Mở DevTools (F12) -> tab **Application/Storage** -> **Cookies**.
3. Sao chép toàn bộ Cookie của trang `chat.zalo.me` vào `config.py`.
4. Khởi động lại bot.

> Quan trọng: Với cùng một tài khoản Zalo, chỉ được chạy **một** kết nối bot tại một thời điểm. Nếu bot đang chạy ở máy khác / cửa sổ khác, kết nối cũ sẽ bị Zalo đóng (kèm log `Another connection is opened, closing this one`).

---

## Lưu ý quan trọng

- Bot chạy trên tài khoản Zalo cá nhân; sử dụng cẩn thận để tránh bị khóa tài khoản do spam.
- Không chia sẻ `config.py`, Cookie hoặc IMEI cho người khác.

---
---

# BÁO CÁO THAY ĐỔI

Báo cáo ghi lại **nguyên nhân sự cố**, **quá trình chẩn đoán** và **các sửa đổi** đã thực hiện ở phiên bản này.

## 1. Sự cố gốc

Bot crash ngay khi khởi động/khởi động lại với lỗi:

```
websockets.exceptions.ConnectionClosedError: no close frame received or sent
```

Lỗi xảy ra tại lần kết nối WebSocket đầu tiên tới server Zalo (`zlapi/_client.py` -> `_listen_ws`), **ngoài** khối `try/except` nên bot thoát chương trình — không tự hồi phục.

## 2. Quá trình chẩn đoán

Đã viết script test trực tiếp (không đụng tới bot) và thu được các kết quả:

| Kiểm tra | Kết quả |
|---|---|
| `getLoginInfo` (kiểm tra Cookie) | OK — `error_code: 0`, Cookie còn hạn |
| TCP + TLS tới `wsX-msg.chat.zalo.me:443` | OK — TLS 1.3 bình thường |
| WebSocket handshake với bộ header cũ của zlapi | Thất bại — server trả `HTTP/1.1 501 Not Implemented` hoặc đóng kết nối ngay |
| WebSocket handshake với header tối giản + host hợp lệ | Thành công — `101 Switching Protocols`, nhận được frame `key` để mã hóa |

Kết luận nguyên nhân:

1. **Header handshake sai/trùng**: `zlapi` gửi kèm `Host`, `Connection`, `Upgrade`, `Sec-Websocket-Version` (sai hoa thường) và `Sec-Websocket-Extensions` (không đúng chuẩn) trong `additional_headers`. Các thư viện `websockets` hiện đại (bản 13+) **tự sinh** các header này → gửi trùng, khiến server `zlpws` của Zalo trả `501 Not Implemented`. `websockets` quy lỗi dạng này thành `ConnectionClosedError: no close frame received or sent`.
2. **Chỉ dùng 1 server duy nhất**: code cũ nối tới `zpw_ws[0]` — nhưng Zalo luân phiên ~7 server. Một số node ở trạng thái "black-hole" (nhận TCP+TLS rồi im lặng không đọc dữ liệu) khiến `connect()` **block vô hạn** (websockets không đặt socket timeout trong giai đoạn gửi handshake) hoặc kết thúc bằng `ConnectionClosedError`.
3. **File `main.py` thụ động với lỗi**: chỉ bắt `KeyboardInterrupt`, không bắt lỗi kết nối.

## 3. Các file đã sửa

### 3.1. `zlapi/_client.py` — hàm `_listen_ws`

- **Loại bỏ các header trùng/lỗi** trong handshake. Chỉ giữ: `Accept-Encoding`, `Accept-Language`, `Cache-Control`, `Origin`, `User-Agent`, `Cookie`. `Host`, `Connection`, `Upgrade`, `Sec-WebSocket-Version`, `Sec-WebSocket-Extensions` được để `websockets` tự tạo (đúng chuẩn, đúng cỡ chữ).
- **Thử lần lượt tất cả server** trong `zpw_ws` thay vì chỉ `zpw_ws[0]`.
- **Kiểm tra sẵn (pre-flight)** từng host: mở TCP + TLS với timeout 8s. Host nào không kết nối được sẽ bị bỏ qua ngay.
- **Tự tạo socket đã bọc TLS có timeout** rồi truyền cho `websockets` qua tham số `sock=`, dùng scheme `ws://` (để `websockets` không bọc TLS lần hai): loại bỏ hoàn toàn tình trạng treo vô hạn khi server "black-hole" (block ở hàm `sendall`).
- Bổ sung `open_timeout=10`, `close_timeout=3`, `proxy=False` cho lệnh `connect()`.
- Thêm import `socket` và `ssl`.

### 3.2. `main.py`

- **Tự động kết nối lại** khi mất kết nối: `client.listen()` được bọc trong vòng lặp, bắt toàn bộ ngoại lệ (trừ `KeyboardInterrupt`), in thông báo và chờ 5 giây rồi thử lại — bot không còn thoát chương trình khi lỗi mạng/server.
- **Chống crash do bảng mã console**: `sys.stdout`/`sys.stderr` được `reconfigure(errors="replace")` ngay khi khởi động. Trước đây, các dòng debug tiếng Việt/emoji (như từ `zlapi/logging.py`) có thể ném `UnicodeEncodeError` và làm bot chết trên console Windows mã hóa `cp1252`.
- **Sửa Ctrl+C không dừng được bot**: vòng lặp `recv()` của `websockets` block kiểu *condition-wait vô hạn* — trên Windows, `Ctrl+C` không làm gián đoạn `queue.get()` không timeout, nên main thread ngủ vô hạn và không bao giờ xử lý tín hiệu. Hàm `signal_handler` giờ dùng `os._exit(0)` để thoát cứng ngay khi tín hiệu được xử lý.

### 3.3. `zlapi/_client.py` — vòng lặp lắng nghe

- `ws.recv()` được đổi thành `ws.recv(timeout=1)`: khi mạng im lặng, `TimeoutError` được bắt riêng (`continue`) để **không** ngắt kết nối, đồng thời main thread thức dậy **mỗi 1 giây** → bàn phím `Ctrl+C` luôn được xử lý trong vòng tối đa vài giây thay vì treo vô hạn.

### 3.4. Sửa 2 lỗi xử lý tin nhắn lặp lại (`_imei` và `modules.TEMP.antibot`)

- **`zlapi/_client.py`** — trong `ZaloAPI.__init__`, nhánh đăng nhập bằng `session_cookies` chỉ gọi `self._state.login(...)` nhưng **không gán** `self._imei` (chỉ `ZaloAPI.login()` ở nhánh phone/password mới gán). Vì `main.py` đăng nhập bằng cookies, mọi lệnh gọi API dùng `self._imei` (send, getUserInfo, userinfo...) đều văng `'Client' object has no attribute '_imei'`. Đã thêm `self._imei = imei` ngay sau `self._state.login(...)`.
- **`modules/TEMP/antibot.py`** (mới) — module này không tồn tại nên `antibot_cmd.py` không import được; và cứ mỗi lần gõ `...menu`, `menu.py` re-import toàn bộ `modules/*.py` → lỗi `No module named 'modules.TEMP.antibot'` mỗi lần. Đã tạo `modules/TEMP/__init__.py` + `modules/TEMP/antibot.py` cung cấp `get_group_settings`/`set_group_settings` (lưu JSON vào `modules/TEMP/antibot_settings.json`).
- **`modules/auto/antiqr.py`** — đổi `from pyzbar.pyzbar import decode` thành `try/except` (bọc trong `_PYZBAR_OK`); khi thiếu `libzbar-64.dll`, module vẫn load được, `has_qr_code` trả về `False` thay vì crash. 
- **`modules/menu.py`** — `get_all_hzlbot()` giờ bọc `importlib.import_module` trong `try/except`: 1 module bị lỗi sẽ bị bỏ qua (in cảnh báo) thay vì làm sập toàn bộ lệnh `...menu`.

### 3.5. `modules/nhac.py` — lệnh `...scl` gửi voice nhưng không phát được

- **Nguyên nhân**: Zalo chỉ phát được bubble voice với định dạng **m4a/AAC**. File **mp3** đặt ở host ngoài (uguu.se) hiện bubble nhưng bấm nghe không được (đã xác nhận link sống, `Content-Type: audio/mpeg`, magic `FF FB` — lỗi nằm ở codec, không phải link).
- **Sửa**: thêm `convert_to_m4a(file_path)` — dùng ffmpeg (qua gói `imageio-ffmpeg`, cài kèm ffmpeg tĩnh, không cần cài hệ thống) chuyển bài hát sang **m4a/AAC 128kbps** trước khi upload lên uguu; đồng thời giảm dung lượng (19MB mp3 → ~5-8MB).
- Nếu máy thiếu ffmpeg, chương trình tự bỏ qua bước đổi và gửi mp3 như cũ.
- Cài ffmpeg: `pip install imageio-ffmpeg`.

## 4. Kết quả sau sửa

Chạy thử `main.py` thực tế:

- Kết nối WebSocket thành công, log `DEBUG BẠN ĐANG DÙNG API ZLAPI 1.0.3` hiển thị.
- Nhận được frame `key` từ server (đã thiết lập phiên mã hóa).
- Nhận và phản hồi tin nhắn realtime từ nhóm (test với `...menu`, `...help`).
- Không còn `ConnectionClosedError` làm bot crash.
- Bấm `Ctrl+C` trong cửa sổ chạy bot sẽ tắt bot sạch sẽ (log `Nhận Ctrl+C, đang tắt bot...`).
- Hết lỗi `'Client' object has no attribute '_imei'` và `No module named 'modules.TEMP.antibot'`; `...menu` hiển thị đầy đủ lệnh (gồm `antibot`, `antiqr`).

## 5. Vấn đề còn lại (không thuộc phạm vi sửa kết nối)

- Lệnh **`...antiqr`** tải được nhưng tính năng **quét mã QR thực tế** chỉ hoạt động khi có bản ZBar native: cần cài thêm **ZBar** và thêm `libzbar-64.dll` vào `site-packages\pyzbar\`. Khi thiếu, bot vẫn chạy bình thường (bỏ qua ảnh QR).

---

*Project maintained by Nguyen Hoang*