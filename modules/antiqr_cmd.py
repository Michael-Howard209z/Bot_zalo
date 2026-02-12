from zlapi.models import Message
from zlapi._threads import ThreadType
from modules.auto.antiqr import get_group_settings, set_group_settings
from modules.bot_info import is_admin

# ================== INFO ==================
des = {
    "version": "1.0.0",
    "credits": "Gemini Code Assist",
    "description": "Quản lý chống gửi ảnh QR trong nhóm",
    "power": "Quản trị viên"
}

# ================== COMMAND HANDLER ==================
def handle_antiqr_command(message, message_object, thread_id, thread_type, author_id, client):
    """
    Xử lý lệnh quản lý antiqr
    Cú pháp:
        ...antiqr on/off - Bật/tắt antiqr
        ...antiqr status - Xem trạng thái hiện tại
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
            client.send(Message(text="Đã bật tính năng chống gửi ảnh QR cho nhóm này."), thread_id, thread_type)
        
        elif action == "off":
            settings['status'] = False
            set_group_settings(thread_id, settings)
            client.send(Message(text="Đã tắt tính năng chống gửi ảnh QR cho nhóm này."), thread_id, thread_type)
            
        elif action == "status":
            status_text = "Đang bật" if settings.get('status', False) else "Đang tắt"
            client.send(Message(text=f"Trạng thái anti-QR hiện tại: {status_text}"), thread_id, thread_type)
            
        else: # help
            help_text = ("**Hướng dẫn sử dụng Anti-QR**\n\n"
                         "...antiqr on - Bật chống gửi ảnh QR\n"
                         "...antiqr off - Tắt chống gửi ảnh QR\n"
                         "...antiqr status - Xem trạng thái")
            client.send(Message(text=help_text), thread_id, thread_type)
            
    except Exception as e:
        print(f"[ANTIQR CMD] Lỗi: {e}")
        client.send(Message(text=f"Đã xảy ra lỗi: {e}"), thread_id, thread_type)

def get_hzlbot():
    return {'antiqr': handle_antiqr_command}