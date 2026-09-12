from zlapi.models import Message, MultiMsgStyle, MessageStyle
from zlapi._threads import ThreadType
from modules.auto.antilink import (
    toggle_antilink,
    add_to_whitelist,
    remove_from_whitelist,
    get_whitelist,
    get_group_settings,
    toggle_block_user
)
from modules.bot_info import is_admin

# ================== INFO ==================
des = {
    "version": "1.0.0",
    "credits": "Nguyen Hoang Dev ✓",
    "description": "Quản lý chống link trong nhóm",
    "power": "Quản trị viên"
}

def send_pixel(client, text, thread_id, thread_type, color="#000000", size="20"):
    style = MultiMsgStyle([
        MessageStyle(offset=0, length=len(text), style="font", size=size, auto_format=False),
        MessageStyle(offset=0, length=len(text), style="color", color=color, auto_format=False)
    ])
    client.send(Message(text=text, style=style), thread_id, thread_type)

def handle_antilink_command(message, message_object, thread_id, thread_type, author_id, client):
    """
    Xử lý lệnh quản lý antilink
    Cú pháp:
        ...antilink on/off - Bật/tắt antilink
        ...antilink block on/off - Bật/tắt tự động block
        ...antilink add <domain> - Thêm domain vào whitelist
        ...antilink remove <domain> - Xóa domain khỏi whitelist
        ...antilink list - Xem danh sách whitelist
        ...antilink status - Xem trạng thái hiện tại
    """
    try:
        # Chỉ hoạt động trong nhóm
        if thread_type != ThreadType.GROUP:
            send_pixel(client, "Lệnh này chỉ hoạt động trong nhóm!", thread_id, thread_type, color="#ff0000")
            return
        
        # Kiểm tra quyền admin
        if not is_admin(author_id):
            send_pixel(client, "Chỉ admin mới có thể sử dụng lệnh này!", thread_id, thread_type, color="#ff0000")
            return
        
        # Parse command
        parts = message.split()
        
        if len(parts) == 1:
            # Hiển thị hướng dẫn
            help_text = (
                "📋 **Hướng dẫn sử dụng Antilink**\n\n"
                "🔹 ...antilink on - Bật chống link\n"
                "🔹 ...antilink off - Tắt chống link\n"
                "🔹 ...antilink block on/off - Bật/tắt tự động BLOCK\n"
                "🔹 ...antilink add <domain> - Thêm domain vào whitelist\n"
                "   Ví dụ: ...antilink add facebook.com\n"
                "🔹 ...antilink remove <domain> - Xóa domain khỏi whitelist\n"
                "🔹 ...antilink list - Xem danh sách whitelist\n"
                "🔹 ...antilink status - Xem trạng thái hiện tại\n\n"
                "💡 **Lưu ý:**\n"
                "- Khi antilink bật, mọi link sẽ bị xóa trừ link trong whitelist\n"
                "- Admin bot không bị ảnh hưởng bởi antilink\n"
                "- Có thể thêm nhiều domain vào whitelist"
            )
            send_pixel(client, help_text, thread_id, thread_type, size="15")
            return
        
        action = parts[1].lower()
        
        if action == "on":
            result = toggle_antilink(thread_id, True)
            send_pixel(client, f" Đã bật antilink cho nhóm này!\n\n Sử dụng ...antilink add <domain> để thêm domain được phép.", thread_id, thread_type, color="#00ff00")
        
        elif action == "off":
            result = toggle_antilink(thread_id, False)
            send_pixel(client, "Đã tắt antilink cho nhóm này!", thread_id, thread_type, color="#ff0000")
        
        elif action == "block":
            if len(parts) < 3:
                send_pixel(client, " Vui lòng nhập on hoặc off!\nVí dụ: ...antilink block on", thread_id, thread_type, color="#ff0000")
                return
            
            sub_action = parts[2].lower()
            status = True if sub_action == "on" else False
            result = toggle_block_user(thread_id, status)
            
            send_pixel(client, result, thread_id, thread_type, color="#00ff00" if status else "#ff0000")

        elif action == "add":
            if len(parts) < 3:
                send_pixel(client, " Vui lòng nhập domain cần thêm!\nVí dụ: ...antilink add facebook.com", thread_id, thread_type, color="#ff0000")
                return
            
            domain = parts[2]
            result = add_to_whitelist(thread_id, domain)
            send_pixel(client, result, thread_id, thread_type, color="#00ff00")
        
        elif action == "remove":
            if len(parts) < 3:
                send_pixel(client, " Vui lòng nhập domain cần xóa!\nVí dụ: ...antilink remove facebook.com", thread_id, thread_type, color="#ff0000")
                return
            
            domain = parts[2]
            result = remove_from_whitelist(thread_id, domain)
            send_pixel(client, result, thread_id, thread_type, color="#00ff00")
        
        elif action == "list":
            whitelist = get_whitelist(thread_id)
            if whitelist:
                list_text = " **Danh sách domain được phép:**\n\n"
                for i, domain in enumerate(whitelist, 1):
                    list_text += f"{i}. {domain}\n"
            else:
                list_text = " Danh sách whitelist trống!\n\nSử dụng ...antilink add <domain> để thêm domain."
            
            send_pixel(client, list_text, thread_id, thread_type)
        
        elif action == "status":
            settings = get_group_settings(thread_id)
            status = " Đang bật" if settings.get('status', False) else " Đang tắt"
            delete_msg = " Có" if settings.get('delete_msg', True) else " Không"
            warn_user = " Có" if settings.get('warn_user', True) else " Không"
            block_user = " Có" if settings.get('block_user', False) else " Không"
            whitelist_count = len(settings.get('whitelist', []))
            
            status_text = (
                f" **Trạng thái Antilink**\n\n"
                f"🔹 Trạng thái: {status}\n"
                f"🔹 Xóa tin nhắn: {delete_msg}\n"
                f"🔹 Tự động Block: {block_user}\n"
                f"🔹 Gửi cảnh báo: {warn_user}\n"
                f"🔹 Số domain trong whitelist: {whitelist_count}\n\n"
                f"Dùng ...antilink list để xem chi tiết whitelist"
            )
            
            send_pixel(client, status_text, thread_id, thread_type)
        
        else:
            send_pixel(client, f"Lệnh không hợp lệ: {action}\n\nDùng ...antilink để xem hướng dẫn.", thread_id, thread_type, color="#ff0000")
    
    except Exception as e:
        print(f"[ANTILINK CMD] Lỗi: {e}")
        import traceback
        traceback.print_exc()
        send_pixel(client, f"Đã xảy ra lỗi khi xử lý lệnh: {str(e)}", thread_id, thread_type, color="#ff0000")

def get_hzlbot():
    """Export command handler"""
    return {
        'antilink': handle_antilink_command
    }
