import json
import os
from config import ADMIN, PREFIX
from zlapi.models import Message, ThreadType

# ================== INFO ==================
des = {
    'version': "1.0.0",
    'credits': "Gemini Code Assist",
    'description': "Chống các bot khác hoạt động trong nhóm."
}

# ================== CONFIG ==================
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'antibot_config.json')

# Các tiền tố lệnh phổ biến của bot khác (sẽ tự động loại trừ tiền tố của bot này)
OTHER_BOT_PREFIXES = ['/', '!', '#', '$', '%', '^', '&', '*', '?']

# ================== HELPER FUNCTIONS ==================
def load_config():
    """Tải cấu hình từ file JSON"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config):
    """Lưu cấu hình vào file JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ANTIBOT] Lỗi khi lưu config: {e}")

def get_group_settings(thread_id):
    """Lấy cài đặt của nhóm"""
    config = load_config()
    default_settings = {
        'status': False,
        'warn_user': True,
        'block_user': False
    }
    settings = config.get(str(thread_id), default_settings.copy())
    for key, value in default_settings.items():
        settings.setdefault(key, value)
    return settings

def set_group_settings(thread_id, settings):
    """Cập nhật cài đặt của nhóm"""
    config = load_config()
    config[str(thread_id)] = settings
    save_config(config)

def is_admin(author_id):
    """Kiểm tra xem user có phải admin không"""
    return str(author_id) in map(str, ADMIN)

# ================== MAIN HANDLER ==================
def handle_antibot(message, message_object, thread_id, thread_type, author_id, client):
    try:
        if thread_type != ThreadType.GROUP:
            return

        settings = get_group_settings(thread_id)
        if not settings.get('status', False):
            return

        if is_admin(author_id) or str(author_id) == str(client.uid):
            return
            
        if not isinstance(message, str) or not message:
            return

        prefixes_to_check = [p for p in OTHER_BOT_PREFIXES if p != PREFIX]
        message_lower = message.lower().strip()

        for prefix in prefixes_to_check:
            if message_lower.startswith(prefix):
                # --- VIOLATION DETECTED ---

                # 1. Delete message
                try:
                    if hasattr(message_object, 'msgId') and hasattr(message_object, 'cliMsgId'):
                        client.deleteGroupMsg(
                            msgId=message_object.msgId,
                            ownerId=author_id,
                            clientMsgId=message_object.cliMsgId,
                            groupId=thread_id
                        )
                        print(f"[ANTIBOT] Đã xóa lệnh bot của user {author_id} trong nhóm {thread_id}: {message}")
                except Exception as e:
                    print(f"[ANTIBOT] Lỗi khi xóa tin nhắn: {e}")

                # Get user name for notifications
                user_name = author_id
                try:
                    user_info = client.fetchUserInfo(author_id).changed_profiles.get(author_id)
                    if user_info and hasattr(user_info, 'displayName'):
                        user_name = user_info.displayName
                except Exception as e:
                    print(f"[ANTIBOT] Không thể lấy tên user {author_id}: {e}")

                # 2. Block user if enabled
                if settings.get('block_user', False):
                    try:
                        client.blockUsersInGroup(author_id, thread_id)
                        print(f"[ANTIBOT] Đã BLOCK user {author_id} khỏi nhóm {thread_id}")
                        client.send(
                            Message(text=f"🚫 Đã chặn thành viên {user_name} khỏi nhóm vì sử dụng lệnh bot khác."),
                            thread_id, thread_type
                        )
                    except Exception as e:
                        print(f"[ANTIBOT] Lỗi khi block user: {e}")
                    return

                # 3. Warn user if enabled (and not blocked)
                if settings.get('warn_user', True):
                    try:
                        warning_text = f"⚠️ {user_name}, vui lòng không sử dụng lệnh của bot khác trong nhóm này."
                        client.send(Message(text=warning_text), thread_id, thread_type)
                    except Exception as e:
                        print(f"[ANTIBOT] Lỗi khi gửi cảnh báo: {e}")

                return

    except Exception as e:
        print(f"[ANTIBOT] Lỗi trong handle_antibot: {e}")

# ================== EXPORT ==================
def get_global_hzlbot():
    """Trả về danh sách các hàm xử lý event toàn cục"""
    return [handle_antibot]

def get_hzlbot():
    return {}