#!/data/data/com.termux/files/usr/bin/bash

echo "🛠️  رفع مشکل indentation در فایل ultimate_bot.py"

# رفتن به پوشه پروژه
cd ~/ultimate_oracle_bot || exit

# ایجاد بک‌آپ
cp bot/ultimate_bot.py bot/ultimate_bot.py.bak
echo "✅ بک‌آپ گرفته شد"

# استفاده از sed برای اصلاح دقیق خط 1262
sed -i '1262s/^[[:space:]]*/        /' bot/ultimate_bot.py

# اطمینان از اینکه خط 1261 هم درسته
sed -i '1261s/^[[:space:]]*/        /' bot/ultimate_bot.py

echo "✅ خطوط 1261 و 1262 اصلاح شدند"

# چک کردن سینتکس
python3 -m py_compile bot/ultimate_bot.py
if [ $? -eq 0 ]; then
    echo "✅ سینتکس درست است"
else
    echo "❌ هنوز مشکل وجود دارد"
fi

# commit و push
git add bot/ultimate_bot.py
git commit -m "رفع نهایی indentation"
git push origin main

echo "✅ تغییرات به GitHub ارسال شد"
echo "⏱️  ۵ دقیقه صبر کن تا Railway دیپلوی کنه"
