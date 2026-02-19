# update_config.py
"""
ابزار به‌روزرسانی تنظیمات ربات
"""

import os
import re
from pathlib import Path

def update_wallet_address(new_address: str):
    """به‌روزرسانی آدرس کیف پول در config.py"""
    
    config_file = Path("config.py")
    if not config_file.exists():
        print("❌ config.py not found!")
        return False
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    # جایگزینی آدرس
    pattern = r'PRIMARY_WALLET\s*=\s*"[^"]*"'
    replacement = f'PRIMARY_WALLET = "{new_address}"'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, replacement, content)
        
        with open(config_file, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Wallet address updated to: {new_address}")
        return True
    else:
        print("❌ PRIMARY_WALLET not found in config.py")
        return False

def update_api_key(api_name: str, new_key: str):
    """به‌روزرسانی API key"""
    
    config_file = Path("config.py")
    if not config_file.exists():
        print("❌ config.py not found!")
        return False
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    # پیدا کردن API key
    pattern = rf'{api_name}\s*=\s*"[^"]*"'
    replacement = f'{api_name} = "{new_key}"'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, replacement, content)
        
        with open(config_file, 'w') as f:
            f.write(new_content)
        
        print(f"✅ {api_name} updated")
        return True
    else:
        print(f"❌ {api_name} not found in config.py")
        return False

def show_current_config():
    """نمایش تنظیمات فعلی"""
    
    config_file = Path("config.py")
    if not config_file.exists():
        print("❌ config.py not found!")
        return
    
    with open(config_file, 'r') as f:
        content = f.read()
    
    # استخراج مقادیر مهم
    patterns = {
        'PRIMARY_WALLET': r'PRIMARY_WALLET\s*=\s*"([^"]*)"',
        'COINGECKO_API_KEY': r'COINGECKO_API_KEY\s*=\s*"([^"]*)"',
        'NEWS_API_KEY': r'NEWS_API_KEY\s*=\s*"([^"]*)"',
        'ETHERSCAN_API_KEY': r'ETHERSCAN_API_KEY\s*=\s*"([^"]*)"'
    }
    
    print("\n📋 Current Configuration:")
    print("="*50)
    
    for name, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            value = match.group(1)
            # ماسک کردن کلیدهای طولانی
            if len(value) > 10:
                value = value[:6] + "..." + value[-4:]
            print(f"{name}: {value}")
    
    print("="*50)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Update bot configuration")
    parser.add_argument("--show", action="store_true", help="Show current config")
    parser.add_argument("--wallet", help="Update wallet address")
    parser.add_argument("--coingecko", help="Update CoinGecko API key")
    parser.add_argument("--newsapi", help="Update NewsAPI key")
    parser.add_argument("--etherscan", help="Update Etherscan API key")
    
    args = parser.parse_args()
    
    if args.show:
        show_current_config()
    
    if args.wallet:
        update_wallet_address(args.wallet)
    
    if args.coingecko:
        update_api_key("COINGECKO_API_KEY", args.coingecko)
    
    if args.newsapi:
        update_api_key("NEWS_API_KEY", args.newsapi)
    
    if args.etherscan:
        update_api_key("ETHERSCAN_API_KEY", args.etherscan)
