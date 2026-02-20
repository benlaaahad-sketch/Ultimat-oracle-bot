#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The Ultimate Oracle Bot - Main Entry Point
Version: 1.0.0
"""

import os
import sys
import logging
from pathlib import Path

# تنظیم مسیر
sys.path.append(str(Path(__file__).parent))

# تلاش برای import ماژول‌ها
try:
    from bot.ultimate_bot import UltimateBot
    from database.models import init_database
    from utils.logger import setup_logger
    from config import *
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📝 Make sure all files are created correctly")
    sys.exit(1)

# تنظیم لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('main')

def create_initial_backup():
    """ایجاد پشتیبان اولیه قبل از اجرا"""
    try:
        from utils.backup_manager import BackupManager
        bm = BackupManager()
        backup = bm.create_backup("initial_setup")
        if backup['success']:
            logger.info(f"✅ Initial backup created: {backup['file']} ({backup['size_mb']} MB)")
        else:
            logger.warning("⚠️ Initial backup failed")
    except Exception as e:
        logger.error(f"❌ Backup error: {e}")

def main():
    """نقطه ورود اصلی"""
    
    logger.info("="*60)
    logger.info("🚀 Starting The Ultimate Oracle Bot")
    logger.info("="*60)
    
    try:
        # ایجاد پشتیبان اولیه
        logger.info("📦 Creating initial backup...")
        create_initial_backup()
        
        # راه‌اندازی دیتابیس
        logger.info("🗄️ Initializing database...")
        init_database()
        
        # ایجاد ربات
        logger.info("🤖 Creating bot instance...")
        bot = UltimateBot()
        
        # اجرا
        logger.info("✅ Bot is ready! Press Ctrl+C to stop")
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("="*60)

if __name__ == "__main__":
    main()
