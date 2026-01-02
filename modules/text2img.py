from zlapi.models import Message
import requests

des = {
    'version': "1.0.2",
    'credits': "Nguyễn Đức Tài",
    'description': "Tạo ảnh từ text bằng DeepAI"
}

def handle_text2img_command(message, message_object, thread_id, thread_type, author_id, client):
    text = message.split()

    if len(text) < 2 or not text[1].strip():
        error_message = Message(text="Vui lòng nhập nội dung hợp lệ để chuyển đổi thành ảnh.")
        client.replyMessage(error_message, message_object, thread_id, thread_type)
        return

    content = " ".join(text[1:])

    api_url = "https://api.deepai.org/api/text2img"
    headers = {
        'api-key': 'c138adf0-c63c-4d87-b526-c44808495709',  # Sử dụng API key của bạn
    }
    data = {
        'text': content,
    }

    try:
        response = requests.post(api_url, headers=headers, data=data)
        response.raise_for_status()  # Kiểm tra lỗi HTTP

        data = response.json()
        image_url = data['output_url']

        # Gửi hình ảnh trở lại
        messagesend = Message(text="Đây là hình ảnh bạn đã tạo:")
        client.sendMessage(messagesend, thread_id, thread_type)
        
        client.sendRemoteImage(image_url, thread_id=thread_id, thread_type=thread_type)

    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except KeyError as e:
        error_message = Message(text=f"Dữ liệu từ API không đúng cấu trúc: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)

def get_mitaizl():
    return {
        'text2img': handle_text2img_command
    }