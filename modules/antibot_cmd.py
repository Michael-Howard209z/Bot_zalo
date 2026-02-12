from zlapi.models import Message
from zlapi._threads import ThreadType
from modules.auto.antibot import get_group_settings, set_group_settings
from modules.bot_info import is_admin

# ================== INFO ==================
des = {
    "version": "1.0.0",
    "credits": "Gemini Code Assist",
    "description": "Quản lý chống bot khác trong nhóm",
    "power": "Quản trị viên"
}

# ================== COMMAND HANDLER ==================
def handle_antibot_command(message, message_object, thread_id, thread_type, author_id, client):
    """
    Xử lý lệnh quản lý antibot
    Cú pháp:
        ...antibot on/off - Bật/tắt antibot
        ...antibot warn on/off - Bật/tắt cảnh báo
        ...antibot block on/off - Bật/tắt tự động chặn
        ...antibot status - Xem trạng thái
    """
    try:
        if thread_type != ThreadType.GROUP:
            client.send(Message(text="Lệnh này chỉ hoạt động trong nhóm!"), thread_id, thread_type)
            return
        
        if not is_admin(author_id):
            client.send(Message(text="Chỉ admin mới có thể sử dụng lệnh này!"), thread_id, thread_type)
            return
        
        parts = message.split()
        action = parts[1].lower() if len(parts) > 1 else "help"
        settings = get_group_settings(thread_id)
        
        if action == "on":
            settings['status'] = True
            set_group_settings(thread_id, settings)
            client.send(Message(text="✅ Đã bật anti-bot cho nhóm này."), thread_id, thread_type)
        
        elif action == "off":
            settings['status'] = False
            set_group_settings(thread_id, settings)
            client.send(Message(text="🔴 Đã tắt anti-bot cho nhóm này."), thread_id, thread_type)

        elif action == "warn":
            if len(parts) < 3 or parts[2].lower() not in ['on', 'off']:
                client.send(Message(text="Cú pháp: ...antibot warn on/off"), thread_id, thread_type)
                return
            status = parts[2].lower() == 'on'
            settings['warn_user'] = status
            set_group_settings(thread_id, settings)
            client.send(Message(text=f"✅ Đã {'bật' if status else 'tắt'} tính năng cảnh báo người dùng."), thread_id, thread_type)

        elif action == "block":
            if len(parts) < 3 or parts[2].lower() not in ['on', 'off']:
                client.send(Message(text="Cú pháp: ...antibot block on/off"), thread_id, thread_type)
                return
            status = parts[2].lower() == 'on'
            settings['block_user'] = status
            set_group_settings(thread_id, settings)
            client.send(Message(text=f"✅ Đã {'bật' if status else 'tắt'} tính năng tự động chặn (blacklist) người dùng."), thread_id, thread_type)
            
        elif action == "status":
            status_text = "🟢 Đang bật" if settings.get('status', False) else "🔴 Đang tắt"
            warn_text = "🟢 Bật" if settings.get('warn_user', True) else "🔴 Tắt"
            block_text = "🟢 Bật" if settings.get('block_user', False) else "🔴 Tắt"
            
            status_msg = (
                f"**Trạng thái Anti-bot**\n\n"
                f"🔹 **Trạng thái chung**: {status_text}\n"
                f"🔹 **Cảnh báo người dùng**: {warn_text}\n"
                f"🔹 **Tự động chặn (blacklist)**: {block_text}"
            )
            client.send(Message(text=status_msg), thread_id, thread_type)
            
        else: # help
            help_text = (
                "**Hướng dẫn sử dụng Antibot**\n\n"
                "**Bật/Tắt chung:**\n"
                "🔹 `...antibot on` - Bật anti-bot\n"
                "🔹 `...antibot off` - Tắt anti-bot\n\n"
                "**Cấu hình hành động:**\n"
                "🔹 `...antibot warn on/off` - Bật/tắt gửi cảnh báo.\n"
                "🔹 `...antibot block on/off` - Bật/tắt tự động chặn người dùng (blacklist).\n\n"
                "**Kiểm tra:**\n"
                "🔹 `...antibot status` - Xem trạng thái cấu hình hiện tại."
            )
            client.send(Message(text=help_text), thread_id, thread_type)
            
    except Exception as e:
        print(f"[ANTIBOT CMD] Lỗi: {e}")
        client.send(Message(text=f"Đã xảy ra lỗi: {e}"), thread_id, thread_type)

def get_hzlbot():
    return {
        'antibot': handle_antibot_command,
    }