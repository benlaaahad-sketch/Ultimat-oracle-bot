import requests

BOT_TOKEN = "7358190664:AAGMFdD6HFP0CEQx_3Hv1YCMtWzAsVWgsJk"
WEBHOOK_URL = "https://web-production-1302b.up.railway.app/webhook"

print(f"📡 تنظیم webhook به: {WEBHOOK_URL}")

# پاک کردن webhook قبلی
r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
print("🧹 پاک کردن:", r.json())

# تنظیم webhook جدید
r = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={"url": WEBHOOK_URL}
)
print("📡 تنظیم:", r.json())

# چک کردن وضعیت نهایی
r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
print("\n📊 وضعیت نهایی:")
print(r.json())
