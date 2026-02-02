from config import API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES, PREFIX
from hzlbot import CommandHandler
from zlapi import ZaloAPI
from zlapi.models import Message
from modules.bot_info import *
# from modules.da import welcome

import itertools
import signal
import sys
import atexit
import os
import time
import threading
from colorama import Fore, Style, init

# ================== COLOR ==================
GRADIENT_COLORS = [
    Fore.LIGHTMAGENTA_EX,
    Fore.MAGENTA,
    Fore.LIGHTBLUE_EX,
    Fore.BLUE,
    Fore.CYAN,
    Fore.LIGHTCYAN_EX,
]

def gradient_text(text):
    color_cycle = itertools.cycle(GRADIENT_COLORS)
    result = ""
    for char in text:
        result += next(color_cycle) + Style.BRIGHT + char
    return result + Style.RESET_ALL

init(autoreset=True)

# ================== CLIENT ==================
class Client(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies):
        super().__init__(
            api_key,
            secret_key,
            imei=imei,
            session_cookies=session_cookies
        )
        handle_bot_admin(self)
        self.version = 1.1
        self.me_name = "Bot by NguyenHoangDev"
        self.date_update = "12/01/2025"
        self.command_handler = CommandHandler(self)

    def onEvent(self, event_data, event_type):
        try:
            welcome(self, event_data, event_type)
        except Exception as e:
            print(f"Lỗi event: {e}")

    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        print(
            f"∥{Fore.LIGHTGREEN_EX}{Style.BRIGHT}══════════════════════════════════════\n"
            f"∥Message: {message}\n"
            f"∥Author ID: {author_id}\n"
            f"∥Thread ID: {thread_id}\n"
            f"∥Thread Type: {thread_type}\n"
            f"∥Message Object: {message_object}\n"
            f"∥{Fore.LIGHTGREEN_EX}{Style.BRIGHT}══════════════════════════════════════\n"
        )

        try:
            allowed_thread_ids = get_allowed_thread_ids()
            if (
                thread_id in allowed_thread_ids
                and thread_type == ThreadType.GROUP
                and not is_admin(author_id)
            ):
                handle_check_profanity(
                    self, author_id, thread_id, message_object, thread_type, message
                )

            # Xử lý tin nhắn để chạy Command Handler
            # Nếu message không phải string (vd: link preview, sticker), gán là chuỗi rỗng để vẫn chạy được global handlers
            message_text = message if isinstance(message, str) else ""
            
            if message_text == PREFIX:
                self.send(
                    Message(text=f"Dùng {PREFIX}menu để biết rõ hơn"),
                    thread_id,
                    thread_type
                )
                return

            self.command_handler.handle_command(
                message_text,
                author_id,
                message_object,
                thread_id,
                thread_type
            )

        except KeyboardInterrupt:
            raise  # ⚠️ KHÔNG NUỐT CTRL+C
        except Exception as e:
            print(f"Lỗi xử lý tin nhắn: {e}")

# ================== CLEANUP ==================
def cleanup():
    print(f"\n{Fore.RED}{Style.BRIGHT}Bot đã dừng!{Style.RESET_ALL}")
    try:
        from zlapi._client import pool
        pool.shutdown(wait=False)
    except:
        pass

atexit.register(cleanup)

# ================== AUTO RESTART ==================
def auto_restart(interval_seconds):
    time.sleep(interval_seconds)
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Hệ thống đang tự động khởi động lại sau 3 giờ...{Style.RESET_ALL}")
    python = sys.executable
    os.execl(python, python, *sys.argv)

# ================== SIGNAL ==================
def signal_handler(sig, frame):
    print(f"\n{Fore.RED}{Style.BRIGHT}Nhận Ctrl+C, đang tắt bot...{Style.RESET_ALL}")
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ================== MAIN ==================
if __name__ == "__main__":
    client = Client(API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES)

    # Khởi động thread tự động restart sau mỗi 3 giờ (10800 giây)
    restart_thread = threading.Thread(target=auto_restart, args=(30,), daemon=True)
    restart_thread.start()

    try:
        client.listen(thread=False, delay=0)
    except KeyboardInterrupt:
        cleanup()
