import json
import time
import urllib.parse

from zlapi.models import Message
from zlapi._threads import ThreadType

# ================== INFO ==================
des = {
    "version": "4.1.1",
    "credits": "Nguyen Hoang Dev ✓",
    "description": "Tạo sticker từ ảnh / gif / video Zalo (FIX zlapi bug)",
    "power": "Thành viên"
}

# ================== UTILS ==================
def fix_zalo_jxl_url(url: str):
    if not url:
        return None
    return (
        url.replace("/jxl/", "/jpg/")
           .replace(".jxl", ".jpg")
    )


def detect_media_type(url: str):
    url = url.lower()
    if url.endswith(".gif"):
        return "gif"
    if any(url.endswith(x) for x in (".jpg", ".jpeg", ".png", ".webp")):
        return "image"
    return "video"


def extract_zalo_media(message_object):
    # reply
    if message_object.quote and message_object.quote.get("attach"):
        attach = json.loads(message_object.quote["attach"])
        media = attach.get("href")
        thumb = attach.get("thumb") or media
        return (
            fix_zalo_jxl_url(urllib.parse.unquote(media)),
            fix_zalo_jxl_url(urllib.parse.unquote(thumb))
        )

    # direct photo/video
    content = message_object.content or {}
    if isinstance(content, dict):
        media = content.get("href")
        thumb = content.get("thumb") or media
        return (
            fix_zalo_jxl_url(urllib.parse.unquote(media)),
            fix_zalo_jxl_url(urllib.parse.unquote(thumb))
        )

    return None, None


# ================== COMMAND ==================
def handle_stk_command(message, message_object, thread_id, thread_type, author_id, client):

    media_url, thumb_url = extract_zalo_media(message_object)

    if not media_url:
        client.replyMessage(
            Message(text="❌ Reply ảnh / gif / video rồi gõ ?stk"),
            message_object,
            thread_id,
            thread_type
        )
        return

    client.replyMessage(
        Message(text="⏳ Đang tạo sticker..."),
        message_object,
        thread_id,
        thread_type
    )

    try:
        cid = int(time.time())

        client.send_custom_sticker(
            staticImgUrl=thumb_url or media_url,
            animationImgUrl=media_url,
            thread_id=thread_id,
            thread_type=thread_type,
            reply=message_object.msgId,
            ##width=512,
            ##height=512,
            contentId=cid
        )

    except Exception as e:
        # 🔥 FIX zlapi Response.get BUG
        if "Response" in str(e):
            return
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
