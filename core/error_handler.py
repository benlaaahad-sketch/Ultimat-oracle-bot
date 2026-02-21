#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدیریت خطاهای سراسری
"""

import logging
import sys
import traceback
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

class ErrorHandler:
    """
    کلاس مدیریت خطاها با قابلیت logging و recovery
    """
    
    def __init__(self):
        self.error_count = 0
        self.error_history = []
        self.recovery_strategies = {}
        logger.info("🔰 ErrorHandler initialized")
        
    def handle_error(self, error: Exception, context: dict = None):
        """مدیریت یک خطا"""
        
        self.error_count += 1
        error_type = type(error).__name__
        
        error_info = {
            'type': error_type,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {},
            'count': self.error_count
        }
        
        self.error_history.append(error_info)
        
        # نگه داشتن فقط ۱۰۰ خطای آخر
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
        
        # لاگ کردن
        logger.error(f"❌ Error #{self.error_count}: {error_type} - {error}")
        
        # تلاش برای recovery
        self.try_recovery(error, context)
        
        return error_info
    
    def try_recovery(self, error: Exception, context: dict = None):
        """تلاش برای بازیابی از خطا"""
        
        error_type = type(error).__name__
        
        if error_type in self.recovery_strategies:
            try:
                self.recovery_strategies[error_type](error, context)
                logger.info(f"✅ Recovered from {error_type}")
            except Exception as e:
                logger.error(f"❌ Recovery failed: {e}")
    
    def register_recovery(self, error_type: str, strategy: Callable):
        """ثبت استراتژی بازیابی برای یک نوع خطا"""
        self.recovery_strategies[error_type] = strategy
    
    def get_stats(self) -> dict:
        """گرفتن آمار خطاها"""
        
        # دسته‌بندی خطاها
        error_types = {}
        for err in self.error_history:
            err_type = err['type']
            error_types[err_type] = error_types.get(err_type, 0) + 1
        
        return {
            'total_errors': self.error_count,
            'error_types': error_types,
            'recent_errors': self.error_history[-5:] if self.error_history else []
        }

# نمونه‌سازی سراسری
error_handler = ErrorHandler()

# ==================== Decorators ====================

def safe_execute(default_return=None, log_error=True):
    """
    دکوریتور برای اجرای ایمن توابع
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    error_handler.handle_error(e, {
                        'function': func.__name__,
                        'args': str(args)[:100],
                        'kwargs': str(kwargs)[:100]
                    })
                return default_return
        return wrapper
    return decorator

def safe_async_execute(default_return=None, log_error=True):
    """
    دکوریتور برای اجرای ایمن توابع async
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    error_handler.handle_error(e, {
                        'function': func.__name__,
                        'args': str(args)[:100],
                        'kwargs': str(kwargs)[:100]
                    })
                return default_return
        return wrapper
    return decorator

# ==================== ثبت استراتژی‌های پیش‌فرض ====================

def handle_import_error(error, context):
    """بازیابی از خطای import"""
    try:
        module_name = str(error).split("'")[1] if "'" in str(error) else "unknown"
        logger.warning(f"⚠️ Module {module_name} not found. Some features may be limited.")
    except:
        pass

def handle_indentation_error(error, context):
    """بازیابی از خطای indentation"""
    logger.warning("⚠️ Indentation error detected. Please check the code formatting.")

def handle_module_not_found(error, context):
    """بازیابی از ModuleNotFoundError"""
    try:
        module_name = str(error).split("'")[1] if "'" in str(error) else "unknown"
        logger.warning(f"⚠️ Module {module_name} not found. Using fallback.")
    except:
        pass

error_handler.register_recovery('ModuleNotFoundError', handle_module_not_found)
error_handler.register_recovery('ImportError', handle_import_error)
error_handler.register_recovery('IndentationError', handle_indentation_error)
