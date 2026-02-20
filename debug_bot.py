import requests
import json

BOT_TOKEN = "7358190664:AAGMFdD6HFP0CEQx_3Hv1YCMtWzAsVWgsJk"

print("🔍 بررسی وضعیت ربات...")
print("="*50)

# 1. چک کردن Webhook
print("\n📡 1. وضعیت Webhook:")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
response = requests.get(url)
data = response.json()
print(json.dumps(data, indent=2))

# 2. چک کردن اینکه بات فعال هست
print("\n🤖 2. اطلاعات بات:")
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
response = requests.get(url)
data = response.json()
print(json.dumps(data, indent=2))

# 3. تست ارسال پیام به خودت
print("\n📤 3. تست ارسال پیام:")
YOUR_CHAT_ID = 6590867551
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
data = {
    "chat_id": YOUR_CHAT_ID,
    "text": "🧪 این یه پیام تست از اسکریپت debug هست"
}
response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))

print("\n" + "="*50)
