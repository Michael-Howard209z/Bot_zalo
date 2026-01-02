import os
from zlapi.models import Message, MultiMsgStyle, MessageStyle
import importlib
import math

des = {
    'version': "1.4.3",
    'credits': "Nguyễn Đức Tài",
    'description': "Lấy thông tin nhóm"
}

# Copyright Tamhoangdz
def get_all_mitaizl():
    mitaizl = {}

    for module_name in os.listdir('modules'):
        if module_name.endswith('.py') and module_name != '__init__.py':
            module_path = f'modules.{module_name[:-3]}'
            module = importlib.import_module(module_path)

            if hasattr(module, 'get_mitaizl'):
                module_mitaizl = module.get_mitaizl()
                mitaizl.update(module_mitaizl)

    command_names = list(mitaizl.keys())
    return command_names

# Copyright Tamhoangdz
def handle_menu_command(message, message_object, thread_id, thread_type, author_id, client):
    command_names = get_all_mitaizl()
    total_commands = len(command_names)
    total_pages = 7  # Fixed to 7 pages

# Copyright Tamhoangdz
    items_per_page = math.ceil(total_commands / total_pages)

# Copyright Tamhoangdz
    page_number = 1
    if message.startswith(",help "):
        try:
            page_number = int(message.split()[1])
        except (IndexError, ValueError):
            page_number = 1

# Copyright Tamhoangdz
    page_number = max(1, min(total_pages, page_number))

# Copyright Tamhoangdz
    start_index = (page_number - 1) * items_per_page
    end_index = min(start_index + items_per_page, total_commands)
    paged_commands = command_names[start_index:end_index]

    numbered_mitaizl = [f"{i + 1 + start_index}. {name}" for i, name in enumerate(paged_commands)]
    menu_message = (
        f"Tổng số lệnh panel hiện tại có: {total_commands} lệnh\n"
        f"Trang 1/1\n"
        "copyright:binzdz:\n" + "\n".join(numbered_mitaizl)
    )

    msg_length = len(menu_message)
    style = MultiMsgStyle([
        MessageStyle(offset=0, length=msg_length, style="color", color="#638CEE", auto_format=False),
        MessageStyle(offset=0, length=msg_length, style="font", size="13", auto_format=False),
        MessageStyle(offset=0, length=msg_length, style="italic", auto_format=False)
    ])

    message_to_send = Message(text=menu_message, style=style)
    client.replyMessage(message_to_send, message_object, thread_id, thread_type,ttl=60000)

def get_mitaizl():
    return {
        'panel': handle_menu_command
    }