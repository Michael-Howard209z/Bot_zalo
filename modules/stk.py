import json
import urllib.parse
import time
from zlapi.models import Message
from zlapi._threads import ThreadType

# ================== INFO ==================
des = {
    "version": "3.1.0",
    "credits": "Bot Zalo Nguyen Hoang Dev ✓",
    "description": "Tạo sticker từ ảnh Zalo (custom sticker)",
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


# ================== EXTRACT IMAGE URL ==================
def extract_zalo_image_url(message_object):

    # Reply ảnh
    if message_object.quote and message_object.quote.attach:
        try:
            attach = json.loads(message_object.quote.attach)
            url = attach.get("href") or attach.get("hd") or attach.get("hdUrl")
            return fix_zalo_jxl_url(url)
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
                    return fix_zalo_jxl_url(
                        p["hd"].replace("\\/", "/")
                    )
            except:
                pass

        return fix_zalo_jxl_url(
            content.get("href") or content.get("thumb")
        )

    return None


# ================== COMMAND /stk ==================
def handle_stk_command(message, message_object, thread_id, thread_type, author_id, client):

    image_url = extract_zalo_image_url(message_object)
    if not image_url:
        client.replyMessage(
            Message(text="❌ Reply vào ảnh Zalo rồi gõ /stk"),
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
        client.send_custom_sticker(
            staticImgUrl=image_url,
            animationImgUrl=image_url,
            thread_id=thread_id,
            thread_type=thread_type,
            reply=message_object.msgId,
            ##width=512,
           ## height=512,
            contentId=int(time.time())
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
