# Antilink Module - Cải tiến cho zlapi

## Tổng quan
Module antilink đã được cải tiến hoàn toàn để hoạt động tốt hơn với zlapi, với các tính năng mạnh mẽ và dễ sử dụng hơn.

## Các cải tiến chính

### 1. **Sửa lỗi API zlapi**
-  Đã sửa lại tham số `deleteGroupMsg()` đúng theo zlapi:
  - `msgId` (thay vì `msg_id`)
  - `ownerId` (thay vì `author_id`)
  - `clientMsgId` (thay vì `cli_msg_id`)
  - `groupId` (thay vì `thread_id`)

### 2. **Cải thiện phát hiện URL**
-  Phát hiện nhiều loại URL hơn:
  - `http://` và `https://`
  - `www.domain.com`
  - Domain trực tiếp: `facebook.com`, `zalo.me`, v.v.
-  Hỗ trợ nhiều TLD: `.com`, `.net`, `.org`, `.vn`, `.edu`, `.gov`, `.io`, `.co`, `.me`, `.info`, `.biz`

### 3. **Xử lý đồng bộ (Synchronous)**
-  Loại bỏ `async/await` vì zlapi sử dụng API đồng bộ
-  Tương thích hoàn toàn với cách zlapi hoạt động

### 4. **Kiểm tra an toàn**
-  Kiểm tra `message_object.msgType == "webchat"` thay vì `type == "msg"`
-  Bỏ qua tin nhắn của chính bot để tránh xóa nhầm
-  Kiểm tra thread type (chỉ hoạt động trong GROUP)
-  Kiểm tra thuộc tính tồn tại trước khi sử dụng

### 5. **Logging tốt hơn**
-  Tất cả log đều có prefix `[ANTILINK]`
-  Thêm traceback khi có lỗi để debug dễ hơn
-  Log chi tiết khi xóa tin nhắn thành công

### 6. **Thông báo thân thiện hơn**
-  Hiển thị tối đa 3 link bị chặn
-  Thông báo số lượng link còn lại nếu > 3
-  Hướng dẫn user liên hệ admin để thêm vào whitelist

### 7. **Utility functions cải tiến**
-  Các hàm utility trả về message thông báo
-  Kiểm tra tồn tại trước khi thao tác
-  Xử lý edge cases tốt hơn

## Cách sử dụng

### Bật/Tắt Antilink
```
<Prefix>antilink on    # Bật antilink
<Prefix>antilink off   # Tắt antilink
```

### Quản lý Whitelist
```
<Prefix>antilink add facebook.com      # Thêm domain vào whitelist
<Prefix>antilink add zalo.me           # Thêm domain khác
<Prefix>antilink remove facebook.com   # Xóa domain khỏi whitelist
<Prefix>antilink list                  # Xem danh sách whitelist
```

### Xem trạng thái
```
<Prefix>antilink status   # Xem trạng thái hiện tại
```

## Cấu hình

Mỗi nhóm có cấu hình riêng được lưu trong `modules/auto/antilink_config.json`:

```json
{
  "thread_id": {
    "status": true,           // Bật/tắt antilink
    "whitelist": [            // Danh sách domain được phép
      "facebook.com",
      "zalo.me",
      "youtube.com"
    ],
    "delete_msg": true,       // Có xóa tin nhắn không
    "warn_user": true         // Có gửi cảnh báo không
  }
}
```

## Quyền hạn

- **Admin bot** (trong `config.py`): Không bị ảnh hưởng bởi antilink
- **Admin nhóm**: Cần có quyền admin bot để cấu hình antilink
- **Thành viên thường**: Bị kiểm tra và xóa tin nhắn nếu gửi link không được phép

## Ví dụ sử dụng

### Kịch bản 1: Chặn tất cả link
```
<Prefix>antilink on
```
→ Tất cả link sẽ bị xóa (trừ admin bot)

### Kịch bản 2: Cho phép một số domain
```
<Prefix>antilink on
<Prefix>antilink add facebook.com
<Prefix>antilink add youtube.com
<Prefix>antilink add zalo.me
```
→ Chỉ link từ Facebook, YouTube, Zalo được phép

### Kịch bản 3: Kiểm tra cấu hình
```
<Prefix>antilink status
<Prefix>antilink list
```
→ Xem trạng thái và danh sách whitelist

## Xử lý lỗi

Module có xử lý lỗi toàn diện:
- Bắt lỗi khi xóa tin nhắn (có thể do thiếu quyền)
- Bắt lỗi khi gửi cảnh báo
- Bắt lỗi khi đọc/ghi config
- Log chi tiết để debug

## So sánh với phiên bản cũ

| Tính năng | Phiên bản cũ | Phiên bản mới |
|-----------|--------------|---------------|
| API compatibility | ❌ Sai tham số | ✅ Đúng tham số |
| URL detection | 🟡 Cơ bản | ✅ Nâng cao |
| Async/Sync | ❌ Async (sai) | ✅ Sync (đúng) |
| Bot message check | ❌ Không có | ✅ Có |
| Error handling | 🟡 Cơ bản | ✅ Toàn diện |
| Logging | 🟡 Đơn giản | ✅ Chi tiết |
| Command interface | ❌ Không có | ✅ Có đầy đủ |

## Troubleshooting

### Antilink không hoạt động?
1. Kiểm tra đã bật chưa: `<Prefix>antilink status`
2. Kiểm tra bot có quyền xóa tin nhắn không (cần là admin nhóm)
3. Xem log để biết lỗi cụ thể

### Tin nhắn không bị xóa?
1. Kiểm tra user có phải admin bot không
2. Kiểm tra link có trong whitelist không: `<Prefix>antilink list`
3. Kiểm tra cấu hình `delete_msg` có bật không

### Không nhận được cảnh báo?
1. Kiểm tra cấu hình `warn_user` có bật không
2. Kiểm tra bot có quyền gửi tin nhắn không

## Changelog

### Version 3.0 (2026-01-31)
- Sửa lại hoàn toàn để tương thích với zlapi
- Cải thiện phát hiện URL
- Thêm command interface
- Cải thiện error handling và logging
- Thêm kiểm tra bot message
- Cải thiện thông báo user


- Phiên bản cũ (có lỗi)

## Tác giả
- **Version 3.0**: Cải tiến cho zlapi
- **Credits**: Nguyen Hoang
