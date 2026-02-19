# database/models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey, LargeBinary, BigInteger, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
import os
from config import DATABASE_URL

Base = declarative_base()

class User(Base):
    """کاربران ربات"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    language = Column(String(10), default='en')
    
    # اطلاعات عددشناسی
    birth_date = Column(String(20))
    birth_time = Column(String(10))
    birth_location = Column(String(500))
    full_name = Column(String(500))
    
    # اعداد محاسبه شده
    life_path = Column(Integer)
    expression = Column(Integer)
    soul_urge = Column(Integer)
    personality = Column(Integer)
    birthday_num = Column(Integer)
    maturity = Column(Integer)
    
    # مالی
    balance = Column(Float, default=0.0)
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    
    # اشتراک
    subscription_tier = Column(String(20), default='free')  # free, basic, premium, vip
    subscription_expiry = Column(DateTime)
    api_access = Column(Boolean, default=False)
    api_key = Column(String(64), unique=True)
    
    # سیستم معرفی
    referral_code = Column(String(20), unique=True)
    referred_by_id = Column(Integer, ForeignKey('users.id'))
    referral_earnings = Column(Float, default=0.0)
    total_referrals = Column(Integer, default=0)
    
    # وضعیت
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    
    # آمار
    last_active = Column(DateTime, default=datetime.utcnow)
    last_prediction = Column(DateTime)
    last_deposit = Column(DateTime)
    total_deposits = Column(Float, default=0.0)
    total_withdrawals = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    referrals = relationship("User", backref="referrer", remote_side=[id])
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_telegram', telegram_id),
        Index('idx_user_referral', referral_code),
    )

class Prediction(Base):
    """پیش‌بینی‌ها"""
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # نوع پیش‌بینی
    pred_type = Column(String(50), nullable=False)  # crypto, sports, event, custom
    sub_type = Column(String(50))  # meme_coin, football, election, weather
    
    # ورودی کاربر
    query = Column(Text)
    input_data = Column(JSON)  # ذخیره تمام پارامترهای ورودی
    
    # برای تحلیل توکن
    token_address = Column(String(255))
    token_symbol = Column(String(50))
    chain = Column(String(50))  # ethereum, bsc, solana, polygon
    token_data = Column(JSON)  # داده‌های کامل توکن
    
    # برای ورزش
    sport_type = Column(String(50))
    team1 = Column(String(255))
    team2 = Column(String(255))
    event_date = Column(DateTime)
    league = Column(String(255))
    
    # نتایج عددشناسی
    primary_number = Column(Integer)
    secondary_numbers = Column(JSON)
    numerological_score = Column(Float)
    numerological_interpretation = Column(Text)
    
    # نتایج AI/ML
    ai_confidence = Column(Float)
    ml_prediction = Column(Float)
    ensemble_score = Column(Float)
    ai_analysis = Column(Text)
    
    # داده‌های خارجی
    external_data = Column(JSON)  # کش داده‌های دریافتی
    news_sentiment = Column(Float)
    social_sentiment = Column(Float)
    market_data = Column(JSON)
    
    # نتیجه نهایی پیش‌بینی
    final_prediction = Column(JSON)  # نتیجه ترکیبی
    recommendation = Column(String(255))
    confidence_level = Column(String(20))  # very_low, low, medium, high, very_high
    
    # هزینه
    cost = Column(Float)
    paid = Column(Boolean, default=False)
    
    # زمان‌بندی
    predicted_at = Column(DateTime, default=datetime.utcnow)
    target_date = Column(DateTime)  # تاریخی که پیش‌بینی برای اونه
    occurred_at = Column(DateTime)  # زمانی که اتفاق افتاد
    
    # ارزیابی
    actual_outcome = Column(JSON)
    was_correct = Column(Boolean)
    accuracy_score = Column(Float)
    user_rating = Column(Integer)  # 1-5
    
    # متادیتا
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    user = relationship("User", back_populates="predictions")
    feedback = relationship("Feedback", uselist=False, back_populates="prediction", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_prediction_user', user_id),
        Index('idx_prediction_type', pred_type),
        Index('idx_prediction_date', predicted_at),
        Index('idx_prediction_token', token_address),
    )

class Transaction(Base):
    """تراکنش‌های مالی"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    tx_type = Column(String(20), nullable=False)  # deposit, withdrawal, payment, subscription, referral_bonus
    tx_hash = Column(String(255), unique=True)  # هش تراکنش در بلاکچین
    amount = Column(Float, nullable=False)
    currency = Column(String(20), default='USDT')
    
    # اطلاعات بلاکچین
    chain = Column(String(20))  # ethereum, bsc, tron, solana
    from_address = Column(String(255))
    to_address = Column(String(255))
    block_number = Column(Integer)
    confirmations = Column(Integer, default=0)
    
    # وضعیت
    status = Column(String(20), default='pending')  # pending, confirmed, failed, expired
    description = Column(String(500))
    
    # برای خرید
    prediction_id = Column(Integer, ForeignKey('predictions.id'))
    subscription_tier = Column(String(20))
    
    # زمان
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # روابط
    user = relationship("User", back_populates="transactions")
    prediction = relationship("Prediction")
    
    __table_args__ = (
        Index('idx_transaction_user', user_id),
        Index('idx_transaction_hash', tx_hash),
        Index('idx_transaction_status', status),
    )

class TokenAnalysis(Base):
    """تحلیل توکن‌ها"""
    __tablename__ = 'token_analyses'
    
    id = Column(Integer, primary_key=True)
    token_address = Column(String(255), nullable=False, index=True)
    chain = Column(String(50), nullable=False)
    
    # اطلاعات پایه
    symbol = Column(String(50))
    name = Column(String(255))
    decimals = Column(Integer)
    total_supply = Column(Float)
    circulating_supply = Column(Float)
    
    # توکنومیکس
    holders_count = Column(Integer)
    creator_address = Column(String(255))
    creation_timestamp = Column(DateTime)
    creation_block = Column(Integer)
    
    # امنیت
    is_verified = Column(Boolean)
    is_honeypot = Column(Boolean)
    has_blacklist = Column(Boolean)
    has_whitelist = Column(Boolean)
    can_pause = Column(Boolean)
    can_mint = Column(Boolean)
    can_burn = Column(Boolean)
    has_owner = Column(Boolean)
    renounced = Column(Boolean)
    
    # نقدینگی
    liquidity_usd = Column(Float)
    liquidity_locked = Column(Boolean)
    liquidity_lock_until = Column(DateTime)
    lp_holders = Column(JSON)
    lp_holder_percent = Column(Float)
    
    # معاملات
    buy_tax = Column(Float)
    sell_tax = Column(Float)
    max_tx_amount = Column(Float)
    max_wallet_amount = Column(Float)
    
    # قیمت
    price_usd = Column(Float)
    price_change_5m = Column(Float)
    price_change_1h = Column(Float)
    price_change_24h = Column(Float)
    volume_5m = Column(Float)
    volume_1h = Column(Float)
    volume_24h = Column(Float)
    
    # عددشناسی
    numerological_score = Column(Float)
    lucky_number = Column(Integer)
    angel_number = Column(Integer)
    numerological_analysis = Column(Text)
    
    # خطر
    risk_level = Column(String(20))  # very_low, low, medium, high, very_high
    risk_factors = Column(JSON)
    
    # زمان
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    last_update = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_token_address', token_address),
        Index('idx_token_symbol', symbol),
    )

class Feedback(Base):
    """بازخورد کاربران"""
    __tablename__ = 'feedbacks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    prediction_id = Column(Integer, ForeignKey('predictions.id'), nullable=False)
    
    rating = Column(Integer)  # 1-5
    comment = Column(Text)
    was_correct = Column(Boolean)
    actual_result = Column(JSON)
    correction_data = Column(JSON)  # اگر کاربر اطلاعات اصلاحی داره
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="feedbacks")
    prediction = relationship("Prediction", back_populates="feedback")

class Notification(Base):
    """اعلان‌ها"""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    title = Column(String(255))
    message = Column(Text)
    notification_type = Column(String(50))  # info, success, warning, error, promo
    link = Column(String(500))
    
    read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="notifications")
    
    __table_args__ = (
        Index('idx_notification_user', user_id),
        Index('idx_notification_read', read),
    )

class LearningMemory(Base):
    """حافظه بلندمدت هوش مصنوعی"""
    __tablename__ = 'learning_memory'
    
    id = Column(Integer, primary_key=True)
    
    memory_type = Column(String(50))  # pattern, correlation, rule, insight
    category = Column(String(50))  # crypto, sports, event
    
    # الگو
    input_pattern = Column(JSON)  # شرایط ورودی
    output_pattern = Column(JSON)  # نتیجه
    confidence = Column(Float)  # 0-1
    
    # آمار
    occurrences = Column(Integer, default=1)
    success_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    success_rate = Column(Float)
    
    # زمان
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    last_verified = Column(DateTime)
    
    # متادیتا
    verified_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    tags = Column(JSON)  # برچسب‌ها برای جستجو
    
    __table_args__ = (
        Index('idx_memory_type', memory_type),
        Index('idx_memory_success', success_rate),
    )

class Book(Base):
    """کتاب‌های مرجع عددشناسی"""
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    author = Column(String(300))
    year = Column(Integer)
    
    # محتوا
    content = Column(Text)
    chapters = Column(JSON)
    summary = Column(Text)
    
    # برداری‌سازی برای جستجوی معنایی
    embedding = Column(LargeBinary)  # ذخیره embedding با pickle
    
    # آمار
    total_pages = Column(Integer)
    language = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teachings = relationship("Teaching", back_populates="book", cascade="all, delete-orphan")

class Teaching(Base):
    """آموزه‌های استخراج شده از کتاب‌ها"""
    __tablename__ = 'teachings'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    
    number_value = Column(Integer)  # عدد مرتبط
    teaching_type = Column(String(50))  # meaning, interpretation, magic_square, gematria
    title = Column(String(500))
    content = Column(Text)
    
    keywords = Column(String(1000))  # کلمات کلیدی
    page_reference = Column(Integer)
    confidence = Column(Float, default=1.0)
    
    # برداری‌سازی
    embedding = Column(LargeBinary)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    book = relationship("Book", back_populates="teachings")

class NumberMeaning(Base):
    """معانی کامل اعداد"""
    __tablename__ = 'number_meanings'
    
    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=True, nullable=False)
    
    # معانی از سیستم‌های مختلف
    pythagorean = Column(Text)
    chaldean = Column(Text)
    cabbalistic = Column(Text)
    vedic = Column(Text)
    chinese = Column(Text)
    
    # ویژگی‌ها
    positive_traits = Column(Text)
    negative_traits = Column(Text)
    career = Column(Text)
    love = Column(Text)
    health = Column(Text)
    spirituality = Column(Text)
    money = Column(Text)
    
    # تطابق‌ها
    planet = Column(String(50))
    element = Column(String(50))
    color = Column(String(50))
    crystal = Column(String(100))
    tarot_card = Column(String(100))
    angel = Column(String(100))
    day_of_week = Column(String(20))
    
    # ارتعاش
    vibration = Column(String(50))
    frequency = Column(Float)
    
    # اعداد خاص
    is_master = Column(Boolean, default=False)
    is_karmic = Column(Boolean, default=False)
    is_angel = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketSentiment(Base):
    """احساسات بازار از شبکه‌های اجتماعی"""
    __tablename__ = 'market_sentiment'
    
    id = Column(Integer, primary_key=True)
    
    source = Column(String(50))  # twitter, reddit, telegram, news
    keyword = Column(String(255))
    
    sentiment_score = Column(Float)  # -1 to 1
    magnitude = Column(Float)
    volume = Column(Integer)  # تعداد پست‌ها
    
    top_posts = Column(JSON)
    influencers = Column(JSON)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_sentiment_keyword', keyword),
        Index('idx_sentiment_time', timestamp),
    )

# ==================== Database Setup ====================
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """دریافت session دیتابیس"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """ایجاد جداول و داده‌های اولیه"""
    Base.metadata.create_all(engine)
    
    # ایجاد معانی پایه اعداد اگر وجود ندارن
    db = SessionLocal()
    if db.query(NumberMeaning).count() == 0:
        basic_meanings = [
            {"number": 1, "pythagorean": "Leadership, independence, originality", "planet": "Sun", "element": "Fire", "color": "Gold"},
            {"number": 2, "pythagorean": "Cooperation, diplomacy, sensitivity", "planet": "Moon", "element": "Water", "color": "Silver"},
            {"number": 3, "pythagorean": "Creativity, expression, optimism", "planet": "Jupiter", "element": "Air", "color": "Purple"},
            {"number": 4, "pythagorean": "Stability, discipline, practicality", "planet": "Uranus", "element": "Earth", "color": "Blue"},
            {"number": 5, "pythagorean": "Freedom, adventure, versatility", "planet": "Mercury", "element": "Air", "color": "Yellow"},
            {"number": 6, "pythagorean": "Responsibility, love, harmony", "planet": "Venus", "element": "Earth", "color": "Green"},
            {"number": 7, "pythagorean": "Wisdom, analysis, spirituality", "planet": "Neptune", "element": "Water", "color": "Sea Green"},
            {"number": 8, "pythagorean": "Power, success, abundance", "planet": "Saturn", "element": "Earth", "color": "Black"},
            {"number": 9, "pythagorean": "Humanitarianism, completion, art", "planet": "Mars", "element": "Fire", "color": "Red"},
        ]
        for m in basic_meanings:
            db.add(NumberMeaning(**m))
        db.commit()
    
    db.close()
