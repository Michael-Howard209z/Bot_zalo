from config import PREFIX
import os
import importlib
import random
from zlapi.models import Message

des = {
    'version': "1.0.2",
    'credits': "NguyenHoangDev",
    'description': "Xem toàn bộ lệnh hiện có của bot"
}

# Danh sách các emoji
#emojis = ['🐯', '💤', '✨', '💦', '🎶', '⚡', '🌏', '🌊', '💌', '☃️', '🎡', '⛈️', '💢', '🌌', '💝', '🌋', '🌪️', '☔', '🌦️', '🏔️', '🌧️', '🚀', '🐲', '🧸', '📲', '💩', '💨', '✨', '💟', '🏵️', '🏞️', '🌠', '🛸', '💎', '⭐', '☄️', '🧊', '🍡', '🎮', '🎵', '🔮', '🇻🇳', '☠️', '🤍', '🐟', '💻', '🥳', '🐰']

def get_all_hzlbot():
    hzlbot = {}

    for module_name in os.listdir('modules'):
        if module_name.endswith('.py') and module_name != '__init__.py':
            module_path = f'modules.{module_name[:-3]}'
            module = importlib.import_module(module_path)

            if hasattr(module, 'get_hzlbot'):
                module_hzlbot = module.get_hzlbot()
                hzlbot.update(module_hzlbot)

    command_names = list(hzlbot.keys())
    
    return command_names

def handle_menu_command(message, message_object, thread_id, thread_type, author_id, client):
    command_names = get_all_hzlbot()
    total_hzlbot = len(command_names)
    
    # Thêm emoji ngẫu nhiên vào trước mỗi lệnh
    #numbered_hzlbot =  [f"- {random.choice(emojis)} {name}" for i, name in enumerate(command_names)]
    prefix = PREFIX
    numbered_hzlbot =  [f"- {name}" for i, name in enumerate(command_names)]
    menu_message = f"𝙈𝙚𝙣𝙪 \n{total_hzlbot} 𝐋ệ𝐧𝐡 𝐦𝐞𝐧𝐮\n 𝐔𝐩𝐝𝐚𝐭𝐞 : 𝐯𝟏.𝟎.𝟐" + f"\n Prefix là: [{prefix}]\n" + f"\n__________________________,\n" + "\n".join(numbered_hzlbot)
    
    client.sendLocalImage("menu.jpg", thread_id=thread_id, thread_type=thread_type, message=Message(text=menu_message),ttl=120000)

    # Bot already sent image with menu message, no need for redundant replyMessage

def get_hzlbot():
    return {
        'menu': handle_menu_command
    }