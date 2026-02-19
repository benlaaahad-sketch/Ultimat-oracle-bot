#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The Ultimate Oracle Bot - Main Entry Point
Version: 1.0.0 (pandas-free)
"""

import os
import sys
import logging
from pathlib import Path

# تنظیم مسیر
sys.path.append(str(Path(__file__).parent))

# تنظیم لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('main')

# ==================== ایمپورت‌ها ====================

try:
    # ابتدا کتابخونه‌های اصلی
    from bot.ultimate_bot import UltimateBot
    from database.models import init_database
    from config import *
    
    # تلاش برای ایمپورت logger (اگه وجود داشت)
    try:
        from utils.logger import setup_logger
        logger = setup_logger('main')
    except ImportError:
        print("⚠️ Logger module not found, using basic logging")
    
    # pandas غیرفعال - به جای اون از numpy و csv استفاده می‌کنیم
    HAS_PANDAS = False
    print("📊 Running in pandas-free mode (numpy + csv will be used)")
    
except ImportError as e:
    print(f"❌ Critical import error: {e}")
    print("📝 Please install required packages:")
    print("   pip install python-telegram-bot sqlalchemy requests aiohttp beautifulsoup4 python-dateutil")
    sys.exit(1)

# ==================== توابع کمکی ====================

def check_environment():
    """بررسی محیط اجرا"""
    
    print("\n" + "="*60)
    print("🚀 The Ultimate Oracle Bot")
    print("="*60)
    
    # پایتون
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # کتابخونه‌های نصب شده
    installed = []
    missing = []
    
    required = [
        ('telegram', 'python-telegram-bot'),
        ('sqlalchemy', 'sqlalchemy'),
        ('requests', 'requests'),
        ('aiohttp', 'aiohttp'),
        ('bs4', 'beautifulsoup4'),
        ('dateutil', 'python-dateutil')
    ]
    
    for module, package in required:
        try:
            __import__(module)
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    if installed:
        print(f"✅ Installed: {', '.join(installed)}")
    
    if missing:
        print(f"❌ Missing: {', '.join(missing)}")
        print("   Run: pip install " + ' '.join(missing))
        return False
    
    return True

def create_directories():
    """ایجاد پوشه‌های مورد نیاز"""
    
    dirs = ['data', 'logs', 'memory', 'backups']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        print(f"📁 Directory '{d}/' checked")

# ==================== تابع اصلی ====================

def main():
    """نقطه ورود اصلی"""
    
    try:
        # بررسی محیط
        if not check_environment():
            print("\n❌ Environment check failed")
            return
        
        # ایجاد پوشه‌ها
        print("\n📁 Checking directories...")
        create_directories()
        
        # راه‌اندازی دیتابیس
        print("\n🗄️ Initializing database...")
        init_database()
        
        # ایجاد ربات
        print("\n🤖 Creating bot instance...")
        bot = UltimateBot()
        
        # اجرا
        print("\n✅ Bot is ready! Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "="*60)
    return 0

# ==================== اجرا ====================

if __name__ == "__main__":
    sys.exit(main())
