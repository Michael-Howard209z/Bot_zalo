import requests

LAVA_HOST = "lava-v4.ajieblogs.eu.org"
LAVA_PORT = 443
LAVA_PASS = "https://dsc.gg/ajidevserver"
LAVA_SECURE = True

protocol = "https" if LAVA_SECURE else "http"
url = f"{protocol}://{LAVA_HOST}:{LAVA_PORT}/v4/loadtracks"

headers = {
    "Authorization": LAVA_PASS,
    "Content-Type": "application/json"
}

data = {"identifier": "ytsearch:love 3000"}

try:
    resp = requests.post(url, headers=headers, json=data, timeout=10)
    print(resp.status_code)
    print(resp.json())
except Exception as e:
    print("Lỗi request:", e)
