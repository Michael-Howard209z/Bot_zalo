import subprocess
import json
import urllib.parse
import os
import time
import random
import requests
from PIL import Image
from zlapi.models import Message
from zlapi._threads import ThreadType

# ================== INFO ==================
des = {
    "version": "3.0.0",
    "credits": "Bot Zalo Nguyen Hoang Dev ✓",
    "description": "Tạo sticker từ ảnh JPG Zalo (sendSticker)",
    "power": "Thành viên"
}

# ================== FIX URL JXL -> JPG ==================
def fix_zalo_jxl_url(url: str) -> str:
    if not url:
        return None
    url = url.replace("/jxl/", "/jpg/")
    if url.endswith(".jxl"):
        url = url[:-4] + ".jpg"
    return url


# ================== EXTRACT IMAGE URL ==================
def extract_zalo_image_url(message_object):
    """
    Chỉ xử lý ẢNH JPG Zalo
    """

    # 1. Reply ảnh
    if message_object.quote and message_object.quote.get("attach"):
        try:
            attach = json.loads(message_object.quote["attach"])
            url = attach.get("href") or attach.get("hd")
            return fix_zalo_jxl_url(url)
        except:
            pass

    # 2. chat.photo
    if message_object.msgType == "chat.photo":
        content = message_object.content or {}

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


# ================== DOWNLOAD IMAGE ==================
def download_image(url, save_path):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(r.content)


# ================== RESIZE TO STICKER ==================
def make_sticker(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    img.thumbnail((128, 64), Image.LANCZOS)

    canvas = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    x = (128 - img.width) // 2
    y = (64 - img.height) // 2
    canvas.paste(img, (x, y), img)

    canvas.save(output_path, "PNG")


# ================== COMMAND /stk ==================
def handle_stk_command(message, message_object, thread_id, thread_type, author_id, client):

    image_url = extract_zalo_image_url(message_object)
    if not image_url or not image_url.endswith(".jpg"):
        client.replyMessage(
            Message(text="❌ Vui lòng reply ảnh JPG Zalo."),
            message_object,
            thread_id,
            thread_type
        )
        return

    image_url = urllib.parse.unquote(image_url)

    client.replyMessage(
        Message(text="⏳ Đang tạo sticker..."),
        message_object,
        thread_id,
        thread_type
    )

    try:
        base_dir = os.path.join(os.path.dirname(__file__), "sticker")
        os.makedirs(base_dir, exist_ok=True)

        uid = f"{thread_id}_{int(time.time())}_{random.randint(1000,9999)}"
        raw_path = os.path.join(base_dir, f"raw_{uid}.jpg")
        sticker_path = os.path.join(base_dir, f"stk_{uid}.png")

        # tải ảnh
        download_image(image_url, raw_path)

        # resize
        make_sticker(raw_path, sticker_path)

        # gửi sticker
        client.sendSticker(
            imagePath=sticker_path,
            thread_id=thread_id,
            thread_type=thread_type,
            width=128,
            height=64,
            ## message=Message(text="✨ Sticker đây!")
        )

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
