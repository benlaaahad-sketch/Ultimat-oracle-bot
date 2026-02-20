import requests

BOT_TOKEN = "7358190664:AAGMFdD6HFP0CEQx_3Hv1YCMtWzAsVWgsJk"

# پاک کردن webhook (که همه پیام‌های معلق هم پاک بشن)
r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
print("🧹 Webhook پاک شد:", r.json())

# صبر کن
import time
time.sleep(2)

# تنظیم دوباره
webhook_url = "https://web-production-1302b.up.railway.app/webhook"
r = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={"url": webhook_url}
)
print("📡 Webhook تنظیم شد:", r.json())

# چک کردن وضعیت
r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo")
print("\n📊 وضعیت نهایی:")
print(r.json())
