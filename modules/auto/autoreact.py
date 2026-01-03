from zlapi.models import Message 
des = {
    'version': "1.0.0",
    'credits': "Hoàng",
    'description': "Auto react tin nhắn"
}

def handle_autoreact_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        client.reactToMessage(message_object.id, 'LIKE', thread_id, thread_type)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi react: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)

def get_hzlbot():
    return {
        'autoreact': handle_autoreact_command
    }