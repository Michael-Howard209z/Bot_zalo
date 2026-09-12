import json
import os
import re
import time
import textwrap
from urllib.parse import urlparse
from config import ADMIN
from zlapi.models import Message
from zlapi.models import Message, MultiMsgStyle, MessageStyle
from zlapi._threads import ThreadType

# ================== INFO ==================
des = {
    'version': "3.1.0",
    'credits': "Nguyen Hoang",
    'description': "Chống gửi link trong nhóm (Fix Whitelist)"
}
# 1486999657390250587
# ================== CONFIG ==================
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'antilink_config.json')

# ================== HELPER FUNCTIONS ==================
def load_config():
    """Tải cấu hình từ file JSON"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ANTILINK] Lỗi khi tải config: {e}")
        return {}

def save_config(config):
    """Lưu cấu hình vào file JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ANTILINK] Lỗi khi lưu config: {e}")

def get_group_settings(thread_id):
    """Lấy cài đặt của nhóm"""
    config = load_config()
    return config.get(str(thread_id), {
        'status': False,
        'whitelist': [],
        'delete_msg': True,
        'warn_user': True,
        'block_user': False
    })

def set_group_settings(thread_id, settings):
    """Cập nhật cài đặt của nhóm"""
    config = load_config()
    config[str(thread_id)] = settings
    save_config(config)

def is_admin(author_id):
    """Kiểm tra xem user có phải admin không"""
    return str(author_id) in map(str, ADMIN)

def is_whitelisted_url(url, whitelist):
    """Kiểm tra URL có trong danh sách trắng không (so sánh domain)"""
    if not whitelist:
        return False
    
    def get_domain(u):
        try:
            # Thêm http nếu chưa có để urlparse hoạt động đúng với netloc
            if not u.startswith(('http://', 'https://')):
                u = 'http://' + u
            
            parsed = urlparse(u)
            domain = parsed.netloc.lower()
            
            # Loại bỏ www.
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Loại bỏ port nếu có (vd: domain.com:8080)
            if ':' in domain:
                domain = domain.split(':')[0]
                
            return domain.strip()
        except:
            return ""

    target_domain = get_domain(url)
    if not target_domain:
        return False
        
    for w in whitelist:
        whitelisted_domain = get_domain(w)
        if whitelisted_domain and whitelisted_domain == target_domain:
            return True
            
    return False

def extract_urls(content):
    """Trích xuất tất cả URLs từ nội dung tin nhắn"""
    if not content:
        return []
    
    # Pattern cải tiến để tìm URLs
    patterns = [
        # Bắt http/https URLs
        r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*',
        
        # Bắt www.
        r'www\.(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*',
        
        # Bắt domain.tld (phải có ít nhất 1 dấu chấm ở giữa và không bắt tld đứng một mình)
        # vd: google.com -> ok, com -> sai
        r'\b(?:[a-zA-Z0-9-]+\.)+(com|net|org|vn|edu|gov|io|co|me|info|biz)\b(?:/[^\s]*)?'
    ]
    
    urls = []
    for pattern in patterns:
        found = re.findall(pattern, content, re.IGNORECASE)
        urls.extend(found)
    
    # Loại bỏ các kết quả không phải URL hợp lệ (nếu cần)
    valid_urls = []
    for u in urls:
        # Kiểm tra sơ bộ độ dài và cấu trúc
        if len(u) > 3 and '.' in u:
             valid_urls.append(u)
             
    # Loại bỏ trùng lặp
    return list(set(valid_urls))

def to_pixel(text):
    """Chuyển đổi văn bản sang font pixel (Monospace Unicode)"""
    result = ""
    for char in text:
        if 'A' <= char <= 'Z':
            result += chr(ord(char) + 120367)
        elif 'a' <= char <= 'z':
            result += chr(ord(char) + 120361)
        elif '0' <= char <= '9':
            result += chr(ord(char) + 120774)
        else:
            result += char
    return result

# ================== MAIN HANDLER ==================
def handle_antilink(message, message_object, thread_id, thread_type, author_id, client):
    """
    Xử lý chống link - Tự động xóa tin nhắn chứa link không được phép
    """
    try:
        # Chỉ xử lý trong nhóm
        if thread_type != ThreadType.GROUP:
            return
        
        # Kiểm tra message_object hợp lệ
        if not message_object or not hasattr(message_object, 'msgType'):
            return
        
        # Lấy cài đặt nhóm
        settings = get_group_settings(thread_id)
        
        # Kiểm tra xem antilink có bật không
        if not settings.get('status', False):
            return
        
        # Bỏ qua tin nhắn của bot
        if str(author_id) == str(client.uid):
            return
        
        # Admin không bị check
        if is_admin(author_id):
            return
        
        # Lấy nội dung tin nhắn
        content = ""
        
        # Xử lý các loại tin nhắn khác nhau
        if message_object.msgType == "webchat":
            # Tin nhắn text thường
            content = message or ""
        elif message_object.msgType == "chat.recommended":
            # Tin nhắn link preview
            if hasattr(message_object, 'content') and isinstance(message_object.content, dict):
                # Lấy URL từ title hoặc href
                content = message_object.content.get('title', '') + ' ' + message_object.content.get('href', '')
                print(f"[ANTILINK] Phát hiện link preview: {content}")
        else:
            # Bỏ qua các loại tin nhắn khác
            return
        
        # Tìm URLs trong tin nhắn
        urls = extract_urls(content)
        if not urls:
            return
        
        # Lấy whitelist
        whitelist = settings.get('whitelist', [])
        
        # Kiểm tra từng URL
        blocked_urls = []
        for url in urls:
            if not is_whitelisted_url(url, whitelist):
                blocked_urls.append(url)
        
        # Nếu có link bị chặn
        if blocked_urls:
            # Xóa tin nhắn nếu được bật
            if settings.get('delete_msg', True):
                try:
                    # Kiểm tra các thuộc tính cần thiết
                    if hasattr(message_object, 'msgId') and hasattr(message_object, 'cliMsgId'):
                        client.deleteGroupMsg(
                            msgId=message_object.msgId,
                            ownerId=author_id,
                            clientMsgId=message_object.cliMsgId,
                            groupId=thread_id
                        )
                        print(f"[ANTILINK] Đã xóa tin nhắn chứa link từ {author_id} trong nhóm {thread_id}")
                    else:
                        print(f"[ANTILINK] Không thể xóa tin nhắn: thiếu msgId hoặc cliMsgId")
                except Exception as e:
                    print(f"[ANTILINK] Lỗi khi xóa tin nhắn: {e}")
            
            # Block user nếu được bật
            if settings.get('block_user', False):
                try:
                    client.blockUsersInGroup(author_id, thread_id)
                    print(f"[ANTILINK] Đã BLOCK user {author_id} khỏi nhóm {thread_id}")
                    client.send(
                        Message(text=f"🚫 Đã chặn thành viên {author_id} khỏi nhóm vì gửi link cấm!"),
                        thread_id, thread_type
                    )
                except Exception as e:
                    print(f"[ANTILINK] Lỗi khi block user: {e}")

            # Gửi cảnh báo nếu được bật
            if settings.get('warn_user', True):
                try:
                    raw_text = "CẢNH BÁO \nPhát hiện gửi link cấm!\nVui lòng đọc kỹ nội quy nhóm."
                    warning_text = to_pixel(raw_text)
                    
                    # Sử dụng font pixel unicode và màu đỏ
                    style = MultiMsgStyle([
                        MessageStyle(offset=0, length=len(warning_text), style="font", size="50", auto_format=False),
                        MessageStyle(offset=0, length=len(warning_text), style="color", color="#ff0000", auto_format=False)
                    ])
                    client.send(Message(text=warning_text, style=style), thread_id, thread_type)

                except Exception as e:
                    print(f"[ANTILINK] Lỗi khi gửi cảnh báo: {e}")
    
    except Exception as e:
        print(f"[ANTILINK] Lỗi trong handle_antilink: {e}")
        import traceback
        traceback.print_exc()

# ================== EXPORT ==================
def get_global_hzlbot():
    """Trả về danh sách các hàm xử lý event"""
    return [handle_antilink]

# ================== UTILITIES (Dùng cho command) ==================
def toggle_antilink(thread_id, status):
    """Bật/tắt antilink cho nhóm"""
    settings = get_group_settings(thread_id)
    settings['status'] = status
    set_group_settings(thread_id, settings)
    return f" Đã {'bật' if status else 'tắt'} antilink cho nhóm {thread_id}"

def toggle_block_user(thread_id, status):
    """Bật/tắt tính năng tự động block"""
    settings = get_group_settings(thread_id)
    settings['block_user'] = status
    set_group_settings(thread_id, settings)
    return f" Đã {'bật' if status else 'tắt'} tính năng tự động BLOCK user gửi link cho nhóm {thread_id}"

def add_to_whitelist(thread_id, domain):
    """Thêm domain vào whitelist"""
    settings = get_group_settings(thread_id)
    if domain not in settings.get('whitelist', []):
        if 'whitelist' not in settings:
            settings['whitelist'] = []
        settings['whitelist'].append(domain)
        set_group_settings(thread_id, settings)
        return f" Đã thêm '{domain}' vào whitelist"
    return f" '{domain}' đã có trong whitelist"

def remove_from_whitelist(thread_id, domain):
    """Xóa domain khỏi whitelist"""
    settings = get_group_settings(thread_id)
    if 'whitelist' in settings and domain in settings['whitelist']:
        settings['whitelist'].remove(domain)
        set_group_settings(thread_id, settings)
        return f" Đã xóa '{domain}' khỏi whitelist"
    return f" '{domain}' không có trong whitelist"

def get_whitelist(thread_id):
    """Lấy danh sách whitelist của nhóm"""
    settings = get_group_settings(thread_id)
    return settings.get('whitelist', [])