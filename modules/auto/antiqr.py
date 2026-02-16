import json
import os
import requests
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
from config import ADMIN
from zlapi.models import Message, ThreadType

# ================== INFO ==================
des = {
    'version': "1.0.0",
    'credits': "Gemini Code Assist",
    'description': "Chống gửi ảnh chứa mã QR trong nhóm."
}

# ================== CONFIG ==================
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'antiqr_config.json')

# ================== HELPER FUNCTIONS ==================
def load_config():
    """Tải cấu hình từ file JSON"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config):
    """Lưu cấu hình vào file JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ANTIQR] Lỗi khi lưu config: {e}")

def get_group_settings(thread_id):
    """Lấy cài đặt của nhóm"""
    config = load_config()
    return config.get(str(thread_id), {'status': False})

def set_group_settings(thread_id, settings):
    """Cập nhật cài đặt của nhóm"""
    config = load_config()
    config[str(thread_id)] = settings
    save_config(config)

#def is_admin(author_id):
    """Kiểm tra xem user có phải admin không"""
 #   return str(author_id) in map(str, ADMIN)

def has_qr_code(image_bytes):
    """Kiểm tra xem ảnh có chứa mã QR không"""
    try:
        image = Image.open(BytesIO(image_bytes))
        # Chuyển sang ảnh xám để tăng độ chính xác
        image = image.convert('L')
        decoded_objects = decode(image)
        return len(decoded_objects) > 0
    except Exception as e:
        print(f"[ANTIQR] Lỗi khi phân tích ảnh: {e}")
        return False

# ================== MAIN HANDLER ==================
def handle_antiqr(message, message_object, thread_id, thread_type, author_id, client):
    try:
        if thread_type != ThreadType.GROUP:
            return

        settings = get_group_settings(thread_id)
        if not settings.get('status', False):
            return

        # Bỏ qua tin nhắn của admin hoặc của chính bot
        #if is_admin(author_id) or str(author_id) == str(client.uid):
            #if str(author_id) == str(client.uid):
                # Ghi log khi bot bỏ qua tin nhắn của chính nó
                #print(f"[ANTIQR] Bỏ qua tin nhắn từ chính bot (ID: {author_id}).")
          #  return

        image_url = None

        # Trường hợp 1: Tin nhắn là ảnh gửi trực tiếp (dựa trên log bạn cung cấp)
        if message_object.msgType == "chat.photo":
            if hasattr(message_object, 'content') and isinstance(message_object.content, dict):
                # Lấy URL từ 'href' làm phương án dự phòng
                image_url = message_object.content.get('href')
                
                # Thử lấy link chất lượng cao (HD) từ 'params' nếu có
                params_str = message_object.content.get('params')
                if params_str:
                    try:
                        if isinstance(params_str, dict):
                            params_dict = params_str
                        else:
                            params_dict = json.loads(params_str)
                        hd_url = params_dict.get('hd')
                        if hd_url:
                            image_url = hd_url # Ưu tiên link HD
                    except Exception:
                        pass # Bỏ qua nếu params không hợp lệ
        
        # Trường hợp 2: Tin nhắn có đính kèm (ví dụ: ảnh được forward)
        elif hasattr(message_object, 'attachments') and message_object.attachments:
            for attachment in message_object.attachments:
                if attachment.get('type') == 'photo' and attachment.get('photo'):
                    photo_data = attachment.get('photo')
                    image_url = photo_data.get('largeUrl') or photo_data.get('url') or photo_data.get('previewUrl')
                    if image_url:
                        break

        if not image_url:
            return

        # Thêm User-Agent để tránh bị chặn bởi Zalo CDN
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()

        if has_qr_code(response.content):
            print(f"[ANTIQR] Phát hiện mã QR từ user {author_id} trong nhóm {thread_id}.")
            if hasattr(message_object, 'msgId') and hasattr(message_object, 'cliMsgId'):
                client.deleteGroupMsg(msgId=message_object.msgId, ownerId=author_id, clientMsgId=message_object.cliMsgId, groupId=thread_id)
                print(f"[ANTIQR] Đã xóa tin nhắn chứa mã QR.")

    except Exception as e:
        print(f"[ANTIQR] Lỗi trong handle_antiqr: {e}")

# ================== EXPORT ==================
def get_global_hzlbot():
    """Trả về danh sách các hàm xử lý event toàn cục"""
    return [handle_antiqr]

def get_hzlbot():
    return {}