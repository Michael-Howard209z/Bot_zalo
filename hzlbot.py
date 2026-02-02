from zlapi.models import Message
import os
import importlib
from config import PREFIX
import modules.bot_info
RESET = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[92m'
RED = '\033[91m'

class CommandHandler:
    def __init__(self, client):
        self.client = client
        self.hzlbot = self.load_hzlbot()
        self.auto_hzlbot = self.load_auto_hzlbot()
        self.global_handlers = self.load_global_handlers()

    def load_hzlbot(self):
        hzlbot = {}
        modules_path = 'modules'
        success_count = 0
        failed_count = 0
        success_hzlbot = []
        failed_hzlbot = []

        for filename in os.listdir(modules_path):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'{modules_path}.{module_name}')
                    if hasattr(module, 'get_hzlbot'):
                        hzlbot.update(module.get_hzlbot())
                        success_count += 1
                        success_hzlbot.append(module_name)
                    else:
                        raise ImportError(f"Module {module_name} không có hàm get_hzlbot")
                except Exception as e:
                    print(f"{BOLD}{RED}Không thể load được module: {module_name}. Lỗi: {e}{RESET}")
                    failed_count += 1
                    failed_hzlbot.append(module_name)

        if success_count > 0:
            print(f"{BOLD}{GREEN}Đã load thành công PREFIX: {PREFIX}")
            print(f"{BOLD}{GREEN}Đã load thành công {success_count} lệnh: {', '.join(success_hzlbot)}{RESET}")
        if failed_count > 0:
            print(f"{BOLD}{RED}Không thể load được {failed_count} lệnh: {', '.join(failed_hzlbot)}{RESET}")

        return hzlbot

    def load_auto_hzlbot(self):
        """Load các lệnh không cần prefix từ folder 'modules/auto'."""
        auto_hzlbot = {}
        auto_modules_path = 'modules.auto'
        success_count = 0
        failed_count = 0
        success_auto_hzlbot = []
        failed_auto_hzlbot = []

        for filename in os.listdir('modules/auto'):
            if filename.endswith('.py') and filename != '__init__.py' and filename not in ['autoreact.py', 'antilink.py']:
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'{auto_modules_path}.{module_name}')
                    if hasattr(module, 'get_hzlbot'):
                        auto_hzlbot.update(module.get_hzlbot())
                        success_count += 1
                        success_auto_hzlbot.append(module_name)
                    else:
                        raise ImportError(f"Module {module_name} không có hàm get_hzlbot")
                except Exception as e:
                    print(f"{BOLD}{RED}Không thể load được module: {module_name}. Lỗi: {e}{RESET}")
                    failed_count += 1
                    failed_auto_hzlbot.append(module_name)

        if success_count > 0:
            print(f"{BOLD}{GREEN}Đã load thành công {success_count} lệnh auto: {', '.join(success_auto_hzlbot)}{RESET}")
        if failed_count > 0:
            print(f"{BOLD}{RED}Không thể load được {failed_count} lệnh auto: {', '.join(failed_auto_hzlbot)}{RESET}")

        return auto_hzlbot

    def load_global_handlers(self):
        """Load các handler toàn cục (chạy với mọi tin nhắn) từ folder 'modules/auto'."""
        global_handlers = []
        auto_modules_path = 'modules.auto'
        success_count = 0
        failed_count = 0
        success_global = []
        failed_global = []

        for filename in os.listdir('modules/auto'):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'{auto_modules_path}.{module_name}')
                    if hasattr(module, 'get_global_hzlbot'):
                        handlers = module.get_global_hzlbot()
                        if isinstance(handlers, list):
                            global_handlers.extend(handlers)
                            success_count += 1
                            success_global.append(module_name)
                    # Không raise error nếu không có get_global_hzlbot
                except Exception as e:
                    print(f"{BOLD}{RED}Không thể load được global handler: {module_name}. Lỗi: {e}{RESET}")
                    failed_count += 1
                    failed_global.append(module_name)

        if success_count > 0:
            print(f"{BOLD}{GREEN}Đã load thành công {success_count} global handler: {', '.join(success_global)}{RESET}")
        if failed_count > 0:
            print(f"{BOLD}{RED}Không thể load được {failed_count} global handler: {', '.join(failed_global)}{RESET}")

        return global_handlers

    def handle_command(self, message, author_id, message_object, thread_id, thread_type):
        # Chạy global handlers trước (chạy với mọi tin nhắn)
        for handler in self.global_handlers:
            try:
                handler(message, message_object, thread_id, thread_type, author_id, self.client)
            except Exception as e:
                print(f"{BOLD}{RED}[GLOBAL HANDLER ERROR] {e}{RESET}")
        
        # Xử lý các lệnh không cần prefix
        auto_command_handler = self.auto_hzlbot.get(message.lower())
        if auto_command_handler:
            auto_command_handler(message, message_object, thread_id, thread_type, author_id, self.client)
            return
        
        if not message.startswith(PREFIX):
            return
#xử lí lệnh càn prefix
        command_name = message[len(PREFIX):].split(' ')[0].lower()
        command_handler = self.hzlbot.get(command_name)

        if command_handler:
            command_handler(message, message_object, thread_id, thread_type, author_id, self.client)
        else:
            self.client.sendMessage(
                Message(text=f"Không tìm thấy lệnh '{command_name}'. Hãy dùng {PREFIX}menu để biết các lệnh có trên hệ thống."), 
                thread_id, 
                thread_type
            )
