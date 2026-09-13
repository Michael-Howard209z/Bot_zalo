import time

from zlapi.models import Message, MessageStyle, ThreadType

TIMEOUT_SECONDS = 300

# --- Cấu hình danh thiếp tài khoản mới (0889017113) ---
# UID Zalo (dãy số) của account 0889017113
UID = "8608278143078411663"
# URL ảnh avatar/QR của account đó — bỏ trống để bot tự lấy qua fetchUserInfo
QRCODE_URL = ""
# SĐT hiển thị trên danh thiếp
PHONE = "0889017113"
# ------------------------------------------------------

REPLY_CONTENT = (
    "đây là hệ thống tự động trả lời tin nhắn zalo| "
    "tài khoản này đã ngừng hoạt động nếu bạn có thắc mắc gì xin liên hệ tới "
    "tài khoản mới (0889017113)"
)

# Cỡ chữ hiển thị cho tin text (Zalo chỉ hỗ trợ cỡ chữ/màu/đậm... không hỗ trợ font family)
FONT_SIZE = "24"

_last_reply_time = {}


def send_business_card(client, thread_id, thread_type):
    card_uid = UID or str(client.uid)
    card_qr = QRCODE_URL

    if not card_qr:
        try:
            user_info = client.fetchUserInfo(card_uid).changed_profiles.get(str(card_uid))
            card_qr = user_info.avatar if user_info and getattr(user_info, "avatar", None) else None
        except Exception as e:
            print(f"[AUTO REPLY DM] Không lấy được avatar: {e}")
            card_qr = None

    if not card_qr:
        print("[AUTO REPLY DM] Bỏ qua danh thiếp: thiếu QRCODE_URL/avatar")
        return

    client.sendBusinessCard(
        userId=card_uid,
        qrCodeUrl=card_qr,
        thread_id=thread_id,
        thread_type=thread_type,
        phone=PHONE,
        ttl=60000
    )


def handle_auto_reply(message, message_object, thread_id, thread_type, author_id, client):
    try:
        if thread_type != ThreadType.USER:
            return

        if not author_id or author_id == str(client.uid):
            return

        now = time.time()
        last = _last_reply_time.get(thread_id, 0)
        if now - last < TIMEOUT_SECONDS:
            return

        _last_reply_time[thread_id] = now

        # Text thật dùng style Zalo hỗ trợ (cỡ chữ lớn)
        styled_text = Message(
            text=REPLY_CONTENT,
            style=MessageStyle(
                offset=0,
                length=len(REPLY_CONTENT),
                style="font",
                size=FONT_SIZE
            )
        )
        client.send(styled_text, thread_id, thread_type, ttl=60000)

        send_business_card(client, thread_id, thread_type)
    except Exception as e:
        print(f"[AUTO REPLY DM] Lỗi: {e}")


def get_global_hzlbot():
    return [handle_auto_reply]


def get_hzlbot():
    return {}