from config import PREFIX
import os
from zlapi.models import Message, MultiMsgStyle, MessageStyle
import importlib
import math

des = {
    'version': "1.4.3",
    'credits': "Nguyễn Đức Tài",
    'description': "Lấy thông tin nhóm"
}


def get_all_hzlbot():
    hzlbot_cmds = {}

    for module_name in os.listdir('modules'):
        if module_name.endswith('.py') and module_name != '__init__.py':
            module_path = f'modules.{module_name[:-3]}'
            try:
                module = importlib.import_module(module_path)
                if hasattr(module, 'get_hzlbot'):
                    module_hzlbot = module.get_hzlbot()
                    hzlbot_cmds.update(module_hzlbot)
            except:
                continue

    command_names = list(hzlbot_cmds.keys())
    return command_names

def handle_help_command(message, message_object, thread_id, thread_type, author_id, client):
    command_names = get_all_hzlbot()
    total_commands = len(command_names)
    total_pages = 7  # Fixed to 7 pages

    items_per_page = math.ceil(total_commands / total_pages)

    page_number = 1
    if message.startswith(f"{PREFIX}help "):
        try:
            page_number = int(message.split()[1])
        except (IndexError, ValueError):
            page_number = 1

    page_number = max(1, min(total_pages, page_number))

    start_index = (page_number - 1) * items_per_page
    end_index = min(start_index + items_per_page, total_commands)
    paged_commands = command_names[start_index:end_index]

    numbered_hzlbot = [f"{i + 1 + start_index}. {name}" for i, name in enumerate(paged_commands)]
    menu_message = (
        f"Tổng số lệnh hiện tại có: {total_commands} lệnh\n"
        f"Trang {page_number}/{total_pages}\n"
        "copyright: Nguyen Duc Tai\n" + "\n".join(numbered_hzlbot)
    )

    msg_length = len(menu_message)
    style = MultiMsgStyle([
        MessageStyle(offset=0, length=msg_length, style="color", color="#638CEE", auto_format=False),
        MessageStyle(offset=0, length=msg_length, style="font", size="13", auto_format=False),
        MessageStyle(offset=0, length=msg_length, style="italic", auto_format=False)
    ])

    message_to_send = Message(text=menu_message, style=style)
    client.replyMessage(message_to_send, message_object, thread_id, thread_type, ttl=60000)

def get_hzlbot():
    return {
        'help': handle_help_command
    }