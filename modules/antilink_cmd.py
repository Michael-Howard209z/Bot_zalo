from zlapi.models import Message
from zlapi._threads import ThreadType
from modules.auto.antilink import (
    toggle_antilink,
    add_to_whitelist,
    remove_from_whitelist,
    get_whitelist,
    get_group_settings
)
from modules.bot_info import is_admin

# ================== INFO ==================
des = {
    "version": "1.0.0",
    "credits": "Nguyen Hoang Dev ✓",
    "description": "Quản lý chống link trong nhóm",
    "power": "Quản trị viên"
}

def handle_antilink_command(message, message_object, thread_id, thread_type, author_id, client):
    """
    Xử lý lệnh quản lý antilink
    Cú pháp:
        /antilink on/off - Bật/tắt antilink
        /antilink add <domain> - Thêm domain vào whitelist
        /antilink remove <domain> - Xóa domain khỏi whitelist
        /antilink list - Xem danh sách whitelist
        /antilink status - Xem trạng thái hiện tại
    """
    try:
        # Chỉ hoạt động trong nhóm
        if thread_type != ThreadType.GROUP:
            client.send(
                Message(text="⚠️ Lệnh này chỉ hoạt động trong nhóm!"),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return
        
        # Kiểm tra quyền admin
        if not is_admin(author_id):
            client.send(
                Message(text="⚠️ Chỉ admin mới có thể sử dụng lệnh này!"),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return
        
        # Parse command
        parts = message.split()
        
        if len(parts) == 1:
            # Hiển thị hướng dẫn
            help_text = (
                "📋 **Hướng dẫn sử dụng Antilink**\n\n"
                "🔹 `/antilink on` - Bật chống link\n"
                "🔹 `/antilink off` - Tắt chống link\n"
                "🔹 `/antilink add <domain>` - Thêm domain vào whitelist\n"
                "   Ví dụ: `/antilink add facebook.com`\n"
                "🔹 `/antilink remove <domain>` - Xóa domain khỏi whitelist\n"
                "🔹 `/antilink list` - Xem danh sách whitelist\n"
                "🔹 `/antilink status` - Xem trạng thái hiện tại\n\n"
                "💡 **Lưu ý:**\n"
                "- Khi antilink bật, mọi link sẽ bị xóa trừ link trong whitelist\n"
                "- Admin bot không bị ảnh hưởng bởi antilink\n"
                "- Có thể thêm nhiều domain vào whitelist"
            )
            client.send(
                Message(text=help_text),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return
        
        action = parts[1].lower()
        
        if action == "on":
            result = toggle_antilink(thread_id, True)
            client.send(
                Message(text=f"✅ Đã bật antilink cho nhóm này!\n\n💡 Sử dụng `/antilink add <domain>` để thêm domain được phép."),
                thread_id=thread_id,
                thread_type=thread_type
            )
        
        elif action == "off":
            result = toggle_antilink(thread_id, False)
            client.send(
                Message(text="🔓 Đã tắt antilink cho nhóm này!"),
                thread_id=thread_id,
                thread_type=thread_type
            )
        
        elif action == "add":
            if len(parts) < 3:
                client.send(
                    Message(text="⚠️ Vui lòng nhập domain cần thêm!\nVí dụ: `/antilink add facebook.com`"),
                    thread_id=thread_id,
                    thread_type=thread_type
                )
                return
            
            domain = parts[2]
            result = add_to_whitelist(thread_id, domain)
            client.send(
                Message(text=result),
                thread_id=thread_id,
                thread_type=thread_type
            )
        
        elif action == "remove":
            if len(parts) < 3:
                client.send(
                    Message(text="⚠️ Vui lòng nhập domain cần xóa!\nVí dụ: `/antilink remove facebook.com`"),
                    thread_id=thread_id,
                    thread_type=thread_type
                )
                return
            
            domain = parts[2]
            result = remove_from_whitelist(thread_id, domain)
            client.send(
                Message(text=result),
                thread_id=thread_id,
                thread_type=thread_type
            )
        
        elif action == "list":
            whitelist = get_whitelist(thread_id)
            if whitelist:
                list_text = "📝 **Danh sách domain được phép:**\n\n"
                for i, domain in enumerate(whitelist, 1):
                    list_text += f"{i}. {domain}\n"
            else:
                list_text = "📝 Danh sách whitelist trống!\n\n💡 Sử dụng `/antilink add <domain>` để thêm domain."
            
            client.send(
                Message(text=list_text),
                thread_id=thread_id,
                thread_type=thread_type
            )
        
        elif action == "status":
            settings = get_group_settings(thread_id)
            status = "🟢 Đang bật" if settings.get('status', False) else "🔴 Đang tắt"
            delete_msg = "✅ Có" if settings.get('delete_msg', True) else "❌ Không"
            warn_user = "✅ Có" if settings.get('warn_user', True) else "❌ Không"
            whitelist_count = len(settings.get('whitelist', []))
            
            status_text = (
                f"📊 **Trạng thái Antilink**\n\n"
                f"🔹 Trạng thái: {status}\n"
                f"🔹 Xóa tin nhắn: {delete_msg}\n"
                f"🔹 Gửi cảnh báo: {warn_user}\n"
                f"🔹 Số domain trong whitelist: {whitelist_count}\n\n"
                f"💡 Dùng `/antilink list` để xem chi tiết whitelist"
            )
            
            client.send(
                Message(text=status_text),
                thread_id=thread_id,
                thread_type=thread_type
            )
        
        else:
            client.send(
                Message(text=f"⚠️ Lệnh không hợp lệ: {action}\n\nDùng `/antilink` để xem hướng dẫn."),
                thread_id=thread_id,
                thread_type=thread_type
            )
    
    except Exception as e:
        print(f"[ANTILINK CMD] Lỗi: {e}")
        import traceback
        traceback.print_exc()
        client.send(
            Message(text=f"❌ Đã xảy ra lỗi khi xử lý lệnh: {str(e)}"),
            thread_id=thread_id,
            thread_type=thread_type
        )

def get_hzlbot():
    """Export command handler"""
    return {
        'antilink': handle_antilink_command
    }
