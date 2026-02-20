#!/usr/bin/env python3
import requests
import sys

BOT_TOKEN = "7358190664:AAGMFdD6HFP0CEQx_3Hv1YCMtWzAsVWgsJk"

# گرفتن دامنه از کاربر
print("لطفا دامنه Railway خود را وارد کنید:")
print("مثال: https://ultimat-oracle-bot.up.railway.app")
domain = input("دامنه: ").strip()

if not domain.startswith('http'):
    domain = 'https://' + domain

# تنظیم webhook
url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
data = {"url": f"{domain}/webhook"}

print(f"در حال تنظیم webhook به آدرس: {domain}/webhook")
response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    if result.get('ok'):
        print("✅ Webhook با موفقیت تنظیم شد!")
    else:
        print(f"❌ خطا: {result}")
else:
    print(f"❌ خطا در اتصال: {response.status_code}")

# نمایش وضعیت نهایی
status_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
status = requests.get(status_url).json()
print("\nوضعیت نهایی webhook:")
print(status)
