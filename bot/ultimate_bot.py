# bot/ultimate_bot.py
"""
ربات اصلی تلگرام - هسته مرکزی پروژه
قابلیت‌ها:
- منوی فوق‌پیشرفته با ۱۰+ بخش
- ارتباط با همه ماژول‌ها
- سیستم پرداخت خودکار
- پنل مدیریت
- آمار لحظه‌ای
- بازاریابی خودکار
- ۱۰ زبان مختلف
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes,
    ConversationHandler, PicklePersistence
)
from telegram.constants import ParseMode
from datetime import datetime, timedelta
import asyncio
import json
import os
from typing import Dict, Any, Optional
import sys
from pathlib import Path
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import Update
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import asyncio
# اضافه کردن مسیر
sys.path.append(str(Path(__file__).parent.parent))

from core.numerology_engine import NumerologyEngine
from ai.genius_ai import GeniusAI
from web3_analyzer.token_analyzer import TokenAnalyzer
from sports_analyzer.sports_predictor import SportsPredictor
from event_analyzer.event_predictor import EventPredictor
from payment.payment_verifier import PaymentVerifier
from database.models import User, Prediction, Transaction, get_db, init_database
from config import *
from marketing.self_marketing import SelfMarketing  # بعداً می‌سازیم
from admin.admin_panel import AdminPanel  # بعداً می‌سازیم

logger = logging.getLogger(__name__)

# ==================== وضعیت‌های مکالمه ====================
(
    MAIN_MENU,
    WAITING_FOR_CRYPTO_ADDRESS,
    WAITING_FOR_SPORTS_QUERY,
    WAITING_FOR_EVENT_QUERY,
    WAITING_FOR_BIRTH_DATE,
    WAITING_FOR_FULL_NAME,
    WAITING_FOR_PAYMENT_TX,
    WAITING_FOR_CUSTOM_QUERY,
    WAITING_FOR_FEEDBACK
) = range(9)

class UltimateBot:
    """
    ربات اصلی - مغز متفکر کل پروژه
    """
    
    def __init__(self):
        # ==================== اتصال به دیتابیس ====================
        self.db = next(get_db())
        init_database()
        
        # ==================== موتورها ====================
        self.numerology = NumerologyEngine(self.db)
        self.ai = GeniusAI(self.db, self.numerology)
        self.token_analyzer = TokenAnalyzer(self.db, self.numerology, self.ai)
        self.sports_predictor = SportsPredictor(self.db, self.numerology, self.ai)
        self.event_predictor = EventPredictor(self.db, self.numerology, self.ai)
        self.payment_verifier = PaymentVerifier(self.db)
        self.marketing = SelfMarketing(self.db) if 'SelfMarketing' in dir() else None
        self.admin = AdminPanel(self.db) if 'AdminPanel' in dir() else None
        
        # ==================== کش ====================
        self.user_sessions = {}
        self.temp_data = {}
        
        # ==================== آمار ====================
        self.stats = {
            'start_time': datetime.utcnow(),
            'total_users': 0,
            'active_users': 0,
            'total_predictions': 0,
            'total_revenue': 0
        }
        
        logger.info("🤖 UltimateBot initialized with all modules")
    
    # ==================== منوهای اصلی ====================
    
    def get_main_menu(self, user_language: str = 'en') -> InlineKeyboardMarkup:
        """منوی اصلی ربات"""
        
        buttons = [
            [
                InlineKeyboardButton("🔮 Crypto Predictions", callback_data='menu_crypto'),
                InlineKeyboardButton("⚽ Sports Predictions", callback_data='menu_sports')
            ],
            [
                InlineKeyboardButton("🌍 Event Predictions", callback_data='menu_events'),
                InlineKeyboardButton("🔢 Numerology", callback_data='menu_numerology')
            ],
            [
                InlineKeyboardButton("💰 Wallet & Payments", callback_data='menu_wallet'),
                InlineKeyboardButton("📊 My Profile", callback_data='menu_profile')
            ],
            [
                InlineKeyboardButton("📚 Knowledge Base", callback_data='menu_knowledge'),
                InlineKeyboardButton("❓ Help & Support", callback_data='menu_help')
            ],
            [
                InlineKeyboardButton("⭐ VIP Features", callback_data='menu_vip'),
                InlineKeyboardButton("🎁 Referral Program", callback_data='menu_referral')
            ]
        ]
        
        # دکمه مدیریت (فقط برای ادمین‌ها)
        # if user_is_admin:  # TODO
        #     buttons.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data='menu_admin')])
        
        return InlineKeyboardMarkup(buttons)
    
    def get_crypto_menu(self) -> InlineKeyboardMarkup:
        """منوی پیش‌بینی ارز"""
        
        buttons = [
            [
                InlineKeyboardButton("🔍 Analyze Token Address", callback_data='crypto_address'),
                InlineKeyboardButton("📈 Trending Tokens", callback_data='crypto_trending')
            ],
            [
                InlineKeyboardButton("🆕 New Tokens", callback_data='crypto_new'),
                InlineKeyboardButton("🚀 Pump Prediction", callback_data='crypto_pump')
            ],
            [
                InlineKeyboardButton("💎 Top Meme Coins", callback_data='crypto_meme'),
                InlineKeyboardButton("📊 Market Overview", callback_data='crypto_market')
            ],
            [
                InlineKeyboardButton("🔙 Back to Main", callback_data='back_main')
            ]
        ]
        
        return InlineKeyboardMarkup(buttons)
    
    def get_sports_menu(self) -> InlineKeyboardMarkup:
        """منوی پیش‌بینی ورزشی"""
        
        sports = [
            ("⚽ Football", "sport_football"),
            ("🏀 Basketball", "sport_basketball"),
            ("🎾 Tennis", "sport_tennis"),
            ("🏈 American Football", "sport_american_football"),
            ("⚾ Baseball", "sport_baseball"),
            ("🏒 Hockey", "sport_hockey"),
            ("🥊 Boxing", "sport_boxing"),
            ("🥋 MMA", "sport_mma"),
            ("🏎️ F1", "sport_f1"),
            ("🎮 Esports", "sport_esports")
        ]
        
        buttons = []
        row = []
        for i, (name, callback) in enumerate(sports):
            row.append(InlineKeyboardButton(name, callback_data=callback))
            if (i + 1) % 2 == 0:
                buttons.append(row)
                row = []
        
        if row:
            buttons.append(row)
        
        buttons.append([InlineKeyboardButton("🔙 Back to Main", callback_data='back_main')])
        
        return InlineKeyboardMarkup(buttons)
    
    def get_events_menu(self) -> InlineKeyboardMarkup:
        """منوی پیش‌بینی رویدادها"""
        
        buttons = [
            [
                InlineKeyboardButton("🗳️ Elections", callback_data='event_elections'),
                InlineKeyboardButton("📊 Economy", callback_data='event_economy')
            ],
            [
                InlineKeyboardButton("🌤️ Weather", callback_data='event_weather'),
                InlineKeyboardButton("🏆 Awards", callback_data='event_awards')
            ],
            [
                InlineKeyboardButton("💻 Technology", callback_data='event_tech'),
                InlineKeyboardButton("🎬 Entertainment", callback_data='event_entertainment')
            ],
            [
                InlineKeyboardButton("✨ Custom Event", callback_data='event_custom'),
                InlineKeyboardButton("📈 Trends", callback_data='event_trends')
            ],
            [
                InlineKeyboardButton("🔙 Back to Main", callback_data='back_main')
            ]
        ]
        
        return InlineKeyboardMarkup(buttons)
    
    def get_numerology_menu(self) -> InlineKeyboardMarkup:
        """منوی عددشناسی"""
        
        buttons = [
            [
                InlineKeyboardButton("📅 Life Path", callback_data='num_life_path'),
                InlineKeyboardButton("📝 Name Number", callback_data='num_name')
            ],
            [
                InlineKeyboardButton("❤️ Compatibility", callback_data='num_compatibility'),
                InlineKeyboardButton("🔢 Personal Day", callback_data='num_personal_day')
            ],
            [
                InlineKeyboardButton("🔄 Gematria", callback_data='num_gematria'),
                InlineKeyboardButton("📊 Full Report", callback_data='num_report')
            ],
            [
                InlineKeyboardButton("🔙 Back to Main", callback_data='back_main')
            ]
        ]
        
        return InlineKeyboardMarkup(buttons)
    
    def get_wallet_menu(self) -> InlineKeyboardMarkup:
        """منوی کیف پول"""
        
        buttons = [
            [
                InlineKeyboardButton("💰 Check Balance", callback_data='wallet_balance'),
                InlineKeyboardButton("📥 Deposit", callback_data='wallet_deposit')
            ],
            [
                InlineKeyboardButton("📤 Withdraw", callback_data='wallet_withdraw'),
                InlineKeyboardButton("📊 Transactions", callback_data='wallet_txs')
            ],
            [
                InlineKeyboardButton("⭐ Buy VIP", callback_data='wallet_vip'),
                InlineKeyboardButton("🎁 Redeem Code", callback_data='wallet_redeem')
            ],
            [
                InlineKeyboardButton("🔙 Back to Main", callback_data='back_main')
            ]
        ]
        
        return InlineKeyboardMarkup(buttons)
    
    # ==================== هندلرهای اصلی ====================
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """شروع ربات"""
        
        user = update.effective_user
        logger.info(f"User {user.id} (@{user.username}) started the bot")
        
        # ثبت یا به‌روزرسانی کاربر
        db_user = self.db.query(User).filter_by(telegram_id=user.id).first()
        
        if not db_user:
            db_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                balance=WELCOME_BONUS,  # هدیه خوش‌آمدگویی
                referral_code=self._generate_referral_code(user.id)
            )
            self.db.add(db_user)
            self.db.commit()
            
            welcome_bonus_text = f"\n\n🎁 You received **${WELCOME_BONUS}** as welcome bonus!"
            self.stats['total_users'] += 1
        else:
            welcome_bonus_text = ""
            db_user.last_active = datetime.utcnow()
            self.db.commit()
        
        # آمار
        self.stats['active_users'] += 1
        
        # پیام خوش‌آمدگویی
        welcome_text = (
            f"✨ **Welcome to The Ultimate Oracle, {user.first_name}!** ✨\n\n"
            f"I am the world's most advanced prediction bot, combining:\n"
            f"🔮 **Ancient Numerology** (Pythagorean, Chaldean, Cabbalistic)\n"
            f"🧠 **Advanced AI** with 10+ machine learning models\n"
            f"🌐 **Real-time Data** from 20+ APIs\n"
            f"📚 **Sacred Texts** from 3 ancient books\n\n"
            f"**I can predict:**\n"
            f"• Any meme coin with just the contract address\n"
            f"• Sports matches in 15+ disciplines\n"
            f"• Elections, awards, weather, and any event\n"
            f"• Your personal numerology and destiny\n"
            f"{welcome_bonus_text}\n\n"
            f"**Price per prediction:** ${PRICING['basic_prediction']}\n"
            f"**VIP access:** ${PRICING['vip_monthly']}/month\n\n"
            f"👇 **Choose from the menu below:**"
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=self.get_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        # بازاریابی خودکار
        if self.marketing:
            asyncio.create_task(self.marketing.on_new_user(db_user))
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت کلیک روی دکمه‌ها"""
        
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        # ==================== منوی اصلی ====================
        
        if data == 'back_main':
            await query.edit_message_text(
                "✨ **Main Menu** ✨\n\nChoose an option:",
                reply_markup=self.get_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ==================== منوی کریپتو ====================
        
        elif data == 'menu_crypto':
            await query.edit_message_text(
                "🔮 **Crypto Predictions**\n\n"
                "Choose an option below:",
                reply_markup=self.get_crypto_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == 'crypto_address':
            await query.edit_message_text(
                "🔍 **Analyze Token by Address**\n\n"
                "Please send me the **contract address** of the token.\n\n"
                "Supported chains:\n"
                "• Ethereum (0x...)\n"
                "• BSC (0x...)\n"
                "• Polygon (0x...)\n"
                "• Solana (base58...)\n"
                "• Avalanche\n"
                "• Arbitrum\n\n"
                "Example: `0x6982508145454Ce325dDbE47a25d4ec3d2311933` (PEPE)",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['state'] = WAITING_FOR_CRYPTO_ADDRESS
        
        elif data == 'crypto_trending':
            await self._show_trending_tokens(query)
        
        elif data == 'crypto_new':
            await self._show_new_tokens(query)
        
        elif data == 'crypto_pump':
            await query.edit_message_text(
                "🚀 **Pump Prediction**\n\n"
                "Send me the token address to predict if it will pump:",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['state'] = WAITING_FOR_CRYPTO_ADDRESS
            context.user_data['pump_mode'] = True
        
        # ==================== منوی ورزشی ====================
        
        elif data == 'menu_sports':
            await query.edit_message_text(
                "⚽ **Sports Predictions**\n\n"
                "Choose your sport:",
                reply_markup=self.get_sports_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data.startswith('sport_'):
            sport = data.replace('sport_', '')
            await query.edit_message_text(
                f"{self.sports_predictor.get_sport_emoji(sport)} **{sport.replace('_', ' ').title()} Prediction**\n\n"
                f"Send me the match in this format:\n"
                f"`Team A vs Team B`\n\n"
                f"Examples:\n"
                f"• `Man United vs Liverpool`\n"
                f"• `Lakers vs Warriors`\n"
                f"• `Djokovic vs Alcaraz`\n\n"
                f"You can add date: `Man United vs Liverpool tomorrow`",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['state'] = WAITING_FOR_SPORTS_QUERY
            context.user_data['sport'] = sport
        
        # ==================== منوی رویدادها ====================
        
        elif data == 'menu_events':
            await query.edit_message_text(
                "🌍 **Event Predictions**\n\n"
                "Choose event type:",
                reply_markup=self.get_events_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data.startswith('event_'):
            event_type = data.replace('event_', '')
            await query.edit_message_text(
                f"{self.event_predictor.get_category_emoji(event_type)} **{event_type.title()} Prediction**\n\n"
                f"Send me your question.\n\n"
                f"Examples:\n"
                f"• `Who will win the 2024 US election?`\n"
                f"• `Will there be a market crash in 2024?`\n"
                f"• `Who will win the Oscar for Best Picture?`",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['state'] = WAITING_FOR_EVENT_QUERY
            context.user_data['event_type'] = event_type
        
        # ==================== منوی عددشناسی ====================
        
        elif data == 'menu_numerology':
            await query.edit_message_text(
                "🔢 **Numerology Calculations**\n\n"
                "Choose calculation type:",
                reply_markup=self.get_numerology_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == 'num_life_path':
            await query.edit_message_text(
                "📅 **Life Path Number**\n\n"
                "Send me your birth date in format: `YYYY-MM-DD`\n\n"
                "Example: `1990-05-15`",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['state'] = WAITING_FOR_BIRTH_DATE
        
        elif data == 'num_name':
            await query.edit_message_text(
                "📝 **Name Number**\n\n"
                "Send me your full name:\n\n"
                "Example: `John Doe`",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data['state'] = WAITING_FOR_FULL_NAME
        
        # ==================== منوی کیف پول ====================
        
        elif data == 'menu_wallet':
            await self._show_wallet(query, context)
        
        elif data == 'wallet_balance':
            await self._show_balance(query, context)
        
        elif data == 'wallet_deposit':
            await self._show_deposit_options(query, context)
        
        elif data == 'wallet_txs':
            await self._show_transactions(query, context)
        
        elif data == 'wallet_vip':
            await self._show_vip_options(query, context)
        
        # ==================== منوی پروفایل ====================
        
        elif data == 'menu_profile':
            await self._show_profile(query, context)
        
        # ==================== منوی دانش ====================
        
        elif data == 'menu_knowledge':
            await self._show_knowledge_base(query)
        
        # ==================== منوی راهنما ====================
        
        elif data == 'menu_help':
            await self._show_help(query)
        
        # ==================== منوی VIP ====================
        
        elif data == 'menu_vip':
            await self._show_vip_features(query)
        
        # ==================== منوی معرفی ====================
        
        elif data == 'menu_referral':
            await self._show_referral(query, context)
        
        # ==================== انتخاب ارز برای واریز ====================
        
        elif data.startswith('deposit_'):
            chain = data.replace('deposit_', '')
            await self._show_deposit_address(query, context, chain)
    
    # ==================== هندلر پیام‌ها ====================
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پیام‌های متنی"""
        
        user_id = update.effective_user.id
        text = update.message.text
        state = context.user_data.get('state')
        
        # دریافت کاربر از دیتابیس
        db_user = self.db.query(User).filter_by(telegram_id=user_id).first()
        if not db_user:
            await update.message.reply_text("Please use /start first.")
            return
        
        # ==================== پردازش بر اساس وضعیت ====================
        
        if state == WAITING_FOR_CRYPTO_ADDRESS:
            await self._process_crypto_address(update, context, text, db_user)
        
        elif state == WAITING_FOR_SPORTS_QUERY:
            await self._process_sports_query(update, context, text, db_user)
        
        elif state == WAITING_FOR_EVENT_QUERY:
            await self._process_event_query(update, context, text, db_user)
        
        elif state == WAITING_FOR_BIRTH_DATE:
            await self._process_birth_date(update, context, text, db_user)
        
        elif state == WAITING_FOR_FULL_NAME:
            await self._process_full_name(update, context, text, db_user)
        
        elif state == WAITING_FOR_PAYMENT_TX:
            await self._process_payment_tx(update, context, text, db_user)
        
        elif state == WAITING_FOR_CUSTOM_QUERY:
            await self._process_custom_query(update, context, text, db_user)
        
        elif state == WAITING_FOR_FEEDBACK:
            await self._process_feedback(update, context, text, db_user)
        
        else:
            await update.message.reply_text(
                "Please use the menu buttons to navigate.",
                reply_markup=self.get_main_menu()
            )
        
        # پاک کردن وضعیت
        context.user_data['state'] = None
    
    # ==================== توابع پردازش ====================
    
    async def _process_crypto_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                      address: str, db_user: User):
        """پردازش آدرس توکن"""
        
        # بررسی موجودی
        if db_user.balance < PRICING['basic_prediction'] and db_user.subscription_tier == 'free':
            await update.message.reply_text(
                f"❌ **Insufficient balance**\n\n"
                f"Price: ${PRICING['basic_prediction']}\n"
                f"Your balance: ${db_user.balance:.2f}\n\n"
                f"Please deposit using /wallet",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        await update.message.reply_text(
            f"🔍 **Analyzing token...**\n"
            f"Address: `{address[:10]}...{address[-8:]}`\n\n"
            f"⏱ This will take about 20 seconds...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # تحلیل توکن
            analysis = await self.token_analyzer.analyze_token(address)
            
            if analysis.get('status') == 'error':
                await update.message.reply_text(
                    f"❌ Error: {analysis.get('error', 'Unknown error')}"
                )
                return
            
            # پیش‌بینی پامپ
            pump_prediction = None
            if context.user_data.get('pump_mode'):
                pump_prediction = await self.token_analyzer.predict_pump(address)
            
            # کسر هزینه
            if db_user.subscription_tier == 'free':
                db_user.balance -= PRICING['basic_prediction']
                db_user.total_predictions += 1
            
            # ثبت پیش‌بینی
            pred = Prediction(
                user_id=db_user.id,
                pred_type='crypto',
                sub_type='token_analysis',
                query=address,
                token_address=address,
                chain=analysis.get('chain', 'unknown'),
                primary_number=analysis.get('numerology', {}).get('reduced_number', 0),
                numerological_score=analysis.get('numerology', {}).get('numerological_score', 50),
                ai_confidence=analysis.get('ai_prediction', {}).get('confidence', 0.5),
                interpretation=json.dumps(analysis),
                cost=PRICING['basic_prediction'] if db_user.subscription_tier == 'free' else 0
            )
            self.db.add(pred)
            self.db.commit()
            
            # ساخت پیام نتیجه
            result_text = self._format_token_analysis(analysis, pump_prediction)
            
            # دکمه‌های بعدی
            buttons = [
                [
                    InlineKeyboardButton("🔄 New Analysis", callback_data='crypto_address'),
                    InlineKeyboardButton("💰 Check Balance", callback_data='wallet_balance')
                ],
                [InlineKeyboardButton("🔙 Main Menu", callback_data='back_main')]
            ]
            
            await update.message.reply_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            
            # یادگیری AI
            asyncio.create_task(self.ai.learn_from_experience(
                {'type': 'crypto', 'address': address},
                analysis
            ))
            
        except Exception as e:
            logger.error(f"Error processing crypto address: {e}")
            await update.message.reply_text(
                f"❌ Error analyzing token: {str(e)[:200]}"
            )
    
    async def _process_sports_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   query: str, db_user: User):
        """پردازش سوال ورزشی"""
        
        # بررسی موجودی
        if db_user.balance < PRICING['basic_prediction'] and db_user.subscription_tier == 'free':
            await update.message.reply_text(
                f"❌ **Insufficient balance**\n\n"
                f"Price: ${PRICING['basic_prediction']}\n"
                f"Your balance: ${db_user.balance:.2f}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        await update.message.reply_text(
            f"⚽ **Analyzing match...**\n"
            f"Query: {query}\n\n"
            f"⏱ This will take about 15 seconds...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # پیش‌بینی مسابقه
            prediction = await self.sports_predictor.predict_match(query)
            
            if prediction.get('error'):
                await update.message.reply_text(
                    f"❌ Error: {prediction['error']}"
                )
                return
            
            # کسر هزینه
            if db_user.subscription_tier == 'free':
                db_user.balance -= PRICING['basic_prediction']
                db_user.total_predictions += 1
            
            # ثبت پیش‌بینی
            pred = Prediction(
                user_id=db_user.id,
                pred_type='sports',
                sub_type=context.user_data.get('sport', 'football'),
                query=query,
                interpretation=json.dumps(prediction),
                cost=PRICING['basic_prediction'] if db_user.subscription_tier == 'free' else 0
            )
            self.db.add(pred)
            self.db.commit()
            
            # ساخت پیام نتیجه
            result_text = self._format_sports_prediction(prediction)
            
            # دکمه‌های بعدی
            buttons = [
                [
                    InlineKeyboardButton("⚽ New Match", callback_data='menu_sports'),
                    InlineKeyboardButton("💰 Balance", callback_data='wallet_balance')
                ],
                [InlineKeyboardButton("🔙 Main", callback_data='back_main')]
            ]
            
            await update.message.reply_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error processing sports query: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)[:200]}")
    
    async def _process_event_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  query: str, db_user: User):
        """پردازش سوال رویداد"""
        
        # بررسی موجودی
        if db_user.balance < PRICING['basic_prediction'] and db_user.subscription_tier == 'free':
            await update.message.reply_text(
                f"❌ **Insufficient balance**\n\n"
                f"Price: ${PRICING['basic_prediction']}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        await update.message.reply_text(
            f"🌍 **Analyzing event...**\n"
            f"Query: {query}\n\n"
            f"⏱ This will take about 20 seconds...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # پیش‌بینی رویداد
            prediction = await self.event_predictor.predict_event(query)
            
            # کسر هزینه
            if db_user.subscription_tier == 'free':
                db_user.balance -= PRICING['basic_prediction']
                db_user.total_predictions += 1
            
            # ثبت پیش‌بینی
            pred = Prediction(
                user_id=db_user.id,
                pred_type='event',
                sub_type=context.user_data.get('event_type', 'custom'),
                query=query,
                interpretation=json.dumps(prediction),
                cost=PRICING['basic_prediction'] if db_user.subscription_tier == 'free' else 0
            )
            self.db.add(pred)
            self.db.commit()
            
            # ساخت پیام نتیجه
            result_text = self._format_event_prediction(prediction)
            
            # دکمه‌های بعدی
            buttons = [
                [
                    InlineKeyboardButton("🌍 New Event", callback_data='menu_events'),
                    InlineKeyboardButton("💰 Balance", callback_data='wallet_balance')
                ],
                [InlineKeyboardButton("🔙 Main", callback_data='back_main')]
            ]
            
            await update.message.reply_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            logger.error(f"Error processing event query: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)[:200]}")
    
    async def _process_birth_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 date_str: str, db_user: User):
        """پردازش تاریخ تولد"""
        
        try:
            # محاسبه مسیر زندگی
            result = self.numerology.calculate_life_path(date_str)
            
            # ذخیره در دیتابیس
            db_user.birth_date = date_str
            db_user.life_path = result['primary_number']
            self.db.commit()
            
            # فرمت نتیجه
            text = (
                f"📅 **Life Path Number: {result['primary_number']}**\n\n"
                f"📖 **Meaning:** {result['interpretation']['pythagorean']}\n\n"
                f"⭐ **Positive:** {result['interpretation']['positive']}\n"
                f"⚠️ **Negative:** {result['interpretation']['negative']}\n\n"
                f"🪐 **Planet:** {result['planetary_ruler']}\n"
                f"🌍 **Element:** {result['element']}\n"
                f"🎨 **Color:** {self.numerology.get_color(result['primary_number'])}\n"
                f"💎 **Crystal:** {self.numerology.get_crystal(result['primary_number'])}"
            )
            
            if result['is_master']:
                text += "\n\n✨ **This is a Master Number!**"
            if result['is_karmic']:
                text += "\n\n⚠️ **This is a Karmic Number**"
            
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error: {str(e)}\n\nPlease use format: YYYY-MM-DD"
            )
    
    async def _process_full_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                name: str, db_user: User):
        """پردازش نام کامل"""
        
        try:
            # محاسبه عدد نام
            result = self.numerology.calculate_name_number(name)
            
            # ذخیره در دیتابیس
            db_user.full_name = name
            db_user.expression = result['expression']
            db_user.soul_urge = result['soul_urge']
            db_user.personality = result['personality']
            self.db.commit()
            
            # فرمت نتیجه
            text = (
                f"📝 **Name Analysis: {name.upper()}**\n\n"
                f"🔢 **Expression (Destiny):** {result['expression']}\n"
                f"❤️ **Soul Urge (Heart's Desire):** {result['soul_urge']}\n"
                f"👤 **Personality (Outer Self):** {result['personality']}\n\n"
                f"📖 **Meaning:** {result['interpretation']['pythagorean']}\n"
            )
            
            if result['is_master']:
                text += "\n✨ **Master Number!**"
            
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    # ==================== توابع نمایش ====================
    
    def _format_token_analysis(self, analysis: Dict, pump_prediction: Dict = None) -> str:
        """فرمت‌بندی تحلیل توکن"""
        
        try:
            symbol = analysis.get('symbol', 'Unknown')
            name = analysis.get('name', 'Unknown')
            chain = analysis.get('chain', 'unknown').upper()
            
            text = f"🔮 **Token Analysis: {symbol} ({name})**\n"
            text += f"🔗 **Chain:** {chain}\n"
            text += f"📊 **Price:** ${analysis.get('price_usd', 0):.8f}\n"
            text += f"📈 **24h Change:** {analysis.get('price_change_24h', 0):.2f}%\n"
            text += f"💧 **Liquidity:** ${analysis.get('liquidity_usd', 0):,.0f}\n"
            text += f"👥 **Holders:** {analysis.get('holders_count', 0):,}\n\n"
            
            # امتیاز نهایی
            score = analysis.get('final_score', {})
            text += f"**Overall Score:** {score.get('total', 0)} ({score.get('grade', 'N/A')})\n"
            text += f"**Risk Level:** {analysis.get('risk_level', 'unknown').upper()}\n\n"
            
            # هشدارها
            warnings = analysis.get('warnings', [])
            if warnings:
                text += "⚠️ **Warnings:**\n"
                for w in warnings[:3]:
                    text += f"• {w}\n"
                text += "\n"
            
            # عددشناسی
            num = analysis.get('numerology', {})
            text += f"🔢 **Numerology:** Number {num.get('reduced_number', 0)} - {num.get('interpretation', '')}\n\n"
            
            # پیش‌بینی پامپ
            if pump_prediction:
                text += f"🚀 **Pump Prediction:** {pump_prediction.get('pump_level', 'N/A')}\n"
                text += f"📊 **Probability:** {pump_prediction.get('probability', 'N/A')}\n"
                text += f"⏱ **Timing:** {pump_prediction.get('timing', {}).get('estimated_timing', 'Unknown')}\n\n"
            
            # توصیه
            text += f"**Recommendation:** {analysis.get('recommendation', 'N/A')}"
            
            return text
            
        except Exception as e:
            logger.error(f"Error formatting token analysis: {e}")
            return "Error formatting result"
    
    def _format_sports_prediction(self, prediction: Dict) -> str:
        """فرمت‌بندی پیش‌بینی ورزشی"""
        
        try:
            match = prediction.get('match', 'Unknown')
            sport = prediction.get('sport', 'Sport')
            date = prediction.get('date', 'Not specified')
            
            text = f"⚽ **{sport} Prediction**\n"
            text += f"📅 **Match:** {match}\n"
            text += f"📆 **Date:** {date}\n\n"
            
            pred = prediction.get('prediction', {})
            text += f"**Result:** {pred.get('result', 'N/A')}\n"
            text += f"📊 **Probabilities:**\n"
            text += f"• Team 1: {pred.get('team1_prob', 0)}%\n"
            text += f"• Team 2: {pred.get('team2_prob', 0)}%\n"
            text += f"• Draw: {pred.get('draw_prob', 0)}%\n"
            text += f"🎯 **Score Prediction:** {pred.get('score', '0-0')}\n"
            text += f"✨ **Confidence:** {pred.get('confidence', 0)}%\n\n"
            
            num = prediction.get('numerology', {})
            text += f"🔢 **Numerology:** Team1: {num.get('team1_number')}, Team2: {num.get('team2_number')}, Day: {num.get('day_number')}\n\n"
            
            text += f"**Recommendation:** {prediction.get('recommendation', 'N/A')}"
            
            return text
            
        except Exception as e:
            logger.error(f"Error formatting sports prediction: {e}")
            return "Error formatting result"
    
    def _format_event_prediction(self, prediction: Dict) -> str:
        """فرمت‌بندی پیش‌بینی رویداد"""
        
        try:
            category = prediction.get('category', 'Event')
            subcategory = prediction.get('subcategory', '')
            query = prediction.get('query', '')
            
            text = f"🌍 **{category} Prediction**\n"
            if subcategory:
                text += f"📋 **Type:** {subcategory}\n"
            text += f"❓ **Question:** {query}\n\n"
            
            text += f"**Prediction:** {prediction.get('prediction', 'N/A')}\n"
            text += f"📊 **Probability:** {prediction.get('probability', 0)}%\n"
            text += f"✨ **Confidence:** {prediction.get('confidence', 0)}% ({prediction.get('confidence_level', 'N/A')})\n\n"
            
            factors = prediction.get('factors', [])
            if factors:
                text += "**Key Factors:**\n"
                for f in factors[:3]:
                    text += f"• {f}\n"
                text += "\n"
            
            timeline = prediction.get('timeline', {})
            text += f"⏱ **Timeline:** {timeline.get('estimate', 'Unknown')}\n\n"
            
            text += f"**Recommendation:** {prediction.get('recommendation', 'N/A')}"
            
            return text
            
        except Exception as e:
            logger.error(f"Error formatting event prediction: {e}")
            return "Error formatting result"
    
    async def _show_wallet(self, query, context):
        """نمایش کیف پول"""
        
        user_id = query.from_user.id
        db_user = self.db.query(User).filter_by(telegram_id=user_id).first()
        
        # آمار
        success_rate = 0
        if db_user.total_predictions > 0:
            success_rate = (db_user.correct_predictions / db_user.total_predictions) * 100
        
        text = (
            f"💰 **Your Wallet**\n\n"
            f"💵 **Balance:** ${db_user.balance:.2f}\n"
            f"📊 **Total Predictions:** {db_user.total_predictions}\n"
            f"✅ **Correct:** {db_user.correct_predictions}\n"
            f"📈 **Success Rate:** {success_rate:.1f}%\n"
            f"💎 **Subscription:** {db_user.subscription_tier.upper()}\n\n"
            f"**Prices:**\n"
            f"• Basic Prediction: ${PRICING['basic_prediction']}\n"
            f"• Deep Analysis: ${PRICING['deep_analysis']}\n"
            f"• VIP Monthly: ${PRICING['vip_monthly']}\n"
            f"• Lifetime: ${PRICING['lifetime_access']}"
        )
        
        await query.edit_message_text(
            text,
            reply_markup=self.get_wallet_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_deposit_options(self, query, context):
        """نمایش گزینه‌های واریز"""
        
        text = (
            "📥 **Deposit Funds**\n\n"
            "Choose your preferred network:\n\n"
            "• **Ethereum** (ERC20) - USDT, USDC\n"
            "• **BSC** (BEP20) - USDT, BNB\n"
            "• **Solana** - USDC, SOL\n"
            "• **Tron** (TRC20) - USDT\n"
            "• **Polygon** - USDT, USDC\n\n"
            "Minimum deposit: $5\n"
            "Confirmations needed: 2 blocks\n"
            "Estimated time: 2-5 minutes"
        )
        
        buttons = [
            [
                InlineKeyboardButton("Ethereum", callback_data='deposit_ethereum'),
                InlineKeyboardButton("BSC", callback_data='deposit_bsc')
            ],
            [
                InlineKeyboardButton("Solana", callback_data='deposit_solana'),
                InlineKeyboardButton("Tron", callback_data='deposit_tron')
            ],
            [
                InlineKeyboardButton("Polygon", callback_data='deposit_polygon'),
                InlineKeyboardButton("Bitcoin", callback_data='deposit_bitcoin')
            ],
            [InlineKeyboardButton("🔙 Back", callback_data='menu_wallet')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_deposit_address(self, query, context, chain: str):
        """نمایش آدرس واریز"""
        
        user_id = query.from_user.id
        address = self.payment_verifier.generate_payment_address(user_id, chain)
        
        text = (
            f"📥 **Deposit to {chain.upper()}**\n\n"
            f"**Address:**\n"
            f"`{address}`\n\n"
            f"**Network:** {chain.upper()}\n"
            f"**Only send USDT on this network!**\n\n"
            f"After sending the transaction, send me the **Tx Hash** to verify.\n\n"
            f"Example: `0x8a5a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a`"
        )
        
        buttons = [
            [InlineKeyboardButton("✅ I've Sent", callback_data='wallet_balance')],
            [InlineKeyboardButton("🔙 Back", callback_data='wallet_deposit')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
        
        context.user_data['state'] = WAITING_FOR_PAYMENT_TX
        context.user_data['deposit_chain'] = chain
    
    async def _show_profile(self, query, context):
        """نمایش پروفایل کاربر"""
        
        user_id = query.from_user.id
        db_user = self.db.query(User).filter_by(telegram_id=user_id).first()
        
        # اعداد
        life_path = db_user.life_path or 'Not set'
        expression = db_user.expression or 'Not set'
        soul_urge = db_user.soul_urge or 'Not set'
        
        text = (
            f"👤 **Your Profile**\n\n"
            f"🆔 ID: `{db_user.telegram_id}`\n"
            f"📅 Joined: {db_user.created_at.strftime('%Y-%m-%d')}\n\n"
            f"**Your Numbers:**\n"
            f"• Life Path: {life_path}\n"
            f"• Expression: {expression}\n"
            f"• Soul Urge: {soul_urge}\n\n"
            f"**Statistics:**\n"
            f"• Predictions: {db_user.total_predictions}\n"
            f"• Correct: {db_user.correct_predictions}\n"
            f"• Balance: ${db_user.balance:.2f}\n"
            f"• Referrals: {db_user.total_referrals}\n\n"
            f"**Referral Link:**\n"
            f"`https://t.me/{BOT_USERNAME}?start={db_user.referral_code}`"
        )
        
        buttons = [
            [InlineKeyboardButton("📝 Update Info", callback_data='profile_update')],
            [InlineKeyboardButton("🔙 Main Menu", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_referral(self, query, context):
        """نمایش برنامه معرفی"""
        
        user_id = query.from_user.id
        db_user = self.db.query(User).filter_by(telegram_id=user_id).first()
        
        text = (
            "🎁 **Referral Program**\n\n"
            f"**Your Referral Code:**\n"
            f"`{db_user.referral_code}`\n\n"
            f"**Your Link:**\n"
            f"https://t.me/{BOT_USERNAME}?start={db_user.referral_code}\n\n"
            f"**Benefits:**\n"
            f"• Get {REFERRAL_BONUS_PERCENT}% of your referrals' purchases\n"
            f"• No limit on referrals\n"
            f"• Lifetime commission\n\n"
            f"**Your Stats:**\n"
            f"• Total Referrals: {db_user.total_referrals}\n"
            f"• Earnings: ${db_user.referral_earnings:.2f}\n\n"
            f"Share your link and earn!"
        )
        
        buttons = [
            [InlineKeyboardButton("🔙 Main Menu", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_knowledge_base(self, query):
        """نمایش دانشنامه"""
        
        text = (
            "📚 **Knowledge Base**\n\n"
            "**Number Meanings:**\n"
            "1️⃣ **One** - Leadership, independence, originality\n"
            "2️⃣ **Two** - Cooperation, diplomacy, sensitivity\n"
            "3️⃣ **Three** - Creativity, expression, optimism\n"
            "4️⃣ **Four** - Stability, discipline, practicality\n"
            "5️⃣ **Five** - Freedom, adventure, versatility\n"
            "6️⃣ **Six** - Responsibility, love, harmony\n"
            "7️⃣ **Seven** - Wisdom, analysis, spirituality\n"
            "8️⃣ **Eight** - Power, success, abundance\n"
            "9️⃣ **Nine** - Humanitarianism, completion, art\n\n"
            "✨ **Master Numbers:**\n"
            "11 - Illumination, inspiration\n"
            "22 - Master builder, manifestation\n"
            "33 - Master teacher, unconditional love\n\n"
            "**Sources:**\n"
            "• Numbers: Their Occult Power (Westcott)\n"
            "• Kabala of Numbers (Sepharial)\n"
            "• Three Books of Occult Philosophy (Agrippa)"
        )
        
        buttons = [
            [InlineKeyboardButton("🔢 Numerology Guide", callback_data='knowledge_numbers')],
            [InlineKeyboardButton("📖 Book References", callback_data='knowledge_books')],
            [InlineKeyboardButton("🔙 Main Menu", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_help(self, query):
        """نمایش راهنما"""
        
        text = (
            "❓ **Help & Support**\n\n"
            "**How to use:**\n"
            "1️⃣ Choose a prediction type from menu\n"
            "2️⃣ Enter your query (token address, teams, etc.)\n"
            "3️⃣ Pay ${PRICING['basic_prediction']} (free for VIP)\n"
            "4️⃣ Get your prediction!\n\n"
            "**Commands:**\n"
            "/start - Main menu\n"
            "/balance - Check balance\n"
            "/profile - Your profile\n"
            "/referral - Referral program\n"
            "/vip - VIP features\n"
            "/feedback - Send feedback\n\n"
            "**Support:**\n"
            "📧 Email: support@oracle.com\n"
            "💬 Telegram: @OracleSupport\n"
            "🌐 Website: https://oracle.com"
        )
        
        buttons = [
            [InlineKeyboardButton("📧 Contact Support", url='https://t.me/OracleSupport')],
            [InlineKeyboardButton("🔙 Main Menu", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_vip_features(self, query):
        """نمایش ویژگی‌های VIP"""
        
        text = (
            "⭐ **VIP Features**\n\n"
            "**Free Users:**\n"
            "• Basic predictions ($0.32 each)\n"
            "• 5 daily predictions\n"
            "• Basic numerology\n\n"
            "**VIP Monthly (${PRICING['vip_monthly']}):**\n"
            "✅ Unlimited predictions\n"
            "✅ Deep analysis with AI\n"
            "✅ Priority support\n"
            "✅ Exclusive insights\n"
            "✅ Advanced numerology\n"
            "✅ API access\n"
            "✅ No ads\n\n"
            "**Lifetime (${PRICING['lifetime_access']}):**\n"
            "✅ All VIP features\n"
            "✅ Lifetime updates\n"
            "✅ Beta features\n"
            "✅ Personal AI assistant"
        )
        
        buttons = [
            [InlineKeyboardButton("💎 Buy VIP", callback_data='wallet_vip')],
            [InlineKeyboardButton("🔙 Main Menu", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    # ==================== ابزارها ====================
    
    def _generate_referral_code(self, user_id: int) -> str:
        """تولید کد معرفی یکتا"""
        import hashlib
        import base64
        
        hash_obj = hashlib.md5(f"{user_id}{datetime.utcnow()}".encode())
        return base64.b32encode(hash_obj.digest()).decode()[:8].upper()
    
    # ==================== اجرای ربات ====================
    
    def run(self):
        """اجرای ربات"""
        
        # ایجاد اپلیکیشن
        app = Application.builder().token(TELEGRAM_TOKEN).build()
                # راه‌اندازی webhook server در thread جدا
                webhook_thread = threading.Thread(target=self._run_webhook_server, daemon=True)
                webhook_thread.start()

        
        # هندلرها
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("balance", self._balance_command))
        app.add_handler(CommandHandler("profile", self._profile_command))
        app.add_handler(CommandHandler("vip", self._vip_command))
        app.add_handler(CommandHandler("feedback", self._feedback_command))
        
        app.add_handler(CallbackQueryHandler(self.button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # شروع
        logger.info("🚀 Starting Ultimate Oracle Bot...")
        app.run_polling()
    
    async def _balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور نمایش موجودی"""
        user_id = update.effective_user.id
        db_user = self.db.query(User).filter_by(telegram_id=user_id).first()
        
        await update.message.reply_text(
            f"💰 **Your Balance:** ${db_user.balance:.2f}",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور نمایش پروفایل"""
        user_id = update.effective_user.id
        db_user = self.db.query(User).filter_by(telegram_id=user_id).first()
        
        text = (
            f"👤 **Profile**\n\n"
            f"ID: `{db_user.telegram_id}`\n"
            f"Balance: ${db_user.balance:.2f}\n"
            f"Predictions: {db_user.total_predictions}\n"
            f"Correct: {db_user.correct_predictions}"
        )
        
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    
    async def _vip_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور نمایش VIP"""
        await self._show_vip_features(update.message)
    
    async def _feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور ارسال بازخورد"""
        await update.message.reply_text(
            "📝 Please send your feedback:"
        )
        context.user_data['state'] = WAITING_FOR_FEEDBACK
# ==================== Webhook Server ====================
class WebhookServer:
    def __init__(self, bot_app):
        self.bot_app = bot_app
        self.server = None
    
    async def handle_webhook(self, request):
        try:
            content_length = int(request.headers.get('Content-Length', 0))
            post_data = await request.read()
            update = Update.de_json(json.loads(post_data), self.bot_app.bot)
            await self.bot_app.process_update(update)
            return web.Response(text='OK')
        except Exception as e:
            print(f"Webhook error: {e}")
            return web.Response(text='Error', status=500)
    
    def run(self):
        from aiohttp import web
        app = web.Application()
        app.router.add_post('/webhook', self.handle_webhook)

    def _run_webhook_server(self):
        """راه‌اندازی سرور webhook در پورت 8080"""
        import threading
        import asyncio
        import json
        from aiohttp import web
        from telegram import Update
        
        async def webhook_handler(request):
            try:
                data = await request.json()
                if hasattr(self, 'app') and self.app:
                    update = Update.de_json(data, self.app.bot)
                    await self.app.process_update(update)
                return web.Response(text='OK')
            except Exception as e:
                print(f"Webhook error: {e}")
                return web.Response(text='Error', status=500)
        
        async def run_server():
            app = web.Application()
            app.router.add_post('/webhook', webhook_handler)
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 8080)
            await site.start()
            print("✅ Webhook server running on port 8080")
            
            # نگه داشتن سرور فعال
            while True:
                await asyncio.sleep(3600)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())
        loop.run_forever()

        
        runner = web.AppRunner(app)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        loop.run_until_complete(site.start())
        print("✅ Webhook server running on port 8080")
        loop.run_forever()
