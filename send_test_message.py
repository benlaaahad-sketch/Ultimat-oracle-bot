import requests

BOT_TOKEN = "7358190664:AAGMFdD6HFP0CEQx_3Hv1YCMtWzAsVWgsJk"
YOUR_CHAT_ID = 6590867551  # آیدی خودت

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {
    "chat_id": YOUR_CHAT_ID,
    "text": "🧪 سلام! این یه پیام تست از سمت رباته. اگه اینو می‌بینی یعنی ربات می‌تونه باهات حرف بزنه!"
}

response = requests.post(url, json=data)
print(response.json())
