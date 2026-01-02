from zlapi.models import Message
import requests
import random
import threading
import time

def handle_vdgai_command(message, message_object, thread_id, thread_type, author_id, client):
    # Thông báo trước
    sent_msg = client.sendMessage(
        Message(text="Đang tìm video TikTok ngẫu nhiên..."),
        thread_id, thread_type
    )
    
    api_url = "https://www.tikwm.com/api/feed/search/"

    try:
        params = {
            "keywords": "gái xinh nhảy",
            "count": 30,
            "cursor": 0
        }

        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get("data", {}).get("videos", [])

        if not results:
            client.sendMessage(
                Message(text="Không tìm được video TikTok nào."),
                thread_id, thread_type
            )
            return

        # Random video
        selected = random.choice(results)

        video_url = selected.get("play", "")
        thumbnail_url = selected.get("cover", "") or selected.get("origin_cover", "")
        duration = str(selected.get("duration", 60))

        if not video_url:
            client.sendMessage(
                Message(text="Video không hợp lệ."),
                thread_id, thread_type
            )
            return

        # GỬI VIDEO
        video_msg = client.sendRemoteVideo(
            video_url,
            thumbnail_url,
            duration=duration,
            message=None,
            thread_id=thread_id,
            thread_type=thread_type,
            width=1080,
            height=1920
        )

        # --------------------------
        #  TỰ ĐỘNG THU HỒI SAU 15 GIÂY
        # --------------------------
        def auto_recall(msg):
            time.sleep(15)
            try:
                client.recallMessage(msg.msgId, thread_id, thread_type)
            except:
                pass

        threading.Thread(target=auto_recall, args=(video_msg,), daemon=True).start()

    except Exception as e:
        client.sendMessage(
            Message(text=f"Lỗi API TikTok: {str(e)}"),
            thread_id, thread_type
        )


def get_hzlbot():
    return {
        'vdgai': handle_vdgai_command
    }
