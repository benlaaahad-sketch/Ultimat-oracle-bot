import requests

BOT_TOKEN = "7358190664:AAGMFdD6HFP0CEQx_3Hv1YCMtWzAsVWgsJk"

# اول webhook رو پاک کن
print("🧹 پاک کردن webhook...")
r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
print(r.json())

# دوباره با مسیر درست تنظیم کن
webhook_url = "https://web-production-1302b.up.railway.app/webhook"
print(f"\n📡 تنظیم webhook به آدرس: {webhook_url}")
r = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={"url": webhook_url}
)
print(r.json())
