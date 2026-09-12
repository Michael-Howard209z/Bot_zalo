import requests
from zlapi.models import Message
from datetime import datetime

def fetch_weather_info():
    # Địa điểm: Bạn có thể thay đổi vĩ độ và kinh độ
    latitude = 21.0285  # Vĩ độ của thành phố Hồ Chí Minh
    longitude = 105.804  # Kinh độ của thành phố Hồ Chí Minh
    
    # API URL
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&daily=precipitation_sum,temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"

    response = requests.get(url)
    data = response.json()

    if 'daily' in data:
        daily_data = data['daily']
        weather_code = daily_data['weathercode'][0]
        min_temp = daily_data['temperature_2m_min'][0]
        max_temp = daily_data['temperature_2m_max'][0]
        precipitation = daily_data['precipitation_sum'][0]
        
        # Tạo thông báo thời tiết
        weather_info = create_weather_message(weather_code, min_temp, max_temp, precipitation)
        return weather_info
    else:
        return "Không thể lấy thông tin thời tiết."

def create_weather_message(weather_code, min_temp, max_temp, precipitation):
    # Dự đoán thời tiết theo mã thời tiết
    if weather_code == 1:
        weather_description = "Trời quang"
    elif weather_code == 2:
        weather_description = "Mây ít"
    elif weather_code == 3:
        weather_description = "Mây vừa"
    elif weather_code == 4:
        weather_description = "Mây nhiều"
    elif weather_code in [5, 6, 7]:
        weather_description = "Mưa"
    else:
        weather_description = "Thời tiết không xác định"

    # Tạo chuỗi thông báo
    message = (
        "📢 [THÔNG BÁO THỜI TIẾT BY MLOI]\n"
        "Thời tiết hôm nay:\n"
        f"Dự kiến thời tiết: {weather_description} từ chiều Chủ Nhật đến cuối đêm Chủ Nhật\n"
        f"🌡 Nhiệt độ thấp nhất - cao nhất: {min_temp}°C - {max_temp}°C\n"
        f"🌡 Nhiệt độ cảm nhận được: 18°C - 24°C\n"
        f"🌧 Lượng mưa: {precipitation} mm\n"
        "☔ Xác suất mưa: 100%\n"
        "🌞 Ban ngày: Mưa rào\n"
        "🌙 Ban đêm: Đôi lúc có mưa"
    )
    return message

def handle_weather_command(message, message_object, thread_id, thread_type, author_id, client):
    weather_info = fetch_weather_info()
    client.sendMessage(Message(text=weather_info), thread_id, thread_type,ttl=50000000)

def get_hzlbot():
    return {
        'thoitiet': handle_weather_command
    }