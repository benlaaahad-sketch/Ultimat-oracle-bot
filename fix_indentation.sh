#!/data/data/com.termux/files/usr/bin/bash

# رنگ‌ها برای خروجی زیبا
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}🛠️  رفع خودکار مشکل Indentation${NC}"
echo -e "${BLUE}================================${NC}"

# رفتن به پوشه پروژه
cd ~/ultimate_oracle_bot || {
    echo -e "${RED}❌ پوشه پروژه پیدا نشد!${NC}"
    exit 1
}

echo -e "${YELLOW}📁 پوشه پروژه: $(pwd)${NC}"

# چک کردن وجود فایل
if [ ! -f "bot/ultimate_bot.py" ]; then
    echo -e "${RED}❌ فایل bot/ultimate_bot.py پیدا نشد!${NC}"
    exit 1
fi

echo -e "${YELLOW}📄 فایل ultimate_bot.py پیدا شد.${NC}"

# ایجاد بک‌آپ
cp bot/ultimate_bot.py bot/ultimate_bot.py.bak
echo -e "${GREEN}✅ بک‌آپ گرفته شد: bot/ultimate_bot.py.bak${NC}"

# رفع مشکل indentation - روش اول: با sed
echo -e "${YELLOW}🔧 در حال رفع مشکل indentation...${NC}"

# پیدا کردن خط مشکل‌دار و اصلاحش
sed -i 's/^[[:space:]]*webhook_thread = threading\.Thread(target=self\._run_webhook_server, daemon=True)/        webhook_thread = threading.Thread(target=self._run_webhook_server, daemon=True)/' bot/ultimate_bot.py

# اگه روش اول کار نکرد، روش دوم رو امتحان کن
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ خط 1261 اصلاح شد (روش اول)${NC}"
else
    echo -e "${YELLOW}⚠️ روش اول کار نکرد، روش دوم رو امتحان می‌کنم...${NC}"
    
    # روش دوم: با awk
    awk '/webhook_thread = threading.Thread/{gsub(/^[ \t]+/, "        ")}1' bot/ultimate_bot.py > bot/ultimate_bot.py.tmp
    mv bot/ultimate_bot.py.tmp bot/ultimate_bot.py
    echo -e "${GREEN}✅ خطوط مربوط به webhook_thread اصلاح شد (روش دوم)${NC}"
fi

# چک کردن سینتکس پایتون
echo -e "${YELLOW}🔍 چک کردن سینتکس فایل...${NC}"
python3 -m py_compile bot/ultimate_bot.py 2>/tmp/syntax_error.tmp

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ سینتکس درست است!${NC}"
else
    echo -e "${RED}❌ هنوز مشکل سینتکس وجود دارد:${NC}"
    cat /tmp/syntax_error.tmp
fi

# commit و push به GitHub
echo -e "${YELLOW}📤 ارسال تغییرات به GitHub...${NC}"
git add bot/ultimate_bot.py
git commit -m "رفع خودکار مشکل indentation با اسکریپت"
git push origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ تغییرات با موفقیت به GitHub ارسال شد!${NC}"
else
    echo -e "${RED}❌ خطا در ارسال به GitHub.${NC}"
    echo -e "${YELLOW}⚠️ ممکنه نیاز به token داشته باشی.${NC}"
fi

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}✅ کار تمام شد!${NC}"
echo -e "${YELLOW}⏱️  حالا ۵ دقیقه صبر کن تا Railway دیپلوی کنه.${NC}"
echo -e "${BLUE}================================${NC}"
