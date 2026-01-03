from zlapi.models import Message
from config import ADMIN
import time 

des = {
    'version': "1.0.2",
    'credits': "時崎狂三 ",
    'description': "add member by phone number <phone_number>"
}

def handle_adduser_by_phone_command(message, message_object, thread_id, thread_type, author_id, client):
    text = message.split()

    if len(text) < 2:
        error_message = Message(text=" nhập sdt.")
        client.sendMessage(error_message, thread_id, thread_type)
        return

    phone_number = text[1]

    try:
        user_info = client.fetchPhoneNumber(phone_number)

        print("api zalo ngu bao:", user_info)

        if user_info and hasattr(user_info, 'uid'):
            user_id = user_info.uid 
            user_name = user_info.zalo_name  

            client.addUsersToGroup(user_id, thread_id)

            send_message = f"Thêm thành công {user_name} vào nhóm."
        else:
            send_message = "LỖI CMM."

    except Exception as e:
        send_message = f"lỏ r đéo thêm được : {str(e)}"

    gui = Message(text=send_message)
    client.sendMessage(gui, thread_id, thread_type)

def get_hzlbot():
    return {
        'addsdt': handle_adduser_by_phone_command
    }