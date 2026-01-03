import sys, os

from config import ADMIN
from zlapi.models import Message, MultiMsgStyle, MessageStyle

ADMIN_ID = ADMIN

des = {
    'version': "1.0.0",
    'credits': "Hoàng",
    'description': "Restart lại bot prefix (rs)"
}

def is_admin(author_id):
    return author_id == ADMIN_ID

def handle_reset_command(message, message_object, thread_id, thread_type, author_id, client):
    if not is_admin(author_id):
        msg = "• Bạn Không Có Quyền! Chỉ có admin mới có thể sử dụng lệnh này."
        styles = MultiMsgStyle([
            MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
            MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
            MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
        ])
        client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type)
        return

    try:
        msg = f"• loading hzl dev..."
        style = MultiMsgStyle([
            MessageStyle(offset=0, length=2, style="color", color="#80ff00", auto_format=False),
            MessageStyle(offset=2, length=len(msg) - 2, style="color", color="#a6e3a1", auto_format=False),
            MessageStyle(offset=0, length=45, style="color", color="#80ff00", auto_format=False),
            MessageStyle(offset=45, length=len(msg) - 2, style="color", color="#fff000", auto_format=False),
            MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
        ])
        client.replyMessage(Message(text=msg, style=style), message_object, thread_id, thread_type, ttl=12000)

        python = sys.executable
        os.execl(python, python, *sys.argv)

    except Exception as e:
        msg = f"• Đã xảy ra lỗi khi restart bot: {str(e)}"
        styles = MultiMsgStyle([
            MessageStyle(offset=0, length=2, style="color", color="#f38ba8", auto_format=False),
            MessageStyle(offset=2, length=len(msg)-2, style="color", color="#cdd6f4", auto_format=False),
            MessageStyle(offset=0, length=len(msg), style="font", size="13", auto_format=False)
        ])
        client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type)

def get_hzlbot():
    return {
        'rs': handle_reset_command
    }