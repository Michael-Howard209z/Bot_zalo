from zlapi.models import Message
import requests
import urllib.parse
import time
from datetime import datetime

des = {
    'version': "1.9.2",
    'credits': "Nguyễn Đức Tài",
    'description': "trò chuyện với simi"
}

def handle_sim_command(message, message_object, thread_id, thread_type, author_id, client):
    text = message.split()

    if len(text) < 2:
        error_message = Message(text="Vui lòng nhập câu hỏi để trò chuyện cùng binz botchat 💬")
        client.sendMessage(error_message, thread_id, thread_type)
        return

    content = " ".join(text[1:])
    encoded_text = urllib.parse.quote(content)

    try:
        sim_url = f'https://apiquockhanh.click/sim?type=ask&ask={encoded_text}'  # Thay đổi URL
        response = requests.get(sim_url)
        response.raise_for_status()

        data = response.json()
        simi = data.get('answer', 'Không có phản hồi từ Simi.')
        message_to_send = Message(text=f"> botchat binz : {simi}")
        
        client.replyMessage(
            message_to_send,
            message_object,
            thread_id,
            thread_type,
            ttl=60000
        )

    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except KeyError:
        error_message = Message(text="Dữ liệu từ API không đúng cấu trúc.")
        client.sendMessage(error_message, thread_id, thread_type)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)

def handle_teach_sim_command(message, message_object, thread_id, thread_type, author_id, client):
    text = message.split()

    if len(text) < 3:
        error_message = Message(text="Vui lòng nhập câu nói và phản hồi để dạy simi.")
        client.sendMessage(error_message, thread_id, thread_type)
        return

    teach_text = " ".join(text[1:-1])
    teach_response = text[-1]
    encoded_teach_text = urllib.parse.quote(teach_text)
    encoded_teach_response = urllib.parse.quote(teach_response)

    print(f"Đang dạy simi: Câu hỏi='{teach_text}', Phản hồi='{teach_response}'")  # Gỡ lỗi: in ra câu hỏi và phản hồi

    try:
        teach_url = f'https://apiquockhanh.click/sim?type=teach&ask={encoded_teach_text}&ans={encoded_teach_response}'  # Thay đổi URL
        print(f"Gửi yêu cầu tới API: {teach_url}")  # Gỡ lỗi: in ra URL yêu cầu
        response = requests.get(teach_url)
        response.raise_for_status()

        data = response.json()
        print("Dữ liệu trả về từ API:", data)  # In ra toàn bộ dữ liệu trả về từ API để kiểm tra

        msg = data.get("msg")
        if msg:
            if msg == "Dạy học binz chatbot thành công":
                ask = data.get("data", {}).get("ask", "Không có câu hỏi.")
                ans = data.get("data", {}).get("ans", "Không có phản hồi.")
                message_to_send = Message(text=f"> Sim đã học: '{ask}' -> '{ans}'")
            else:
                message_to_send = Message(text=f"Không thể dạy sim, thông báo từ API: {msg}")
        else:
            message_to_send = Message(text="Không thể dạy sim, không có thông báo từ API.")

        client.replyMessage(
            message_to_send,
            message_object,
            thread_id,
            thread_type,
            ttl=60000
        )

    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        print("Lỗi khi gọi API:", str(e))  # Gỡ lỗi: in ra lỗi khi gọi API
        client.sendMessage(error_message, thread_id, thread_type)
    except KeyError:
        error_message = Message(text="Dữ liệu từ API không đúng cấu trúc.")
        print("Lỗi cấu trúc dữ liệu:", str(e))  # Gỡ lỗi: in ra lỗi KeyError
        client.sendMessage(error_message, thread_id, thread_type)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}")
        print("Lỗi không xác định:", str(e))  # Gỡ lỗi: in ra lỗi không xác định
        client.sendMessage(error_message, thread_id, thread_type)

def get_mitaizl():
    return {
        'gpt': handle_sim_command,
        'học': handle_teach_sim_command
    }