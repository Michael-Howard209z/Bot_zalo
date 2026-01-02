from zlapi.models import Message

des = {
    'version': "1.0.3",
    'credits': "Nguyễn Đức Tài",
    'description': "Lấy id Zalo người dùng hoặc id người được tag"
}

def handle_meid_command(message, message_object, thread_id, thread_type, author_id, client):
    # Kiểm tra xem có người nào được tag không
    if message_object.mentions:
        tagged_users = ', '.join([mention['uid'] for mention in message_object.mentions])
    else:
        tagged_users = author_id

    # Tạo thông điệp phản hồi
    if message_object.mentions:
        response_message = f"ID của người được tag: {tagged_users}"
    else:
        response_message = f"ID của bạn: {tagged_users}"

    message_to_send = Message(text=response_message)
    client.replyMessage(message_to_send, message_object, thread_id, thread_type)

def get_hzlbot():
    return {
        'meid': handle_meid_command
    }