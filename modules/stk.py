import os
import json
import time
import subprocess
import urllib.parse
import requests

from zlapi.models import Message
from zlapi._threads import ThreadType

# ================== CONFIG ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "sticker_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

MAX_GIF_DURATION = 5     # giây
GIF_SIZE = 512           # px

# ================== INFO ==================
des = {
    "version": "4.0.0",
    "credits": "Nguyen Hoang Dev ✓",
    "description": "Tạo sticker từ ảnh / gif / video Zalo",
    "power": "Thành viên"
}

# ================== UTILS ==================
def fix_zalo_jxl_url(url: str):
    if not url:
        return None
    url = url.replace("/jxl/", "/jpg/")
    if url.endswith(".jxl"):
        url = url[:-4] + ".jpg"
    return url


def detect_media_type(url: str):
    url = url.lower()
    if url.endswith(".gif"):
        return "gif"
    if any(url.endswith(x) for x in [".jpg", ".jpeg", ".png", ".webp"]):
        return "image"
    return "video"


def extract_zalo_media(message_object):
    # reply media
    if message_object.quote and message_object.quote.get("attach"):
        try:
            attach = json.loads(message_object.quote["attach"])
            return urllib.parse.unquote(attach.get("href"))
        except:
            pass

    # chat.photo / chat.video.msg
    content = message_object.content or {}
    if isinstance(content, dict):
        return urllib.parse.unquote(content.get("href"))

    return None


def download_file(url, out_path):
    r = requests.get(url, stream=True, timeout=15)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)


def video_to_gif(video_path, gif_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-t", str(MAX_GIF_DURATION),
        "-i", video_path,
        "-vf", f"scale={GIF_SIZE}:{GIF_SIZE}:force_original_aspect_ratio=decrease",
        "-r", "12",
        gif_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ================== COMMAND ==================
def handle_stk_command(message, message_object, thread_id, thread_type, author_id, client):

    media_url = extract_zalo_media(message_object)

    if not media_url:
        client.replyMessage(
            Message(text="❌ Reply ảnh / gif / video rồi gõ ?stk"),
            message_object,
            thread_id,
            thread_type
        )
        return

    media_url = fix_zalo_jxl_url(media_url)
    media_type = detect_media_type(media_url)

    client.replyMessage(
        Message(text="⏳ Đang tạo sticker..."),
        message_object,
        thread_id,
        thread_type
    )

    try:
        # ===== IMAGE =====
        if media_type == "image":
            client.send_custom_sticker(
                staticImgUrl=media_url,
                thread_id=thread_id,
                thread_type=thread_type,
                reply=message_object.msgId,
                width=GIF_SIZE,
                height=GIF_SIZE,
                contentId=int(time.time())
            )
            return

        # ===== GIF =====
        if media_type == "gif":
            client.send_custom_sticker(
                animationImgUrl=media_url,
                thread_id=thread_id,
                thread_type=thread_type,
                reply=message_object.msgId,
                width=GIF_SIZE,
                height=GIF_SIZE,
                contentId=int(time.time())
            )
            return

        # ===== VIDEO =====
        ts = int(time.time())
        video_path = os.path.join(CACHE_DIR, f"video_{ts}.mp4")
        gif_path = os.path.join(CACHE_DIR, f"gif_{ts}.gif")

        download_file(media_url, video_path)
        video_to_gif(video_path, gif_path)

        if not os.path.exists(gif_path):
            raise Exception("Không convert được video → gif")

        # upload local gif (Zalo tự nhận)
        client.send_custom_sticker(
            animationImgUrl=f"file:///{gif_path}",
            thread_id=thread_id,
            thread_type=thread_type,
            reply=message_object.msgId,
            width=GIF_SIZE,
            height=GIF_SIZE,
            contentId=ts
        )

        # cleanup
        os.remove(video_path)
        os.remove(gif_path)

    except Exception as e:
        client.replyMessage(
            Message(text=f"❌ Lỗi tạo sticker: {e}"),
            message_object,
            thread_id,
            thread_type
        )


# ================== REGISTER ==================
def get_hzlbot():
    return {
        "stk": handle_stk_command
    }
