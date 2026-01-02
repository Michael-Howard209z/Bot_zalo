from zlapi.models import Message
import requests
import os

# nơi lưu marker theo thread_id
sent_image_marker = {} 


def handle_anhgai_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        MARK = "[ANIME18_IMAGE]"   # dùng để nhận echo sau khi gửi ảnh
        sent_image_marker[thread_id] = MARK

        sendmess = f"Yêu Pajbownbdzs1tg 💤 💢\n{MARK}"
        message_to_send = Message(text=sendmess)

        api_url = "https://api.waifu.pics/nsfw/waifu"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        image_url = data.get("url")

        if not image_url:
            client.sendMessage(Message(text="API không trả về ảnh."), thread_id, thread_type)
            return

        # tải ảnh
        img_data = requests.get(image_url, headers=headers).content
        image_path = "temp_image.jpeg"

        with open(image_path, "wb") as f:
            f.write(img_data)

        # gửi ảnh (KHÔNG có msgId trả về)
        client.sendLocalImage(
            image_path,
            message=message_to_send,
            thread_id=thread_id,
            thread_type=thread_type,
            width=1200,
            height=1600
        )

        os.remove(image_path)

    except Exception as e:
        client.sendMessage(
            Message(text=f"Đã xảy ra lỗi: {str(e)}"),
            thread_id, thread_type
        )


def get_hzlbot():
    return {
        "anime18": handle_anhgai_command
    }
