import random
from zlapi.models import Message
from zlapi._threads import ThreadType

# ================== INFO ==================
des = {
    "version": "1.2.0",
    "credits": "Nguyen Hoang Dev ✓",
    "description": "Auto react tin nhắn ngẫu nhiên và emoji ngẫu nhiên",
    "power": "Thành viên"
}

# ================== CONFIG ==================
# Danh sách emoji ngẫu nhiên
EMOJIS = ["❤️", "👍", "😂", "😆", "😲", "😡", "😭", "🔥", "💯", "👏", "🙌", "✨", "✅", "🎉", "😎", "🤔"]
# Tỷ lệ react (0.3 = 30% tin nhắn sẽ được react)
REACT_PROBABILITY = 0.3
REACTION_TYPE = 75     # mặc định của Zalo
AUTO_REACT_ENABLED = True  # Bật/tắt auto react

# ================== HANDLER ==================
def handle_autoreact_random(message, message_object, thread_id, thread_type, author_id, client):
    """
    Auto react tin nhắn với tỷ lệ ngẫu nhiên và emoji ngẫu nhiên
    """
    if not AUTO_REACT_ENABLED:
        return

    # Bỏ qua tin nhắn của bot
    if str(author_id) == str(client.uid):
        return

    # Bỏ qua sự kiện reaction (tránh lặp vô hạn)
    if message_object.msgType == "chat.reaction":
        return

    # Kiểm tra tin nhắn hợp lệ
    if not message_object or not hasattr(message_object, 'msgId') or not message_object.msgId:
        return

    # Quyết định xem có react hay không (ngẫu nhiên)
    if random.random() > REACT_PROBABILITY:
        return

    try:
        # Chọn emoji ngẫu nhiên
        random_emoji = random.choice(EMOJIS)
        
        client.sendReaction(
            messageObject=message_object,
            reactionIcon=random_emoji,
            thread_id=thread_id,
            thread_type=thread_type,
            reactionType=REACTION_TYPE
        )
    except Exception as e:
        # Không spam log
        print(f"[AUTO-REACT-RANDOM ERROR] {e}")

# ================== EXPORT ==================
def get_global_hzlbot():
    """
    Trả về handler xử lý toàn cục (chạy với mọi tin nhắn)
    """
    return [handle_autoreact_random]
