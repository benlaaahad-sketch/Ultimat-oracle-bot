#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت تست نهایی قبل از push به GitHub
- چک کردن syntax همه فایل‌ها
- چک کردن کتابخونه‌های مورد نیاز
- رفع خودکار خطای indentation
- تست import ها
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

# رنگ‌ها برای خروجی
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
NC = '\033[0m'

def print_step(step):
    print(f"\n{BLUE}▶ {step}{NC}")

def print_success(msg):
    print(f"  {GREEN}✅ {msg}{NC}")

def print_error(msg):
    print(f"  {RED}❌ {msg}{NC}")

def print_warning(msg):
    print(f"  {YELLOW}⚠️ {msg}{NC}")

def fix_indentation_forever():
    """رفع قطعی مشکل indentation"""
    print_step("رفع مشکل indentation در فایل ultimate_bot.py")
    
    file_path = "bot/ultimate_bot.py"
    if not os.path.exists(file_path):
        print_error(f"فایل {file_path} پیدا نشد!")
        return False
    
    # بک‌آپ
    backup_path = file_path + ".pre_test.bak"
    os.system(f"cp {file_path} {backup_path}")
    print_success(f"بک‌آپ گرفته شد: {backup_path}")
    
    # خوندن فایل
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    changed = False
    # اصلاح خط 1261 و 1262
    for i, line in enumerate(lines):
        if i == 1260:  # خط 1261
            if 'webhook_thread = threading.Thread' in line:
                lines[i] = '        webhook_thread = threading.Thread(target=self._run_webhook_server, daemon=True)\n'
                changed = True
                print_success(f"خط 1261 اصلاح شد")
        elif i == 1261:  # خط 1262
            if 'webhook_thread.start()' in line:
                lines[i] = '        webhook_thread.start()\n'
                changed = True
                print_success(f"خط 1262 اصلاح شد")
    
    if changed:
        with open(file_path, 'w') as f:
            f.writelines(lines)
        print_success("فایل با موفقیت اصلاح شد")
    else:
        print_success("خطوط مورد نظر پیدا نشدند یا قبلاً اصلاح شده‌اند")
    
    return True

def check_syntax():
    """چک کردن syntax همه فایل‌های پایتون"""
    print_step("چک کردن syntax همه فایل‌ها")
    
    python_files = []
    for root, dirs, files in os.walk('.'):
        if 'venv' in dirs or 'oracle_env' in dirs or '__pycache__' in dirs or '.git' in dirs:
            dirs[:] = [d for d in dirs if d not in ['venv', 'oracle_env', '__pycache__', '.git']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        print_error("هیچ فایل پایتونی پیدا نشد!")
        return False
    
    all_good = True
    for py_file in python_files:
        result = subprocess.run(['python', '-m', 'py_compile', py_file], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"{py_file}")
        else:
            print_error(f"{py_file}")
            print(result.stderr)
            all_good = False
    
    return all_good

def check_requirements():
    """چک کردن وجود همه کتابخونه‌های مورد نیاز"""
    print_step("چک کردن کتابخونه‌های مورد نیاز")
    
    required_packages = [
        'telegram',
        'sqlalchemy',
        'alembic',
        'dotenv',
        'web3',
        'eth_account',
        'ccxt',
        'pycoingecko',
        'requests',
        'aiohttp',
        'bs4',
        'numpy',
        'pandas',
        'sklearn',
        'nltk',
        'textblob',
        'vaderSentiment',
        'transformers',
        'tensorflow',
        'xgboost',
        'lightgbm',
        'prophet',
        'statsmodels',
        'dateutil'
    ]
    
    installed = []
    missing = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    if installed:
        print_success(f"نصب شده: {len(installed)} کتابخونه")
    
    if missing:
        print_error(f"نصب نشده: {len(missing)} کتابخونه")
        for pkg in missing:
            print(f"    - {pkg}")
        return False
    
    return True

def check_main_imports():
    """تست import فایل اصلی"""
    print_step("تست import فایل اصلی")
    
    try:
        sys.path.insert(0, os.getcwd())
        from bot.ultimate_bot import UltimateBot
        print_success("import UltimateBot موفقیت‌آمیز بود")
        
        # تست instantiation
        bot = UltimateBot()
        print_success("ایجاد instance از UltimateBot موفقیت‌آمیز بود")
        
        return True
    except Exception as e:
        print_error(f"خطا در import: {e}")
        return False

def check_webhook_url():
    """چک کردن آدرس webhook"""
    print_step("چک کردن آدرس webhook در فایل‌ها")
    
    webhook_urls = []
    
    for root, dirs, files in os.walk('.'):
        if 'venv' in dirs or 'oracle_env' in dirs or '__pycache__' in dirs or '.git' in dirs:
            continue
        for file in files:
            if file.endswith('.py') or file.endswith('.json'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if 'web-production-1302b.up.railway.app' in content:
                            webhook_urls.append(filepath)
                except:
                    pass
    
    if webhook_urls:
        print_success(f"آدرس webhook در {len(webhook_urls)} فایل یافت شد")
        for f in webhook_urls:
            print(f"    - {f}")
    else:
        print_warning("آدرس webhook در فایل‌ها یافت نشد")
    
    return True

def create_final_requirements():
    """ایجاد فایل requirements نهایی"""
    print_step("ایجاد فایل requirements نهایی")
    
    requirements = """# Core
python-telegram-bot==20.7
sqlalchemy==2.0.23
alembic==1.12.1
python-dotenv==1.0.0

# Web3
web3==6.15.0
eth-account==0.11.0
ccxt==4.2.9
pycoingecko==3.1.0

# HTTP & Scraping
requests==2.31.0
aiohttp==3.9.1
beautifulsoup4==4.12.2

# Data Science
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.2
joblib==1.3.2
threadpoolctl==3.2.0

# NLP
nltk==3.8.1
textblob==0.17.1
vaderSentiment==3.3.2
transformers==4.35.2
torch==2.1.0
sentence-transformers==2.2.2

# ML
tensorflow==2.13.0
xgboost==2.0.3
lightgbm==4.3.0

# Time Series
prophet==1.1.5
statsmodels==0.14.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3
"""
    
    with open('requirements-final.txt', 'w') as f:
        f.write(requirements)
    
    print_success("فایل requirements-final.txt ایجاد شد")
    return True

def main():
    """اجرای همه تست‌ها"""
    print("="*60)
    print("🔍 اسکریپت تست نهایی قبل از push")
    print("="*60)
    
    tests = [
        ("رفع indentation", fix_indentation_forever),
        ("چک کردن syntax", check_syntax),
        ("چک کردن کتابخونه‌ها", check_requirements),
        ("تست import", check_main_imports),
        ("چک کردن webhook", check_webhook_url),
        ("ایجاد requirements نهایی", create_final_requirements)
    ]
    
    results = []
    for name, func in tests:
        print(f"\n{BLUE}▶▶▶ {name} ◀◀◀{NC}")
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print_error(f"خطا در {name}: {e}")
            results.append((name, False))
    
    print("\n" + "="*60)
    print("📊 خلاصه نتایج")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        if result:
            print(f"{GREEN}✅ {name}{NC}")
        else:
            print(f"{RED}❌ {name}{NC}")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print(f"{GREEN}✅ همه تست‌ها با موفقیت پاس شدند! می‌توانید push کنید.{NC}")
    else:
        print(f"{RED}❌ بعضی تست‌ها failed شدند. قبل از push رفع کنید.{NC}")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
