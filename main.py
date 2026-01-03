from config import API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES,PREFIX
from hzlbot import CommandHandler
from zlapi import ZaloAPI
from zlapi.models import Message
from modules.bot_info import *
from modules.da import welcome
import itertools
from colorama import Fore, Style, init

GRADIENT_CORLORS = [
    Fore.LIGHTMAGENTA_EX, #tím sáng
    Fore.MAGENTA,         #tím
    Fore.LIGHTBLUE_EX,    #xanh dương sáng
    Fore.BLUE,            #xanh dương
    Fore.CYAN,            #xanh lơ
    Fore.LIGHTCYAN_EX,     #xanh lơ sáng
                   
]
def gradient_text(text):
    color_cycle = itertools.cycle(GRADIENT_CORLORS)
    result = ""
    for char in text:
        result += next(color_cycle) +Style.BRIGHT + char
        return result + Style.RESET_ALL

init(autoreset=True)

class Client(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies):
        super().__init__(api_key, secret_key, imei=imei, session_cookies=session_cookies)
        handle_bot_admin(self)
        self.version = 1.1
        self.me_name = "Bot by NguyenHoangDev"
        self.date_update = "12/01/2025"
        self.command_handler = CommandHandler(self)
    def onEvent(self,event_data,event_type):
        welcome(self,event_data,event_type)
    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        print(f"{Fore.GREEN}{Style.BRIGHT}------------------------------\n"
              f"**Message Details:**\n"
              f"- **Message:** {Style.BRIGHT}{message} {Style.NORMAL}\n"
              f"- **Author ID:** {Fore.MAGENTA}{Style.BRIGHT}{author_id} {Style.NORMAL}\n"
              f"- **Thread ID:** {Fore.YELLOW}{Style.BRIGHT}{thread_id}{Style.NORMAL}\n"
              f"- **Thread Type:** {Fore.BLUE}{Style.BRIGHT}{thread_type}{Style.NORMAL}\n"
              f"- **Message Object:** {Fore.LIGHTBLUE_EX}{Style.BRIGHT}{message_object}{Style.NORMAL}\n"
              f"{Fore.GREEN}{Style.BRIGHT}------------------------------\n"
              )
        allowed_thread_ids = get_allowed_thread_ids()
        if thread_id in allowed_thread_ids and thread_type == ThreadType.GROUP and not is_admin(author_id):
            handle_check_profanity(self, author_id, thread_id, message_object, thread_type, message)
        try:
            if isinstance(message,str):
                if message == f"{PREFIX}":
                    self.send(Message(text=f"Dùng {PREFIX}menu để biết rõ hơn"),thread_id,thread_type)
                    return
                self.command_handler.handle_command(message, author_id, message_object, thread_id, thread_type)
        except:
            pass

if __name__ == "__main__":
    client = Client(API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES)
    client.listen(thread=True,delay=0)
