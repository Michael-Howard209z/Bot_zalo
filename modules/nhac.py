# -*- coding: UTF-8 -*-
import requests
from zlapi.models import Message
from dotenv import load_dotenv
import os
import yt_dlp
import re

# Load biến môi trường từ file .env
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v="

def search_youtube(track_name):
    params = {
        "part": "snippet",
        "q": track_name,
        "type": "video",
        "maxResults": 1,
        "key": YOUTUBE_API_KEY
    }
    try:
        resp = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)
        data = resp.json()
        items = data.get("items")
        if not items:
            return None

        video = items[0]
        video_id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        thumbnail = video["snippet"]["thumbnails"]["high"]["url"]

        return {
            "title": title,
            "thumbnail": thumbnail,
            "url": YOUTUBE_VIDEO_URL + video_id
        }
    except Exception as e:
        print("Lỗi search YouTube:", e)
        return None


def download_mp3(youtube_url, out_file_without_ext):
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": out_file_without_ext,
        "quiet": True,
        "noplaylist": True,
        # Cấu hình để tránh lỗi SABR và JavaScript runtime
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])


def handle_nhac_command(message, message_object, thread_id, thread_type, author_id, client):
    content = message.strip().split()
    if len(content) < 2:
        client.replyMessage(
            Message(text="Nhập tên bài hát đi. VD: nhạc Obito - Buồn Hay Vui 😉"),
            message_object, thread_id, thread_type
        )
        return

    track_name = " ".join(content[1:])
    client.replyMessage(Message(text=f"Đang tải: {track_name}... 🎧"), message_object, thread_id, thread_type)

    track = search_youtube(track_name)
    if not track:
        client.replyMessage(Message(text="Không tìm thấy bài hát này trên YouTube!"), message_object, thread_id, thread_type)
        return

    title = track["title"]
    youtube_url = track["url"]
    thumbnail = track["thumbnail"]

    # Tạo đường dẫn tuyệt đối để tránh lỗi "No connection adapters"
    file_name = f"temp_{author_id}"
    mp3_file = os.path.abspath(f"{file_name}.mp3")
    cover_file = os.path.abspath(f"thumb_{author_id}.jpg")

    try:
        # Tải nhạc
        download_mp3(youtube_url, file_name)
        
        # Gửi ảnh cover và thông tin bài hát
        msg = Message(text=f"🎵 {title}\n🔗 {youtube_url}")
        if thumbnail:
            try:
                img_data = requests.get(thumbnail).content
                with open(cover_file, "wb") as f:
                    f.write(img_data)
                client.sendLocalImage(cover_file, thread_id, thread_type, message=msg)
            except:
                client.replyMessage(msg, message_object, thread_id, thread_type)
        else:
            client.replyMessage(msg, message_object, thread_id, thread_type)

        # Gửi file nhạc bằng sendRemoteVoice (Sử dụng đường dẫn tuyệt đối)
        if os.path.exists(mp3_file):
            client.sendRemoteVoice(mp3_file, thread_id=thread_id, thread_type=thread_type)
        else:
            client.replyMessage(Message(text="Lỗi: Không tìm thấy file âm thanh!"), message_object, thread_id, thread_type)

    except Exception as e:
        print(f"Lỗi xử lý nhạc: {e}")
        client.replyMessage(Message(text=f"Có lỗi xảy ra: {str(e)}"), message_object, thread_id, thread_type)
    
    finally:
        # Xóa file tạm
        if os.path.exists(mp3_file):
            os.remove(mp3_file)
        if os.path.exists(cover_file):
            os.remove(cover_file)


def get_hzlbot():
    return {
        "nhạc": handle_nhac_command
    }