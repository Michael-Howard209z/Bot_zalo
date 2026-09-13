import random
import time

from zlapi.models import ThreadType

TIMEOUT_SECONDS = 300  # 5 phút

REACTIONS = [
    "/-ok", "/-heart", "/-strong", "/-love",
    "😍", "❤️", "😂", "😉", "🥳", "🤩",
    "Dạ", "Yew", "Yes", "Ok", "Oki", "Uwu",
    "😃", "🥰", "👍", "🔥", "🎉",
]

# Lưu lần react gần nhất theo thread (hội thoại cá nhân)
_last_react_time = {}


def handle_auto_react(message, message_object, thread_id, thread_type, author_id, client):
    try:
        # Chỉ react tin nhắn cá nhân, không phải tin nhắn nhóm
        if thread_type != ThreadType.USER:
            return

        # Bỏ qua tin nhắn do chính bot gửi (echo trả về)
        if not author_id or author_id == str(client.uid):
            return

        # Timeout: mỗi 5 phút chỉ react 1 lần cho 1 hội thoại
        now = time.time()
        last = _last_react_time.get(thread_id, 0)
        if now - last < TIMEOUT_SECONDS:
            return

        _last_react_time[thread_id] = now

        # React bằng chữ hoặc bằng emoji (ngẫu nhiên)
        client.sendReaction(
            message_object,
            random.choice(REACTIONS),
            thread_id,
            thread_type
        )
    except Exception as e:
        print(f"[AUTO REACT DM] Lỗi: {e}")


def get_global_hzlbot():
    return [handle_auto_react]


def get_hzlbot():
    return {}