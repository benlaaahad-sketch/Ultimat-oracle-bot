#!/usr/bin/env python3
import logging
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Starting bot...")
    
    # ایمپورت ربات
    from bot.ultimate_bot import UltimateBot
    from database.models import init_database
    
    # راه‌اندازی دیتابیس
    init_database()
    
    # اجرای ربات
    bot = UltimateBot()
    bot.run()

if __name__ == "__main__":
    main()
