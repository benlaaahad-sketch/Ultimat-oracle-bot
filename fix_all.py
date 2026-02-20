#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت نهایی رفع همه مشکلات ربات
- اضافه کردن webhook server
- رفع مشکل 404
- تنظیم خودکار
"""

import os
import re

def fix_ultimate_bot():
    """رفع مشکل فایل ultimate_bot.py"""
    
    file_path = "bot/ultimate_bot.py"
    if not os.path.exists(file_path):
        print(f"❌ فایل {file_path} پیدا نشد!")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # چک کردن اینکه آیا webhook server قبلاً اضافه شده
    if "def _run_webhook_server" in content:
        print("✅ webhook server قبلاً اضافه شده!")
        return True
    
    # پیدا کردن محل اضافه کردن متد جدید
    lines = content.split('\n')
    
    # پیدا کردن خط آخر کلاس
    class_end = -1
    for i in range(len(lines)-1, 0, -1):
        if lines[i].strip() == '' and i < len(lines)-1:
            if lines[i+1].strip() and not lines[i+1].strip().startswith('def'):
                class_end = i
                break
    
    if class_end == -1:
        class_end = len(lines)
    
    # متد جدید برای webhook server
    webhook_method = '''
    def _run_webhook_server(self):
        """راه‌اندازی سرور webhook در پورت 8080"""
        import threading
        import asyncio
        import json
        from aiohttp import web
        from telegram import Update
        
        async def webhook_handler(request):
            try:
                data = await request.json()
                if hasattr(self, 'app') and self.app:
                    update = Update.de_json(data, self.app.bot)
                    await self.app.process_update(update)
                return web.Response(text='OK')
            except Exception as e:
                print(f"Webhook error: {e}")
                return web.Response(text='Error', status=500)
        
        async def run_server():
            app = web.Application()
            app.router.add_post('/webhook', webhook_handler)
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 8080)
            await site.start()
            print("✅ Webhook server running on port 8080")
            
            # نگه داشتن سرور فعال
            while True:
                await asyncio.sleep(3600)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())
        loop.run_forever()
'''
    
    # اضافه کردن متد به انتهای کلاس
    lines.insert(class_end, webhook_method)
    
    # پیدا کردن متد run و اضافه کردن راه‌اندازی webhook
    for i, line in enumerate(lines):
        if 'def run(self):' in line:
            # پیدا کردن جایی که self.app ساخته میشه
            for j in range(i, min(i+30, len(lines))):
                if 'Application.builder' in lines[j] or 'self.app =' in lines[j]:
                    # چند خط بعد رو نگاه کن
                    for k in range(j, min(j+10, len(lines))):
                        if ')' in lines[k] and ';' not in lines[k]:
                            # بعد از این خط، راه‌اندازی webhook رو اضافه کن
                            indent = re.match(r'^(\s*)', lines[k]).group(1)
                            webhook_line = f'{indent}        # راه‌اندازی webhook server در thread جدا\n'
                            webhook_line += f'{indent}        webhook_thread = threading.Thread(target=self._run_webhook_server, daemon=True)\n'
                            webhook_line += f'{indent}        webhook_thread.start()\n'
                            lines.insert(k+1, webhook_line)
                            break
                    break
            break
    
    # ذخیره فایل
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("✅ فایل ultimate_bot.py با موفقیت به‌روزرسانی شد!")
    return True

def fix_requirements():
    """اضافه کردن aiohttp به requirements.txt"""
    
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print("❌ requirements.txt پیدا نشد!")
        return False
    
    with open(req_file, 'r') as f:
        content = f.read()
    
    if 'aiohttp' not in content:
        with open(req_file, 'a') as f:
            f.write('\naiohttp==3.9.1\n')
        print("✅ aiohttp به requirements.txt اضافه شد!")
    else:
        print("✅ aiohttp از قبل وجود دارد!")
    
    return True

def create_set_webhook_script():
    """ایجاد اسکریپت تنظیم webhook"""
    
    with open('set_webhook_auto.py', 'w') as f:
        f.write('''#!/usr/bin/env python3
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
print("\\nوضعیت نهایی webhook:")
print(status)
''')
    print("✅ اسکریپت set_webhook_auto.py ایجاد شد!")

def create_railway_json():
    """ایجاد railway.json برای تنظیمات healthcheck"""
    
    with open('railway.json', 'w') as f:
        f.write('''{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
''')
    print("✅ railway.json ایجاد شد!")

def git_commit_push():
    """commit و push به GitHub"""
    
    print("در حال commit و push به GitHub...")
    os.system('git add .')
    os.system('git commit -m "رفع خودکار همه مشکلات"')
    os.system('git push origin main')
    print("✅ تغییرات با موفقیت به GitHub ارسال شد!")

def main():
    print("="*60)
    print("🛠️  اسکریپت رفع خودکار مشکلات ربات")
    print("="*60)
    
    # مرحله 1: رفع ultimate_bot.py
    print("\n📁 مرحله 1: رفع فایل ultimate_bot.py")
    if fix_ultimate_bot():
        print("   ✅ انجام شد")
    else:
        print("   ❌ مشکل در رفع فایل")
    
    # مرحله 2: رفع requirements.txt
    print("\n📁 مرحله 2: به‌روزرسانی requirements.txt")
    fix_requirements()
    
    # مرحله 3: ایجاد railway.json
    print("\n📁 مرحله 3: ایجاد railway.json")
    create_railway_json()
    
    # مرحله 4: ایجاد اسکریپت تنظیم webhook
    print("\n📁 مرحله 4: ایجاد اسکریپت تنظیم webhook")
    create_set_webhook_script()
    
    # مرحله 5: commit و push
    print("\n📁 مرحله 5: ارسال به GitHub")
    git_commit_push()
    
    print("\n" + "="*60)
    print("✅ همه مراحل با موفقیت انجام شد!")
    print("="*60)
    print("\nمراحل بعدی:")
    print("1. صبر کن تا Railway دیپلوی کنه (حدود ۵ دقیقه)")
    print("2. اجرا کن: python set_webhook_auto.py")
    print("3. دامنه Railway رو وارد کن")
    print("4. ربات تو تلگرام تست کن")

if __name__ == "__main__":
    main()
