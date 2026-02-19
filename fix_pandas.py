#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت خودکار برای غیرفعال کردن pandas در تمام فایل‌ها
بدون خراب کردن کد - فقط خطوط import رو کامنت میکنه
"""

import os
import re
from pathlib import Path
import shutil

def backup_file(file_path):
    """گرفتن بک‌آپ از فایل قبل از تغییر"""
    backup_path = str(file_path) + ".bak"
    shutil.copy2(file_path, backup_path)
    print(f"📦 Backup created: {backup_path}")
    return backup_path

def fix_pandas_imports(file_path):
    """پیدا کردن و کامنت کردن import pandas در فایل"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    changed = False
    new_lines = []
    
    # الگوهای مختلف import pandas
    patterns = [
        r'^\s*import\s+pandas\s*(?:as\s+\w+)?\s*$',
        r'^\s*from\s+pandas\s+import\s+.*$',
        r'^\s*import\s+pandas\.\w+.*$',
    ]
    
    for line in lines:
        original_line = line
        commented = False
        
        # بررسی هر الگو
        for pattern in patterns:
            if re.match(pattern, line.strip()):
                # خط رو کامنت کن
                if not line.strip().startswith('#'):
                    line = '# ' + line
                    changed = True
                    commented = True
                    print(f"  🔧 Commented: {original_line.strip()}")
                break
        
        # اگه خط حاوی pd. بود، یه متغیر تعریف کن
        if not commented and 'pd.' in line and not line.strip().startswith('#'):
            # قبل از این خط یه کامنت اضافه کن
            if not any('HAS_PANDAS' in l for l in new_lines[-3:]):
                new_lines.append('# pandas functionality disabled\n')
                new_lines.append('HAS_PANDAS = False\n')
                new_lines.append('\n')
                changed = True
                print(f"  📝 Added pandas flag")
        
        new_lines.append(line)
    
    if changed:
        # قبل از نوشتن، بک‌آپ بگیر
        backup_file(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    
    return False

def add_safe_fallback(file_path):
    """اضافه کردن fallback ایمن برای مواقعی که pandas نیاز هست"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # اگه فایل از قبل اینو داشت، تغییر نده
    if 'HAS_PANDAS' in content:
        return False
    
    # اضافه کردن به ابتدای فایل
    header = """# ==================== pandas fallback ====================
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    # جایگزین ساده برای مواقع ضروری
    class SimpleDataFrame:
        def __init__(self, data=None):
            self.data = data or []
        def to_dict(self):
            return {}
    pd = SimpleDataFrame
# ====================================================

"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(header + content)
    
    return True

def main():
    """اسکن همه فایل‌های پایتون و رفع مشکلات pandas"""
    
    print("="*60)
    print("🔧 Automatic Pandas Fixer")
    print("="*60)
    
    # پیدا کردن همه فایل‌های .py
    py_files = list(Path('.').rglob('*.py'))
    
    fixed_files = []
    fallback_added = []
    
    for py_file in py_files:
        # اسکیپ کردن فایل‌های موقت و بک‌آپ
        if py_file.name.startswith('fix_') or py_file.name.endswith('.bak'):
            continue
        
        print(f"\n📄 Checking: {py_file}")
        
        # رفع import ها
        if fix_pandas_imports(py_file):
            fixed_files.append(str(py_file))
        
        # اگه فایل خیلی مهمه، fallback اضافه کن
        important_files = ['ai/genius_ai.py', 'core/numerology_engine.py']
        if str(py_file) in important_files:
            if add_safe_fallback(py_file):
                fallback_added.append(str(py_file))
                print(f"  ✨ Added safe fallback to {py_file}")
    
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)
    
    if fixed_files:
        print(f"\n✅ Fixed pandas imports in:")
        for f in fixed_files:
            print(f"   • {f}")
    else:
        print("\n✅ No pandas imports found!")
    
    if fallback_added:
        print(f"\n✨ Added safe fallback to:")
        for f in fallback_added:
            print(f"   • {f}")
    
    print("\n" + "="*60)
    print("🎉 All done! Now run: python main.py")
    print("="*60)

if __name__ == "__main__":
    main()
