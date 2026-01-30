from zlapi.models import Message
from zlapi._threads import ThreadType

# ================== INFO ==================
des = {
    "version": "1.1.0",
    "credits": "Nguyen Hoang Dev ✓",
    "description": "Auto react tin nhắn",
    "power": "Thành viên"
}

# ================== CONFIG ==================
REACTION_ICON = "💢💥💤"   # icon react (👍 😂 ❤️ 😆 😡 🔥 ...)
REACTION_TYPE = 75     # mặc định của Zalo
AUTO_REACT_ENABLED = True  # Bật/tắt auto react

# ================== HANDLER ==================
def handle_autoreact(message, message_object, thread_id, thread_type, author_id, client):
    """
    Auto react tất cả tin nhắn hợp lệ
    """
    # Kiểm tra nếu tắt auto react
    if not AUTO_REACT_ENABLED:
        return

    # ❌ bỏ qua tin nhắn của bot
   # if str(author_id) == str(client.uid):
     #   return

    # ❌ chỉ react tin nhắn thường
    if not message_object or not hasattr(message_object, 'msgId') or not message_object.msgId:
        return

    try:
        client.sendReaction(
            messageObject=message_object,
            reactionIcon=REACTION_ICON,
            thread_id=thread_id,
            thread_type=thread_type,
            reactionType=REACTION_TYPE
        )
    except Exception as e:
        # không spam log
        print(f"[AUTO-REACT ERROR] {e}")

# ================== EXPORT ==================
def get_global_hzlbot():
    """
    Trả về handler xử lý toàn cục (chạy với mọi tin nhắn)
    """
    return [handle_autoreact]
