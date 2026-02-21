#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ماژول ایمن برای import کتابخونه‌ها با fallback
این فایل باید حتماً وجود داشته باشه
"""

import logging
from typing import Any, Optional, Tuple
import importlib

logger = logging.getLogger(__name__)

class SafeImporter:
    """
    کلاس ایمن برای import کتابخونه‌ها
    اگه کتابخونه‌ای نباشه، fallback مناسب برمی‌گردونه
    """
    
    def __init__(self):
        self.import_cache = {}
        self.missing_modules = []
        logger.info("🔰 SafeImporter initialized")
    
    def safe_import(self, module_name: str, fallback: Any = None) -> Tuple[bool, Any]:
        """
        import ایمن با fallback
        
        Returns:
            (موفقیت, ماژول یا fallback)
        """
        if module_name in self.import_cache:
            return True, self.import_cache[module_name]
        
        try:
            module = importlib.import_module(module_name)
            self.import_cache[module_name] = module
            logger.debug(f"✅ Successfully imported {module_name}")
            return True, module
        except ImportError as e:
            logger.warning(f"⚠️ Could not import {module_name}: {e}")
            self.missing_modules.append(module_name)
            return False, fallback
    
    def safe_import_from(self, module_name: str, attr_name: str, fallback: Any = None) -> Tuple[bool, Any]:
        """
        import یک attribute از یک module با fallback
        """
        success, module = self.safe_import(module_name)
        if not success:
            return False, fallback
        
        try:
            attr = getattr(module, attr_name)
            return True, attr
        except AttributeError as e:
            logger.warning(f"⚠️ Could not import {attr_name} from {module_name}: {e}")
            return False, fallback
    
    def has_module(self, module_name: str) -> bool:
        """چک کردن وجود ماژول"""
        success, _ = self.safe_import(module_name)
        return success
    
    def get_missing_modules(self) -> list:
        """گرفتن لیست ماژول‌های missing"""
        return self.missing_modules

# نمونه‌سازی سراسری
importer = SafeImporter()

# ==================== Fallback classes ====================

class DummyClass:
    """کلاس جایگزین برای وقتی کتابخونه‌ای نباشه"""
    def __init__(self, *args, **kwargs):
        pass
    
    def __getattr__(self, name):
        return lambda *args, **kwargs: None
    
    def __call__(self, *args, **kwargs):
        return None

class DummyDataFrame:
    """جایگزین pandas DataFrame"""
    def __init__(self, data=None):
        self.data = data or []
    
    def to_dict(self):
        return {}
    
    def to_json(self):
        return '{}'
    
    def head(self, n=5):
        return self

# ==================== Helper functions ====================

def get_numpy():
    """دریافت numpy با fallback"""
    success, np = importer.safe_import('numpy')
    if success:
        return np
    # fallback ساده
    class SimpleNumpy:
        @staticmethod
        def array(x):
            return x
        @staticmethod
        def mean(x):
            return sum(x)/len(x) if x else 0
    return SimpleNumpy()

def get_pandas():
    """دریافت pandas با fallback"""
    success, pd = importer.safe_import('pandas')
    if success:
        return pd
    return DummyDataFrame

def get_sklearn():
    """دریافت sklearn با fallback"""
    success, sk = importer.safe_import('sklearn')
    if success:
        return sk
    return DummyClass

def get_tensorflow():
    """دریافت tensorflow با fallback"""
    success, tf = importer.safe_import('tensorflow')
    if success:
        return tf
    return DummyClass

def get_torch():
    """دریافت torch با fallback"""
    success, torch = importer.safe_import('torch')
    if success:
        return torch
    return DummyClass

def get_transformers():
    """دریافت transformers با fallback"""
    success, tr = importer.safe_import('transformers')
    if success:
        return tr
    return DummyClass

def get_nltk():
    """دریافت nltk با fallback"""
    success, nltk = importer.safe_import('nltk')
    if success:
        return nltk
    return DummyClass

def get_textblob():
    """دریافت textblob با fallback"""
    success, tb = importer.safe_import('textblob')
    if success:
        return tb
    return DummyClass

def get_vader():
    """دریافت vaderSentiment با fallback"""
    success, vs = importer.safe_import('vaderSentiment')
    if success:
        return vs
    return DummyClass

def get_web3():
    """دریافت web3 با fallback"""
    success, w3 = importer.safe_import('web3')
    if success:
        return w3
    return DummyClass

def get_ccxt():
    """دریافت ccxt با fallback"""
    success, ccxt = importer.safe_import('ccxt')
    if success:
        return ccxt
    return DummyClass
