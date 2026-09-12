from zlapi.models import Message, ThreadType
import time
import re

des = {
    'version': "1.0.0",
    'credits': "Nguyen Hoang Dev",
    'description': "Join nhóm bằng link, gửi tin nhắn và rời nhóm (Spam & Run)"
}

def handle_join_spam(message, message_object, thread_id, thread_type, author_id, client):
    """
    Cú pháp: <prefix>join <link_nhóm> <delay> <nội dung tin nhắn>
    Ví dụ: !join https://zalo.me/g/abcxyz 5 Hello mọi người
    """
    content = message.split()
    
    if len(content) < 3:
        client.replyMessage(
            Message(text=" Sai cú pháp!\nSử dụng: <prefix>join <link_nhóm> <delay> <nội dung tin nhắn>"),
            message_object, thread_id, thread_type
        )
        return
        
    link = content[1]
    try:
        delay = int(content[2])
    except ValueError:
        client.replyMessage(Message(text="Delay phải là số giây (ví dụ: 5)."), message_object, thread_id, thread_type)
        return
        
    msg_text = " ".join(content[3:])
    if not msg_text:
        msg_text = "Xin chào mọi người! Bot ghé chơi chút rồi đi nha "

    # Lấy code từ link (zalo.me/g/code)
    match = re.search(r'zalo\.me/g/([a-zA-Z0-9]+)', link)
    if not match:
        client.replyMessage(Message(text="Link nhóm không hợp lệ."), message_object, thread_id, thread_type)
        return
    
    code = match.group(1)
    
    try:
        client.replyMessage(Message(text=f"Đang thực hiện vào nhóm..."), message_object, thread_id, thread_type)
        
        # Thực hiện join
        res = client.joinGroup(code)
        
        target_group_id = None
        
        # Xử lý kết quả trả về để lấy Group ID
        if isinstance(res, dict) and 'groupId' in res:
            target_group_id = res['groupId']
        elif hasattr(res, 'groupId'):
            target_group_id = res.groupId
        elif isinstance(res, str) and res.isdigit():
            target_group_id = res
            
        if not target_group_id:
            client.replyMessage(Message(text="Đã gửi yêu cầu vào nhóm nhưng không lấy được ID nhóm để gửi tin nhắn."), message_object, thread_id, thread_type)
            return

        # Đợi delay
        if delay > 0:
            time.sleep(delay)
        
        # Gửi tin nhắn vào nhóm mới
        client.send(Message(text=msg_text), target_group_id, ThreadType.GROUP)
        
        # Rời nhóm
        client.leaveGroup(target_group_id)
        
        client.replyMessage(Message(text=f"Đã hoàn thành nhiệm vụ!\n- Vào nhóm: {target_group_id}\n- Gửi tin: '{msg_text}'\n- Đã rời nhóm"), message_object, thread_id, thread_type)

    except Exception as e:
        client.replyMessage(Message(text=f"Lỗi: {str(e)}"), message_object, thread_id, thread_type)

def get_hzlbot():
    return {
        'join': handle_join_spam
    }
