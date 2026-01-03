import json
import urllib.parse
import time
from zlapi.models import Message
from zlapi._threads import ThreadType

# ================== INFO ==================
des = {
    "version": "3.2.0",
    "credits": "Bot Zalo Nguyen Hoang Dev ✓",
    "description": "Tạo sticker từ ảnh / gif Zalo (custom sticker)",
    "power": "Thành viên"
}

# ================== FIX JXL -> JPG ==================
def fix_zalo_jxl_url(url: str):
    if not url:
        return None
    url = url.replace("/jxl/", "/jpg/")
    if url.endswith(".jxl"):
        url = url[:-4] + ".jpg"
    return url


# ================== CHECK GIF ==================
def is_gif(url: str) -> bool:
    return url.lower().endswith(".gif")


# ================== EXTRACT IMAGE URL ==================
def extract_zalo_image_url(message_object):

    # Reply ảnh
    if message_object.quote and message_object.quote.get("attach"):
        try:
            attach = json.loads(message_object.quote["attach"])
            url = (
                attach.get("href")
                or attach.get("hd")
                or attach.get("hdUrl")
            )
            return url
        except:
            pass

    # chat.photo
    if message_object.msgType == "chat.photo":
        content = message_object.content or {}

        params = content.get("params")
        if params:
            try:
                p = json.loads(params)
                if "hd" in p:
                    return p["hd"].replace("\\/", "/")
            except:
                pass

        return content.get("href") or content.get("thumb")

    return None


# ================== COMMAND /stk ==================
def handle_stk_command(message, message_object, thread_id, thread_type, author_id, client):

    image_url = extract_zalo_image_url(message_object)
    if not image_url:
        client.replyMessage(
            Message(text="❌ Reply vào ảnh hoặc GIF Zalo rồi gõ /stk"),
            message_object,
            thread_id,
            thread_type
        )
        return

    image_url = urllib.parse.unquote(image_url)

    # Fix JXL nếu không phải GIF
    if not is_gif(image_url):
        image_url = fix_zalo_jxl_url(image_url)

    client.replyMessage(
        Message(text="⏳ Đang tạo sticker..."),
        message_object,
        thread_id,
        thread_type
    )

    content_id = int(time.time())

    # ====== GIF STICKER ======
    if is_gif(image_url):
        client.send_custom_sticker(
            animationImgUrl=image_url,
            thread_id=thread_id,
            thread_type=thread_type,
            reply=message_object.msgId,
            contentId=content_id
        )
        return

    # ====== STATIC STICKER ======
    client.send_custom_sticker(
        staticImgUrl=image_url,
        thread_id=thread_id,
        thread_type=thread_type,
        reply=message_object.msgId,
        contentId=content_id
    )


# ================== REGISTER ==================
def get_hzlbot():
    return {
        "stk": handle_stk_command
    }
