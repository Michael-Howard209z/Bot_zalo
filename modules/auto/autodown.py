import re
import requests
from zlapi.models import Message

des = {
    'version': "1.0.6",
    'credits': "Nguyễn Đức Tài",
    'description': "autodown"
}

regex = r"https?://(?:www\.|m\.|vm\.|vt\.)?tiktok\.com/(?:@[\w.-]+/video/\d+|v/\d+|[\w-]+)"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Accept': 'application/json'
}

def handle_autodown_command(message, message_object, thread_id, thread_type, author_id, client):
    match = re.search(regex, message)
    if not match:
        return

    linkvd = match.group(0)
    api_url = f'https://api.sumiproject.net/tiktok?video={linkvd}'

    try:
        response = requests.get(api_url, headers=headers, timeout=20)
        response.raise_for_status()

        data = response.json()
        
        # Xử lý cấu trúc JSON linh hoạt hơn (tránh lỗi NoneType)
        video_data = data.get('data') or {}
        if isinstance(video_data, dict) and 'data' in video_data:
            video_data = video_data['data']

        video_url = video_data.get('play')
        thumbnail_url = video_data.get('cover') or video_data.get('origin_cover') or 'https://files.catbox.moe/34xdgb.jpeg'
        
        duration = video_data.get('duration', 0)
        try:
            duration = int(duration)
            if duration < 1000: # Nếu API trả về giây, đổi sang mili giây
                duration *= 1000
        except (ValueError, TypeError):
            duration = 1000

        if video_url:
            client.sendRemoteVideo(
                video_url,
                thumbnail_url,
                duration=duration,
                message=None,
                thread_id=thread_id,
                thread_type=thread_type,
                width=1080,
                height=1920
            )
        else:
            error_message = Message(text="Không thể lấy video từ liên kết TikTok.")
            client.sendMessage(error_message, thread_id, thread_type)
    
    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)

def get_hzlbot():
    return {
        'autodown': handle_autodown_command
    }
