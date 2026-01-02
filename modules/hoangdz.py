import google.generativeai as genai
from zlapi import ZaloAPI, ZaloAPIException
from zlapi.models import *

# Cấu hình Gemini API KEY
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# Model bạn muốn dùng (có thể đổi sang gemini-1.5-pro)
model = genai.GenerativeModel("gemini-1.5-flash")


def nhan_tin(self, mid, author_id, message, message_object, thread_id, thread_type):
    # Không rep tin nhắn của chính bot
    if author_id == self.uid:
        return

    print(f"[{mid}] {author_id}: {message}")

    msg = message.lower()

    # Rule đặc biệt cho "Châu"
    if "châu" in msg:
        return self.send_text("Châu xinh gái vcl, chúc Châu ngủ ngol", thread_id, thread_type)

    # ----- AI REPLY BẰNG GEMINI -----
    try:
        response = model.generate_content(f"""
        Người dùng nói: "{message}"
        Hãy trả lời ngắn gọn, tự nhiên, thân thiện.
        """)
        reply_text = response.text.strip()
    except Exception as e:
        reply_text = f"AI lỗi rồi: {e}"

    # Gửi trả lời vào Zalo
    self.send_text(reply_text, thread_id, thread_type)


def get_hzlbot():
    return {
        'hoangdz': nhan_tin
    }
