# -*- coding: UTF-8 -*-
import requests
from zlapi.models import Message
from dotenv import load_dotenv
import os

# Load biến môi trường từ file .env
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v="

def search_youtube(track_name):
    """Tìm video trên YouTube bằng YouTube API"""
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
        video_url = YOUTUBE_VIDEO_URL + video_id
        return {
            "title": title,
            "thumbnail": thumbnail,
            "url": video_url
        }
    except Exception as e:
        print("Lỗi search YouTube:", e)
        return None

def handle_nhac_command(message, message_object, thread_id, thread_type, author_id, client):
    content = message.strip().split()
    if len(content) < 2:
        client.replyMessage(
            Message(text="Nhập tên bài hát đi. VD: nhạc Obito - Buồn Hay Vui 😉"),
            message_object, thread_id, thread_type
        )
        return

    track_name = " ".join(content[1:])
    client.replyMessage(Message(text="Đợi tao kiếm cái..."), message_object, thread_id, thread_type)

    track = search_youtube(track_name)
    if not track:
        client.replyMessage(Message(text="Không tìm thấy bài hát!"), message_object, thread_id, thread_type)
        return

    title = track["title"]
    audio_url = track["url"]
    thumbnail = track["thumbnail"]

    msg = Message(text=f"🎵 **{title}** 🎵")
    try:
        if thumbnail:
            img_data = requests.get(thumbnail).content
            cover_file = f"{title}.jpg"
            with open(cover_file, "wb") as f:
                f.write(img_data)
            client.sendLocalImage(cover_file, thread_id, thread_type, message=msg, width=240, height=240)
        else:
            client.replyMessage(msg, message_object, thread_id, thread_type)
    except:
        client.replyMessage(msg, message_object, thread_id, thread_type)

    client.sendRemoteVoice(audio_url, thread_id=thread_id, thread_type=thread_type, ttl=15000)

def get_hzlbot():
    return {
        "nhạc": handle_nhac_command
    }
