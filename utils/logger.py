# utils/logger.py
"""
سیستم لاگینگ پیشرفته با قابلیت:
- ذخیره در فایل
- نمایش رنگی در کنسول
- چرخش خودکار فایل‌ها
- فرمت‌بندی حرفه‌ای
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
import os
from colorama import init, Fore, Style, Back

#初始化 colorama برای ویندوز
init(autoreset=True)

# ==================== فرمت‌های رنگی ====================

class ColoredFormatter(logging.Formatter):
    """فرمatter رنگی برای کنسول"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Back.RED + Fore.WHITE
    }
    
    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
            record.msg = f"{self.COLORS[levelname]}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    راه‌اندازی logger با فرمت حرفه‌ای
    
    Args:
        name: نام logger
        log_level: سطح لاگ (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logging.Logger: نمونه logger
    """
    
    # ایجاد پوشه logs اگر وجود ندارد
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # نام فایل لاگ با تاریخ
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{name}_{today}.log"
    
    # ==================== ایجاد logger ====================
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # پاک کردن هندلرهای قبلی
    if logger.handlers:
        logger.handlers.clear()
    
    # ==================== فرمت‌ها ====================
    
    # فرمت برای فایل
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # فرمت برای کنسول (ساده‌تر)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # ==================== هندلر فایل با چرخش ====================
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 مگابایت
        backupCount=5,           # 5 فایل پشتیبان
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)  # همه چیز در فایل ذخیره شود
    logger.addHandler(file_handler)
    
    # ==================== هندلر کنسول ====================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    logger.addHandler(console_handler)
    
    # ==================== هندلر خطا (فقط خطاها) ====================
    error_file = log_dir / f"{name}_error.log"
    error_handler = RotatingFileHandler(
        error_file,
        maxBytes=5*1024*1024,  # 5 مگابایت
        backupCount=3
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)
    
    # لاگ شروع
    logger.info(f"📝 Logger initialized: {name} (level: {log_level})")
    
    return logger

class PerformanceLogger:
    """لاگر عملکرد برای اندازه‌گیری زمان اجرا"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_times = {}
    
    def start(self, operation: str):
        """شروع اندازه‌گیری زمان"""
        self.start_times[operation] = datetime.now()
        self.logger.debug(f"⏱ Started: {operation}")
    
    def end(self, operation: str) -> float:
        """پایان اندازه‌گیری و بازگشت زمان (ثانیه)"""
        if operation in self.start_times:
            elapsed = (datetime.now() - self.start_times[operation]).total_seconds()
            self.logger.debug(f"⏱ Completed: {operation} ({elapsed:.3f}s)")
            del self.start_times[operation]
            return elapsed
        return 0
    
    def end_and_log(self, operation: str, level: str = "INFO"):
        """پایان و لاگ با سطح مشخص"""
        elapsed = self.end(operation)
        log_func = getattr(self.logger, level.lower())
        log_func(f"⏱ {operation} completed in {elapsed:.3f}s")
        return elapsed

class JsonLogger:
    """لاگر مخصوص داده‌های JSON"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_prediction(self, prediction_data: dict):
        """لاگ کردن پیش‌بینی"""
        import json
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'prediction',
            'data': prediction_data
        }
        
        self.logger.info(f"📊 PREDICTION: {json.dumps(log_entry)}")
    
    def log_payment(self, payment_data: dict):
        """لاگ کردن پرداخت"""
        import json
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'payment',
            'data': payment_data
        }
        
        self.logger.info(f"💰 PAYMENT: {json.dumps(log_entry)}")
    
    def log_error(self, error_data: dict):
        """لاگ کردن خطا"""
        import json
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'data': error_data
        }
        
        self.logger.error(f"❌ ERROR: {json.dumps(log_entry)}")

def get_logger(name: str) -> logging.Logger:
    """دریافت logger با نام مشخص (ایجاد اگر وجود نداشته باشد)"""
    logger = logging.getLogger(name)
    
    # اگر logger تنظیم نشده بود، تنظیم کن
    if not logger.handlers:
        return setup_logger(name)
    
    return logger

# ==================== استفاده آسان ====================

# logger پیش‌فرض
default_logger = setup_logger('oracle')

# مثال استفاده
if __name__ == "__main__":
    log = get_logger('test')
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    
    # Performance Logger
    perf = PerformanceLogger(log)
    perf.start("test_operation")
    import time
    time.sleep(1)
    perf.end_and_log("test_operation", "INFO")
    
    # JSON Logger
    json_log = JsonLogger(log)
    json_log.log_prediction({"type": "crypto", "result": "pump", "confidence": 0.95})
