# config.py
import os
from pathlib import Path
from datetime import datetime, timedelta

# ==================== TELEGRAM ====================
TELEGRAM_TOKEN = "7358190664:AAGMFdD6HFP0CEQx_3Hv1YCMtWzAsVWgsJk"
BOT_USERNAME = "UltimateOracleBot"
BOT_NAME = "🔮 The Ultimate Oracle"

# ==================== ADMIN ====================
ADMIN_USER_IDS = []  # بعداً با /admin آیدی خودتو اضافه می‌کنی
ADMIN_COMMANDS = [
    "/admin_panel", "/stats", "/users", "/predictions",
    "/revenue", "/broadcast", "/backup", "/restore",
    "/set_price", "/set_wallet", "/logs", "/debug"
]

# ==================== WALLET (CORRECT - VERIFIED) ====================
# ✅ این آدرس دقیق و صحیح هست:
PRIMARY_WALLET = "0xYourWalletAddress"
PRIMARY_CHAIN = "ETH"  # اتریوم

# کیف پول‌های دیگر (برای نمایش)
WALLETS = {
    "ETH": PRIMARY_WALLET,
    "BTC": "bc1qq96f7lk9d0f7k65q9vx7gh7d9v8k5h7l37qz2c",
    "SOL": "2cjXA9rV6b3Jq9kL2vX8mW5nY4pQ3rS2tAoAWNRJ",
    "BNB": PRIMARY_WALLET,  # BSC از همین آدرس استفاده می‌کنه
    "TRX": "TXYZ...",  # اگر داری اینجا بذار
    "USDT_ERC20": PRIMARY_WALLET,
    "USDC_ERC20": PRIMARY_WALLET,
}

# ==================== API KEYS ====================
COINGECKO_API_KEY = "YOUR_API_KEY"
NEWS_API_KEY = "6b0fc77978664ed695d2a69e68d89f38"

# API Keys که باید ثبت نام کنی (رایگان)
ETHERSCAN_API_KEY = ""  # https://etherscan.io/register
BSCSCAN_API_KEY = ""    # https://bscscan.com/register
INFURA_PROJECT_ID = ""  # https://infura.io/register
MORALIS_API_KEY = ""    # https://moralis.io/register
TWITTER_BEARER_TOKEN = ""  # https://developer.twitter.com
REDDIT_CLIENT_ID = ""   # https://www.reddit.com/prefs/apps
REDDIT_CLIENT_SECRET = ""

# ==================== BLOCKCHAIN RPC ====================
ETH_RPC = f"https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}" if INFURA_PROJECT_ID else "https://cloudflare-eth.com"
BSC_RPC = "https://bsc-dataseed.binance.org"
POLYGON_RPC = "https://polygon-rpc.com"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
AVALANCHE_RPC = "https://api.avax.network/ext/bc/C/rpc"
ARBITRUM_RPC = "https://arb1.arbitrum.io/rpc"
OPTIMISM_RPC = "https://mainnet.optimism.io"

# ==================== PRICING (USDT) ====================
PRICING = {
    "basic_prediction": 0.32,      # پیش‌بینی ساده
    "deep_analysis": 0.99,          # تحلیل عمیق با گزارش کامل
    "whale_alert": 4.99,            # هشدار نهنگ‌ها (ماهانه)
    "monthly_api": 9.99,             # دسترسی به API ربات
    "vip_monthly": 29.99,            # عضویت VIP (همه چیز)
    "lifetime_access": 99.99,        # دسترسی مادام‌العمر
    "custom_query": 1.99,             # سوال دلخواه
}

# ==================== PAYMENT VERIFICATION ====================
PAYMENT_CONFIRMATIONS_NEEDED = 2  # تعداد بلاک‌های تایید
PAYMENT_POLL_INTERVAL = 60  # ثانیه
PAYMENT_EXPIRY_HOURS = 24  # اعتبار لینک پرداخت
AUTO_VERIFY_PAYMENTS = True
SCAN_DEPTH_BLOCKS = 5000  # عمق اسکن بلاکچین

# ==================== PATHS ====================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MEMORY_DIR = BASE_DIR / "memory"
BOOKS_DIR = BASE_DIR / "books"
BACKUP_DIR = BASE_DIR / "backups"
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
MODELS_DIR = BASE_DIR / "models"

for dir_path in [DATA_DIR, LOGS_DIR, MEMORY_DIR, BOOKS_DIR, BACKUP_DIR, KNOWLEDGE_DIR, MODELS_DIR]:
    dir_path.mkdir(exist_ok=True)

# ==================== DATABASE ====================
DATABASE_URL = f"sqlite:///{DATA_DIR}/oracle.db"
SQLALCHEMY_ECHO = False  # True برای دیباگ

# ==================== AI & MACHINE LEARNING ====================
AI_MODEL = "gpt2-medium"  # یا "gpt2-large" برای کیفیت بهتر
LEARNING_RATE = 0.001
MEMORY_RETENTION_DAYS = 365  # حافظه یک ساله
AUTO_LEARN = True
CONTINUOUS_IMPROVEMENT = True
ENSEMBLE_VOTING = True  # رای‌گیری چند مدل
DEEP_LEARNING_ENABLED = True
REINFORCEMENT_LEARNING = True  # یادگیری تقویتی از نتایج

# ==================== NUMEROLOGY ====================
MASTER_NUMBERS = [11, 22, 33, 44, 55, 66, 77, 88, 99]
KARMIC_NUMBERS = [13, 14, 16, 19, 26]
ANGEL_NUMBERS = [111, 222, 333, 444, 555, 666, 777, 888, 999, 1111]
PYTHAGOREAN_SYSTEM = True
CHALDEAN_SYSTEM = True
CABBALISTIC_SYSTEM = True

# ==================== FEATURES ====================
FEATURES = {
    "crypto_prediction": True,        # پیش‌بینی ارز
    "meme_coin_analysis": True,       # تحلیل میم‌کوین
    "token_address_scan": True,        # اسکن با آدرس توکن
    "sports_prediction": True,         # پیش‌بینی ورزشی
    "event_prediction": True,          # پیش‌بینی رویداد
    "weather_prediction": True,        # پیش‌بینی آب و هوا
    "politics_prediction": True,       # پیش‌بینی سیاسی
    "financial_markets": True,         # بازارهای مالی
    "lottery_numbers": True,           # اعداد شانس
    "compatibility": True,              # سازگاری عشقی/کاری
    "dream_interpretation": True,       # تعبیر خواب
    "tarot_reading": True,              # تاروت
    "astrology": True,                   # طالع‌بینی
}

# ==================== MARKETING ====================
REFERRAL_BONUS_PERCENT = 10  # 10% پاداش معرفی
DAILY_TWEETS = 5
AUTO_PROMOTE_INTERVAL = 3600  # ثانیه
MARKETING_CHANNELS = ["telegram", "twitter", "reddit", "instagram"]
WELCOME_BONUS = 0.32  # USDT شارژ اولیه

# ==================== BACKUP ====================
BACKUP_INTERVAL_HOURS = 24
KEEP_BACKUPS_DAYS = 7
AUTO_BACKUP = True
BACKUP_TO_CLOUD = False  # برای آینده

# ==================== LOGGING ====================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
