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

# ================== INFO ==================
des = {
    "version": "2.3.0",
    "credits": "Bot Zalo Nguyen Hoang Dev ✓",
    "description": "Tạo sticker từ ảnh Zalo / GIF / video (FIX JXL)",
    "power": "Thành viên"
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


# ================== FIX URL JXL -> JPG (RẤT QUAN TRỌNG) ==================
def fix_zalo_jxl_url(url: str) -> str:
    if not url:
        return url

    # đổi thư mục jxl -> jpg
    url = url.replace("/jxl/", "/jpg/")

    # đổi đuôi .jxl -> .jpg
    if url.endswith(".jxl"):
        url = url[:-4] + ".jpg"

    return url


# ================== EXTRACT MEDIA URL ==================
def extract_zalo_media_url(message_object):
    """
    Hỗ trợ:
    - Reply ảnh / video / gif
    - Ảnh Zalo chat.photo
    """

    # 1. Reply media
    if message_object.quote and message_object.quote.attach not in (None, "{}"):
        try:
            attach = json.loads(message_object.quote.attach)
            url = attach.get("hdUrl") or attach.get("href")
            return fix_zalo_jxl_url(url)
        except:
            pass

    # 2. Ảnh Zalo (chat.photo)
    if message_object.msgType == "chat.photo":
        content = message_object.content or {}

        # ưu tiên HD trong params
        params = content.get("params")
        if params:
            try:
                p = json.loads(params)
                if "hd" in p:
                    return fix_zalo_jxl_url(
                        p["hd"].replace("\\/", "/")
                    )
            except:
                pass

        return fix_zalo_jxl_url(
            content.get("href") or content.get("thumb")
        )

    return None


# ================== FILE TYPE ==================
def get_file_type(url):
    u = url.lower()

    if any(x in u for x in (".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return "image"
    if any(x in u for x in (".mp4", ".mov", ".webm", ".mkv")):
        return "video"

    try:
        r = requests.get(url, stream=True, timeout=8)
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


# ================== CONVERT MEDIA ==================
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
            try:
                with Image.open(input_file).convert("RGBA") as img:
                    img.thumbnail((512, 512), Image.Resampling.LANCZOS)

                    w, h = img.size
                    mask = Image.new("L", (w, h), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.rounded_rectangle(
                        (0, 0, w, h),
                        radius=60,
                        fill=255
                    )

                    img.putalpha(mask)
                    img.save(
                        output_webp,
                        "WEBP",
                        quality=85,
                        method=6
                    )
            except Exception:
                # PIL mở không được -> fallback sang video
                file_type = "video"

        # VIDEO / GIF
        if file_type == "video":
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


# ================== COMMAND /stk ==================
def handle_stk_command(message, message_object, thread_id, thread_type, author_id, client):

    if not check_ffmpeg():
        client.replyMessage(
            Message(text="❌ Server chưa cài FFmpeg."),
            message_object, thread_id, thread_type
        )
        return

    media_url = extract_zalo_media_url(message_object)
    if not media_url:
        client.replyMessage(
            Message(text="❌ Vui lòng reply vào ảnh / video hợp lệ."),
            message_object, thread_id, thread_type
        )
        return

    media_url = urllib.parse.unquote(media_url)

    file_type = get_file_type(media_url)
    if file_type == "unknown":
        client.replyMessage(
            Message(text="❌ Không xác định được loại media."),
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
