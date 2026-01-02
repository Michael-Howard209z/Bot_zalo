import requests
import subprocess
import json
import urllib.parse
import os
import time
import random
from PIL import Image, ImageDraw
from zlapi.models import Message
from zlapi._threads import ThreadType

des = {
    'version': "2.1.0",
    'credits': "Bot Zalo Nguyen Hoang Dev ✓",
    'description': "Tạo sticker từ ảnh / GIF / video",
    'power': "Thành viên"
}

# ================== CHECK FFMPEG ==================
def check_ffmpeg():
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except:
        return False


# ================== FILE TYPE ==================
def get_file_type(url):
    try:
        r = requests.get(url, stream=True, timeout=8, headers={
            "User-Agent": "Mozilla/5.0"
        })
        ct = r.headers.get("Content-Type", "").lower()
        if "image" in ct:
            return "image"
        if "video" in ct:
            return "video"
    except:
        pass
    return "unknown"


# ================== UPLOAD ==================
def upload_to_uguu(file_path):
    try:
        with open(file_path, "rb") as f:
            r = requests.post(
                "https://uguu.se/upload",
                files={"files[]": f},
                timeout=15
            )
        return r.json()["files"][0]["url"]
    except:
        return None


# ================== CONVERT ==================
def convert_media_and_upload(media_url, file_type, uid):
    base = os.path.join(os.path.dirname(__file__), "cache", "temp")
    os.makedirs(base, exist_ok=True)

    input_file = os.path.join(base, f"input_{uid}")
    output_webp = os.path.join(base, f"sticker_{uid}.webp")

    try:
        # download
        r = requests.get(media_url, stream=True, timeout=15)
        r.raise_for_status()
        with open(input_file, "wb") as f:
            for c in r.iter_content(8192):
                f.write(c)

        # IMAGE
        if file_type == "image":
            with Image.open(input_file).convert("RGBA") as img:
                img.thumbnail((512, 512), Image.Resampling.LANCZOS)

                w, h = img.size
                mask = Image.new("L", (w, h), 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle((0, 0, w, h), 60, fill=255)

                img.putalpha(mask)
                img.save(output_webp, "WEBP", quality=85, method=6)

        # VIDEO / GIF
        else:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", input_file,
                "-vf", "scale=512:-1:flags=lanczos,fps=15",
                "-t", "6",
                "-loop", "0",
                "-an",
                "-c:v", "libwebp",
                "-lossless", "0",
                "-q:v", "80",
                "-loglevel", "error",
                output_webp
            ], check=True)

        return upload_to_uguu(output_webp)

    finally:
        for f in (input_file, output_webp):
            if os.path.exists(f):
                os.remove(f)


# ================== COMMAND ==================
def handle_stk_command(message, message_object, thread_id, thread_type, author_id, client):

    if not check_ffmpeg():
        client.replyMessage(
            Message(text="❌ FFmpeg chưa được cài trên server."),
            message_object, thread_id, thread_type
        )
        return

    if not message_object.quote or not message_object.quote.attach:
        client.replyMessage(
            Message(text="➜ Reply vào ảnh / GIF / video để tạo sticker."),
            message_object, thread_id, thread_type
        )
        return

    try:
        attach = json.loads(message_object.quote.attach)
    except:
        client.replyMessage(
            Message(text="❌ Không đọc được dữ liệu đính kèm."),
            message_object, thread_id, thread_type
        )
        return

    media_url = attach.get("hdUrl") or attach.get("href")
    if not media_url:
        client.replyMessage(
            Message(text="❌ Không tìm thấy media."),
            message_object, thread_id, thread_type
        )
        return

    media_url = urllib.parse.unquote(media_url.replace("\\/", "/"))
    media_url = media_url.replace(".jxl", ".jpg")

    file_type = get_file_type(media_url)
    if file_type not in ("image", "video"):
        client.replyMessage(
            Message(text="❌ File không hỗ trợ."),
            message_object, thread_id, thread_type
        )
        return

    client.replyMessage(
        Message(text="⏳ Đang tạo sticker..."),
        message_object, thread_id, thread_type
    )

    try:
        uid = f"{thread_id}_{int(time.time())}_{random.randint(1000,9999)}"
        webp_url = convert_media_and_upload(media_url, file_type, uid)

        if not webp_url:
            raise Exception("Upload thất bại")

        # gửi sticker
        if hasattr(client, "sendCustomSticker"):
            client.sendCustomSticker(
                animationImgUrl=webp_url,
                staticImgUrl=webp_url,
                width=512,
                height=512,
                thread_id=thread_id,
                thread_type=thread_type
            )
        else:
            client.sendImage(webp_url, thread_id, thread_type)

    except Exception as e:
        client.replyMessage(
            Message(text=f"❌ Lỗi tạo sticker: {e}"),
            message_object, thread_id, thread_type
        )


# ================== REGISTER ==================
def get_hzlbot():
    return {
        "stk": handle_stk_command
    }
