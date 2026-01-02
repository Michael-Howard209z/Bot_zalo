from zlapi.models import Message
import requests
import urllib.parse


des = {
    'version': "1.9.9",
    'credits': "Dzi x Tool",
    'description': "trò chuyện với cyberd"
}


def handle_cyberd_command(message, message_object, thread_id, thread_type, author_id, client):
    text = message.split()

    
    if len(text) < 2:
        error_message = Message(text="Chào bạn ! tôi là cyberd binz dev 👨‍💻 vui lòng nhập câu hỏi để trò chuyện cùng cyberd nhé.")
        client.sendMessage(error_message, thread_id, thread_type,ttl=10000000)
        return

    
    content = " ".join(text[1:])
    encoded_text = urllib.parse.quote(content, safe='')

    try:
        
        cyberd_url = f'https://api.cyberd.dcb.x10.mx/cyberdai?api-key=1709&dcb={encoded_text}'
        response = requests.get(cyberd_url)
        response.raise_for_status()

        
        cyberdi_response = response.text.strip() if response.text.strip() else "Không có phản hồi từ cyberd"
        
        
        message_to_send = Message(text=f"> binz dev: {cyberdi_response}")
        client.replyMessage(
            message_to_send,
            message_object,
            thread_id,
            thread_type,
            ttl=86400000
        )

    
    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type,ttl=10000)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type,ttl=10000)


def get_mitaizl():
    return {
        'cyberd': handle_cyberd_command
    }