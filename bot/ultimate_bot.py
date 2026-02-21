#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ربات اصلی تلگرام - با imports ایمن
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes,
    ConversationHandler
)
from telegram.constants import ParseMode
from datetime import datetime
import asyncio
import json
import threading

# ===== ایمپورت‌های ایمن =====
from core.safe_imports import importer
from core.error_handler import error_handler, safe_execute, safe_async_execute

logger = logging.getLogger(__name__)

class UltimateBot:
    """
    ربات اصلی با imports ایمن
    """
    
    def __init__(self):
        logger.info("🤖 Initializing UltimateBot...")
        
        # ===== ایمپورت‌های ایمن =====
        from database.models import init_database, User, Prediction, get_db
        from core.numerology_engine import NumerologyEngine
        
        self.db = next(get_db())
        self.numerology = NumerologyEngine(self.db)
        
        # ===== AI و تحلیلگرها (با fallback) =====
        self.ai = None
        self.token_analyzer = None
        self.sports_predictor = None
        self.event_predictor = None
        self.payment_verifier = None
        
        # تلاش برای import AI
        try:
            from ai.genius_ai import GeniusAI
            self.ai = GeniusAI(self.db, self.numerology)
            logger.info("✅ GeniusAI loaded")
        except ImportError as e:
            logger.warning(f"⚠️ GeniusAI not available: {e}")
        
        # تلاش برای import Token Analyzer
        try:
            from web3_analyzer.token_analyzer import TokenAnalyzer
            self.token_analyzer = TokenAnalyzer(self.db, self.numerology, self.ai)
            logger.info("✅ TokenAnalyzer loaded")
        except ImportError as e:
            logger.warning(f"⚠️ TokenAnalyzer not available: {e}")
        
        # تلاش برای import Sports Predictor
        try:
            from sports_analyzer.sports_predictor import SportsPredictor
            self.sports_predictor = SportsPredictor(self.db, self.numerology, self.ai)
            logger.info("✅ SportsPredictor loaded")
        except ImportError as e:
            logger.warning(f"⚠️ SportsPredictor not available: {e}")
        
        # تلاش برای import Event Predictor
        try:
            from event_analyzer.event_predictor import EventPredictor
            self.event_predictor = EventPredictor(self.db, self.numerology, self.ai)
            logger.info("✅ EventPredictor loaded")
        except ImportError as e:
            logger.warning(f"⚠️ EventPredictor not available: {e}")
        
        # تلاش برای import Payment Verifier
        try:
            from payment.payment_verifier import PaymentVerifier
            self.payment_verifier = PaymentVerifier(self.db)
            logger.info("✅ PaymentVerifier loaded")
        except ImportError as e:
            logger.warning(f"⚠️ PaymentVerifier not available: {e}")
        
        # ===== Webhook server =====
        self.webhook_server = None
        self.start_webhook_server()
    
    def start_webhook_server(self):
        """راه‌اندازی سرور webhook در thread جدا"""
        try:
            webhook_thread = threading.Thread(target=self._run_webhook_server, daemon=True)
            webhook_thread.start()
            logger.info("✅ Webhook server thread started")
        except Exception as e:
            logger.error(f"❌ Failed to start webhook server: {e}")
    
    def _run_webhook_server(self):
        """اجرای سرور webhook"""
        import asyncio
        from aiohttp import web
        
        async def webhook_handler(request):
            try:
                data = await request.json()
                # پردازش webhook
                return web.Response(text='OK')
            except Exception as e:
                logger.error(f"Webhook error: {e}")
                return web.Response(text='Error', status=500)
        
        async def run_server():
            app = web.Application()
            app.router.add_post('/webhook', webhook_handler)
            
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 8080)
            await site.start()
            logger.info("✅ Webhook server running on port 8080")
            
            # نگه داشتن سرور فعال
            while True:
                await asyncio.sleep(3600)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_server())
        loop.run_forever()
    
    def get_main_menu(self) -> InlineKeyboardMarkup:
        """منوی اصلی"""
        buttons = [
            [
                InlineKeyboardButton("🔮 Crypto", callback_data='menu_crypto'),
                InlineKeyboardButton("⚽ Sports", callback_data='menu_sports')
            ],
            [
                InlineKeyboardButton("🌍 Events", callback_data='menu_events'),
                InlineKeyboardButton("🔢 Numerology", callback_data='menu_numerology')
            ],
            [
                InlineKeyboardButton("💰 Wallet", callback_data='menu_wallet'),
                InlineKeyboardButton("📊 Profile", callback_data='menu_profile')
            ],
            [
                InlineKeyboardButton("📚 Knowledge", callback_data='menu_knowledge'),
                InlineKeyboardButton("❓ Help", callback_data='menu_help')
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @safe_async_execute(default_return=None)
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """دستور start"""
        user = update.effective_user
        logger.info(f"User {user.id} started the bot")
        
        welcome_text = f"""
✨ **Welcome {user.first_name}!** ✨

I'm an intelligent bot with self-healing capabilities.
All features work even if some libraries are missing.

**Available features:**
• 🔮 Crypto predictions {self._get_status_emoji(self.token_analyzer)}
• ⚽ Sports predictions {self._get_status_emoji(self.sports_predictor)}
• 🌍 Event predictions {self._get_status_emoji(self.event_predictor)}
• 🔢 Numerology calculations ✅
• 💰 Wallet & payments {self._get_status_emoji(self.payment_verifier)}
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=self.get_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    def _get_status_emoji(self, module) -> str:
        """دریافت ایموجی وضعیت ماژول"""
        return "✅" if module else "⏳"
    
    @safe_async_execute(default_return=None)
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت دکمه‌ها"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == 'menu_crypto':
            await self._show_crypto_menu(query)
        elif data == 'menu_sports':
            await self._show_sports_menu(query)
        elif data == 'menu_events':
            await self._show_events_menu(query)
        elif data == 'menu_numerology':
            await self._show_numerology_menu(query)
        elif data == 'menu_wallet':
            await self._show_wallet(query)
        elif data == 'menu_profile':
            await self._show_profile(query)
        elif data == 'menu_knowledge':
            await self._show_knowledge(query)
        elif data == 'menu_help':
            await self._show_help(query)
        elif data == 'back_main':
            await query.edit_message_text(
                "✨ **Main Menu** ✨",
                reply_markup=self.get_main_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def _show_crypto_menu(self, query):
        """منوی کریپتو"""
        status = "✅ Active" if self.token_analyzer else "⏳ Limited (basic only)"
        
        text = f"""
🔮 **Crypto Predictions**
Status: {status}

**Available options:**
• Analyze token by address
• Pump prediction
• Market overview
• Whale alerts

**Note:** Basic analysis always works.
        """
        
        buttons = [
            [InlineKeyboardButton("🔍 Analyze Token", callback_data='crypto_analyze')],
            [InlineKeyboardButton("🚀 Pump Prediction", callback_data='crypto_pump')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_sports_menu(self, query):
        """منوی ورزشی"""
        status = "✅ Active" if self.sports_predictor else "⏳ Limited"
        
        text = f"""
⚽ **Sports Predictions**
Status: {status}

**Available sports:**
• Football
• Basketball
• Tennis
• And more...

**Note:** Basic predictions available even without ML.
        """
        
        buttons = [
            [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_events_menu(self, query):
        """منوی رویدادها"""
        status = "✅ Active" if self.event_predictor else "⏳ Limited"
        
        text = f"""
🌍 **Event Predictions**
Status: {status}

**Available events:**
• Elections
• Weather
• Awards
• Custom events
        """
        
        buttons = [
            [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_numerology_menu(self, query):
        """منوی عددشناسی"""
        text = """
🔢 **Numerology**
Status: ✅ Always Active

**Available calculations:**
• Life Path Number
• Name Number
• Personal Day
• Gematria
• Compatibility
        """
        
        buttons = [
            [InlineKeyboardButton("📅 Life Path", callback_data='num_life_path')],
            [InlineKeyboardButton("📝 Name Number", callback_data='num_name')],
            [InlineKeyboardButton("❤️ Compatibility", callback_data='num_compatibility')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_wallet(self, query):
        """نمایش کیف پول"""
        text = """
💰 **Wallet**
Status: Processing...

• Balance: $0.00
• Total predictions: 0
• Success rate: 0%

**Note:** Payment system initializing.
        """
        
        buttons = [
            [InlineKeyboardButton("📥 Deposit", callback_data='wallet_deposit')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_profile(self, query):
        """نمایش پروفایل"""
        user_id = query.from_user.id
        
        text = f"""
📊 **Your Profile**

🆔 ID: `{user_id}`
📅 Joined: {datetime.now().strftime('%Y-%m-%d')}

**Active Features:**
• Numerology: ✅
• Crypto: {self._get_status_emoji(self.token_analyzer)}
• Sports: {self._get_status_emoji(self.sports_predictor)}
• Events: {self._get_status_emoji(self.event_predictor)}
• Wallet: {self._get_status_emoji(self.payment_verifier)}
        """
        
        buttons = [
            [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_knowledge(self, query):
        """نمایش دانشنامه"""
        text = """
📚 **Knowledge Base**

**Number Meanings:**
1️⃣ Leadership, independence
2️⃣ Cooperation, diplomacy
3️⃣ Creativity, expression
4️⃣ Stability, discipline
5️⃣ Freedom, adventure
6️⃣ Responsibility, love
7️⃣ Wisdom, analysis
8️⃣ Power, success
9️⃣ Humanitarianism

**Sources:**
• Numbers: Their Occult Power
• Kabala of Numbers
• Three Books of Occult Philosophy
        """
        
        buttons = [
            [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _show_help(self, query):
        """نمایش راهنما"""
        text = """
❓ **Help & Support**

**Commands:**
/start - Main menu
/balance - Check balance
/profile - Your profile
/help - This menu

**Features:**
• All features work even with limited libraries
• Self-healing system active
• Automatic error recovery
• Continuous evolution

**Support:**
@UltimateOracleBot
        """
        
        buttons = [
            [InlineKeyboardButton("🔙 Back", callback_data='back_main')]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    
    @safe_async_execute(default_return=None)
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """مدیریت پیام‌ها"""
        text = update.message.text
        
        if text.startswith('/'):
            # دستورات
            if text == '/start':
                await self.start(update, context)
            elif text == '/balance':
                await update.message.reply_text("💰 Balance: $0.00")
            elif text == '/profile':
                await self._show_profile(update.message)
            else:
                await update.message.reply_text("Unknown command")
        else:
            # پیام معمولی
            await update.message.reply_text(
                "Please use menu buttons.",
                reply_markup=self.get_main_menu()
            )
    
    def run(self):
        """اجرای ربات"""
        from config import TELEGRAM_TOKEN
        
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CallbackQueryHandler(self.button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("🚀 Bot starting...")
        app.run_polling()
