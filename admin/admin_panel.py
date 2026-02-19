# admin/admin_panel.py
"""
پنل مدیریت پیشرفته برای کنترل کامل ربات
قابلیت‌ها:
- آمار لحظه‌ای
- مدیریت کاربران
- تنظیم قیمت‌ها
- مشاهده تراکنش‌ها
- ارسال همگانی
- پشتیبان‌گیری
- تنظیمات سیستم
- لاگ‌ها
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import json
import os
import shutil
from typing import Dict, Any, List
# import pandas as pd
from pathlib import Path

from database.models import User, Prediction, Transaction, get_db
from config import *

logger = logging.getLogger(__name__)

class AdminPanel:
    """
    پنل مدیریت با دسترسی‌های سطح بالا
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
        
        # لیست ادمین‌ها (از دیتابیس یا config)
        self.admin_ids = ADMIN_USER_IDS
        
        # آمار کش
        self.stats_cache = {}
        self.cache_time = datetime.now()
    
    def is_admin(self, user_id: int) -> bool:
        """بررسی ادمین بودن کاربر"""
        return user_id in self.admin_ids
    
    # ==================== منوی اصلی مدیریت ====================
    
    def get_admin_menu(self) -> InlineKeyboardMarkup:
        """منوی اصلی پنل مدیریت"""
        
        buttons = [
            [
                InlineKeyboardButton("📊 Dashboard", callback_data='admin_dashboard'),
                InlineKeyboardButton("👥 Users", callback_data='admin_users')
            ],
            [
                InlineKeyboardButton("💰 Transactions", callback_data='admin_transactions'),
                InlineKeyboardButton("🔮 Predictions", callback_data='admin_predictions')
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data='admin_settings'),
                InlineKeyboardButton("📢 Broadcast", callback_data='admin_broadcast')
            ],
            [
                InlineKeyboardButton("💾 Backup", callback_data='admin_backup'),
                InlineKeyboardButton("📋 Logs", callback_data='admin_logs')
            ],
            [
                InlineKeyboardButton("📊 Reports", callback_data='admin_reports'),
                InlineKeyboardButton("🔧 Maintenance", callback_data='admin_maintenance')
            ],
            [
                InlineKeyboardButton("🔙 Back to Bot", callback_data='back_main')
            ]
        ]
        
        return InlineKeyboardMarkup(buttons)
    
    # ==================== داشبورد ====================
    
    async def show_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش داشبورد مدیریت"""
        
        stats = self.get_dashboard_stats()
        
        text = (
            "📊 **Admin Dashboard**\n\n"
            f"**Users:**\n"
            f"• Total: {stats['users']['total']}\n"
            f"• Active (24h): {stats['users']['active_24h']}\n"
            f"• New (7d): {stats['users']['new_7d']}\n"
            f"• VIP: {stats['users']['vip']}\n\n"
            
            f"**Predictions:**\n"
            f"• Total: {stats['predictions']['total']}\n"
            f"• Today: {stats['predictions']['today']}\n"
            f"• Accuracy: {stats['predictions']['accuracy']:.1f}%\n"
            f"• Revenue: ${stats['predictions']['revenue']:.2f}\n\n"
            
            f"**Transactions:**\n"
            f"• Total: {stats['transactions']['total']}\n"
            f"• Volume: ${stats['transactions']['volume']:.2f}\n"
            f"• Pending: {stats['transactions']['pending']}\n\n"
            
            f"**System:**\n"
            f"• Uptime: {stats['system']['uptime']}\n"
            f"• DB Size: {stats['system']['db_size']}\n"
            f"• Cache: {stats['system']['cache_size']}\n"
            f"• Last Backup: {stats['system']['last_backup']}\n\n"
            
            f"🕐 Last Update: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        buttons = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data='admin_dashboard'),
                InlineKeyboardButton("📊 Detailed", callback_data='admin_stats_detailed')
            ],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
    
    def get_dashboard_stats(self) -> Dict:
        """گرفتن آمار داشبورد"""
        
        if not self.db:
            return {}
        
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        # آمار کاربران
        total_users = self.db.query(User).count()
        active_24h = self.db.query(User).filter(User.last_active >= yesterday).count()
        new_7d = self.db.query(User).filter(User.created_at >= week_ago).count()
        vip_users = self.db.query(User).filter(User.subscription_tier != 'free').count()
        
        # آمار پیش‌بینی‌ها
        total_preds = self.db.query(Prediction).count()
        today_preds = self.db.query(Prediction).filter(
            Prediction.predicted_at >= now.replace(hour=0, minute=0, second=0)
        ).count()
        
        # محاسبه دقت
        correct_preds = self.db.query(Prediction).filter(Prediction.was_correct == True).count()
        accuracy = (correct_preds / total_preds * 100) if total_preds > 0 else 0
        
        # درآمد
        total_revenue = self.db.query(Transaction).filter(
            Transaction.tx_type == 'payment',
            Transaction.status == 'completed'
        ).with_entities(func.sum(Transaction.amount)).scalar() or 0
        
        # تراکنش‌ها
        total_txs = self.db.query(Transaction).count()
        total_volume = self.db.query(Transaction).with_entities(
            func.sum(Transaction.amount)
        ).filter(Transaction.status == 'completed').scalar() or 0
        pending_txs = self.db.query(Transaction).filter(Transaction.status == 'pending').count()
        
        # سیستم
        db_file = Path('data/oracle.db')
        db_size = f"{db_file.stat().st_size / 1024 / 1024:.1f} MB" if db_file.exists() else "0 MB"
        
        # آخرین بک‌آپ
        backup_dir = Path('backups')
        last_backup = "Never"
        if backup_dir.exists():
            backups = list(backup_dir.glob('*.sqlite'))
            if backups:
                last_backup = max(backups, key=lambda p: p.stat().st_mtime).name
        
        return {
            'users': {
                'total': total_users,
                'active_24h': active_24h,
                'new_7d': new_7d,
                'vip': vip_users
            },
            'predictions': {
                'total': total_preds,
                'today': today_preds,
                'accuracy': accuracy,
                'revenue': total_revenue
            },
            'transactions': {
                'total': total_txs,
                'volume': total_volume,
                'pending': pending_txs
            },
            'system': {
                'uptime': '2 days',  # TODO
                'db_size': db_size,
                'cache_size': '0 MB',
                'last_backup': last_backup
            }
        }
    
    # ==================== مدیریت کاربران ====================
    
    async def show_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
        """نمایش لیست کاربران"""
        
        if not self.db:
            return
        
        per_page = 10
        users = self.db.query(User).order_by(User.created_at.desc()).offset(page * per_page).limit(per_page).all()
        total = self.db.query(User).count()
        pages = (total + per_page - 1) // per_page
        
        text = f"👥 **Users (Page {page+1}/{pages})**\n\n"
        
        for user in users:
            text += (
                f"🆔 `{user.telegram_id}` | "
                f"@{user.username or 'no username'} | "
                f"${user.balance:.2f} | "
                f"{user.subscription_tier.upper()}\n"
            )
        
        text += f"\nTotal: {total} users"
        
        buttons = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f'admin_users_{page-1}'))
        if page < pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f'admin_users_{page+1}'))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        buttons.append([
            InlineKeyboardButton("🔍 Search", callback_data='admin_user_search'),
            InlineKeyboardButton("📊 Export", callback_data='admin_users_export')
        ])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data='admin_menu')])
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
    
    async def show_user_detail(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """نمایش جزئیات کاربر"""
        
        if not self.db:
            return
        
        user = self.db.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            await update.message.reply_text("User not found")
            return
        
        # آمار کاربر
        predictions = self.db.query(Prediction).filter_by(user_id=user.id).count()
        correct = self.db.query(Prediction).filter_by(user_id=user.id, was_correct=True).count()
        accuracy = (correct / predictions * 100) if predictions > 0 else 0
        
        transactions = self.db.query(Transaction).filter_by(user_id=user.id).count()
        total_spent = self.db.query(Transaction).filter_by(
            user_id=user.id, tx_type='payment', status='completed'
        ).with_entities(func.sum(Transaction.amount)).scalar() or 0
        
        text = (
            f"👤 **User Details**\n\n"
            f"🆔 ID: `{user.telegram_id}`\n"
            f"👤 Username: @{user.username or 'N/A'}\n"
            f"📝 Name: {user.first_name or ''} {user.last_name or ''}\n"
            f"📅 Joined: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"⏱ Last Active: {user.last_active.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            f"💰 Balance: ${user.balance:.2f}\n"
            f"💎 Tier: {user.subscription_tier.upper()}\n"
            f"📊 Predictions: {predictions}\n"
            f"✅ Correct: {correct} ({accuracy:.1f}%)\n"
            f"💸 Total Spent: ${total_spent:.2f}\n"
            f"🎁 Referrals: {user.total_referrals}\n\n"
            
            f"🔢 Numbers:\n"
            f"• Life Path: {user.life_path or 'N/A'}\n"
            f"• Expression: {user.expression or 'N/A'}\n"
            f"• Soul Urge: {user.soul_urge or 'N/A'}\n"
        )
        
        buttons = [
            [
                InlineKeyboardButton("➕ Add Balance", callback_data=f'admin_user_add_{user_id}'),
                InlineKeyboardButton("➖ Deduct", callback_data=f'admin_user_deduct_{user_id}')
            ],
            [
                InlineKeyboardButton("📝 Edit", callback_data=f'admin_user_edit_{user_id}'),
                InlineKeyboardButton("🚫 Ban", callback_data=f'admin_user_ban_{user_id}')
            ],
            [
                InlineKeyboardButton("📊 Predictions", callback_data=f'admin_user_preds_{user_id}'),
                InlineKeyboardButton("💰 Transactions", callback_data=f'admin_user_txs_{user_id}')
            ],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_users')]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
    
    # ==================== مدیریت تراکنش‌ها ====================
    
    async def show_transactions(self, update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
        """نمایش تراکنش‌ها"""
        
        if not self.db:
            return
        
        per_page = 10
        txs = self.db.query(Transaction).order_by(Transaction.created_at.desc()).offset(page * per_page).limit(per_page).all()
        total = self.db.query(Transaction).count()
        pages = (total + per_page - 1) // per_page
        
        text = f"💰 **Transactions (Page {page+1}/{pages})**\n\n"
        
        for tx in txs:
            status_emoji = {
                'completed': '✅',
                'pending': '⏳',
                'failed': '❌',
                'expired': '⌛'
            }.get(tx.status, '❓')
            
            text += (
                f"{status_emoji} `{tx.tx_hash[:10]}...` | "
                f"${tx.amount:.2f} | "
                f"{tx.tx_type} | "
                f"{tx.created_at.strftime('%H:%M')}\n"
            )
        
        text += f"\nTotal: {total} transactions"
        text += f"\nVolume: ${self.db.query(Transaction).with_entities(func.sum(Transaction.amount)).scalar() or 0:.2f}"
        
        buttons = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f'admin_transactions_{page-1}'))
        if page < pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f'admin_transactions_{page+1}'))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        buttons.append([
            InlineKeyboardButton("🔍 Search", callback_data='admin_tx_search'),
            InlineKeyboardButton("📊 Export", callback_data='admin_txs_export')
        ])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data='admin_menu')])
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
    
    # ==================== تنظیمات ====================
    
    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش تنظیمات"""
        
        text = (
            "⚙️ **System Settings**\n\n"
            f"**Pricing:**\n"
            f"• Basic: ${PRICING['basic_prediction']}\n"
            f"• Deep: ${PRICING['deep_analysis']}\n"
            f"• VIP Monthly: ${PRICING['vip_monthly']}\n"
            f"• Lifetime: ${PRICING['lifetime_access']}\n\n"
            
            f"**Payment:**\n"
            f"• Confirmations: {PAYMENT_CONFIRMATIONS_NEEDED}\n"
            f"• Expiry: {PAYMENT_EXPIRY_HOURS}h\n"
            f"• Welcome Bonus: ${WELCOME_BONUS}\n\n"
            
            f"**Features:**\n"
            f"• AI Learning: {AUTO_LEARN}\n"
            f"• Marketing: {ENABLE_SELF_MARKETING}\n"
            f"• Referral Bonus: {REFERRAL_BONUS_PERCENT}%\n\n"
            
            f"**System:**\n"
            f"• Log Level: {LOG_LEVEL}\n"
            f"• Backup: {BACKUP_INTERVAL_HOURS}h\n"
            f"• Retention: {KEEP_BACKUPS_DAYS} days"
        )
        
        buttons = [
            [
                InlineKeyboardButton("💰 Prices", callback_data='admin_settings_prices'),
                InlineKeyboardButton("💳 Wallet", callback_data='admin_settings_wallet')
            ],
            [
                InlineKeyboardButton("🤖 AI", callback_data='admin_settings_ai'),
                InlineKeyboardButton("📊 Features", callback_data='admin_settings_features')
            ],
            [
                InlineKeyboardButton("🔧 Advanced", callback_data='admin_settings_advanced'),
                InlineKeyboardButton("💾 Save", callback_data='admin_settings_save')
            ],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
    
    # ==================== ارسال همگانی ====================
    
    async def show_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش صفحه ارسال همگانی"""
        
        if not self.db:
            return
        
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(
            User.last_active >= datetime.now() - timedelta(days=7)
        ).count()
        
        text = (
            "📢 **Broadcast Message**\n\n"
            f"Total Users: {total_users}\n"
            f"Active (7d): {active_users}\n\n"
            "Send me the message you want to broadcast:\n"
            "(You can use Markdown)"
        )
        
        buttons = [
            [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
        
        context.user_data['admin_state'] = 'broadcast'
    
    async def send_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
        """ارسال پیام به همه کاربران"""
        
        if not self.db:
            return
        
        users = self.db.query(User).filter(User.is_active == True).all()
        sent = 0
        failed = 0
        
        await update.message.reply_text(f"📤 Sending to {len(users)} users...")
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message,
                    parse_mode='Markdown'
                )
                sent += 1
                await asyncio.sleep(0.05)  # جلوگیری از rate limit
            except Exception as e:
                failed += 1
                logger.error(f"Failed to send to {user.telegram_id}: {e}")
        
        await update.message.reply_text(
            f"✅ Broadcast completed!\n"
            f"Sent: {sent}\n"
            f"Failed: {failed}"
        )
    
    # ==================== پشتیبان‌گیری ====================
    
    async def show_backup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش صفحه پشتیبان‌گیری"""
        
        backup_dir = Path('backups')
        backup_dir.mkdir(exist_ok=True)
        
        backups = sorted(backup_dir.glob('*.sqlite'), key=lambda p: p.stat().st_mtime, reverse=True)
        
        text = "💾 **Backup Manager**\n\n"
        
        if backups:
            text += "**Recent Backups:**\n"
            for backup in backups[:5]:
                size = backup.stat().st_size / 1024 / 1024
                modified = datetime.fromtimestamp(backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                text += f"• {backup.name} ({size:.1f} MB) - {modified}\n"
        else:
            text += "No backups found.\n"
        
        text += f"\nBackup Location: {backup_dir.absolute()}"
        
        buttons = [
            [
                InlineKeyboardButton("🆕 Create Backup", callback_data='admin_backup_create'),
                InlineKeyboardButton("🔄 Restore", callback_data='admin_backup_restore')
            ],
            [
                InlineKeyboardButton("📥 Download", callback_data='admin_backup_download'),
                InlineKeyboardButton("🗑️ Clean Old", callback_data='admin_backup_clean')
            ],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
    
    async def create_backup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ایجاد پشتیبان جدید"""
        
        await update.message.reply_text("💾 Creating backup...")
        
        try:
            backup_dir = Path('backups')
            backup_dir.mkdir(exist_ok=True)
            
            # نام فایل با تاریخ
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
            backup_path = backup_dir / filename
            
            # کپی دیتابیس
            db_path = Path('data/oracle.db')
            if db_path.exists():
                shutil.copy2(db_path, backup_path)
                
                # فشرده‌سازی
                import gzip
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # حذف فایل غیر فشرده
                backup_path.unlink()
                
                size = (backup_path.stat().st_size if backup_path.exists() else 0) / 1024
                
                await update.message.reply_text(
                    f"✅ Backup created successfully!\n"
                    f"File: {filename}.gz\n"
                    f"Size: {size:.1f} KB"
                )
            else:
                await update.message.reply_text("❌ Database file not found!")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Backup failed: {str(e)}")
    
    # ==================== لاگ‌ها ====================
    
    async def show_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE, lines: int = 50):
        """نمایش لاگ‌های سیستم"""
        
        log_file = Path('logs/oracle.log')
        if not log_file.exists():
            await update.message.reply_text("No log file found.")
            return
        
        try:
            # خواندن آخرین خطوط
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:]
            
            text = f"📋 **Last {lines} Log Lines**\n\n"
            text += "```\n"
            text += ''.join(last_lines)
            text += "```"
            
            if len(text) > 4000:
                text = text[:4000] + "...\n```"
            
            buttons = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data='admin_logs'),
                    InlineKeyboardButton("📥 Download", callback_data='admin_logs_download')
                ],
                [
                    InlineKeyboardButton("❌ Errors Only", callback_data='admin_logs_errors'),
                    InlineKeyboardButton("🗑️ Clear", callback_data='admin_logs_clear')
                ],
                [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
            ]
            
            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading logs: {str(e)}")
    
    # ==================== گزارش‌ها ====================
    
    async def show_reports(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش صفحه گزارش‌ها"""
        
        text = (
            "📊 **Reports**\n\n"
            "Generate various reports:\n\n"
            "• Daily/Weekly/Monthly reports\n"
            "• Revenue reports\n"
            "• User activity reports\n"
            "• Prediction accuracy reports\n"
            "• Export to CSV/Excel"
        )
        
        buttons = [
            [
                InlineKeyboardButton("📅 Daily", callback_data='admin_report_daily'),
                InlineKeyboardButton("📆 Weekly", callback_data='admin_report_weekly')
            ],
            [
                InlineKeyboardButton("📊 Monthly", callback_data='admin_report_monthly'),
                InlineKeyboardButton("💰 Revenue", callback_data='admin_report_revenue')
            ],
            [
                InlineKeyboardButton("👥 Users", callback_data='admin_report_users'),
                InlineKeyboardButton("🔮 Predictions", callback_data='admin_report_predictions')
            ],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
    
    async def generate_revenue_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE, period: str = 'daily'):
        """تولید گزارش درآمد"""
        
        if not self.db:
            return
        
        now = datetime.now()
        
        if period == 'daily':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            group_by = 'hour'
        elif period == 'weekly':
            start = now - timedelta(days=7)
            group_by = 'day'
        else:  # monthly
            start = now - timedelta(days=30)
            group_by = 'day'
        
        # دریافت تراکنش‌ها
        txs = self.db.query(Transaction).filter(
            Transaction.created_at >= start,
            Transaction.status == 'completed',
            Transaction.tx_type == 'payment'
        ).all()
        
        if not txs:
            await update.message.reply_text(f"No transactions in this {period} period.")
            return
        
        total = sum(tx.amount for tx in txs)
        count = len(txs)
        
        # گروه‌بندی
        from collections import defaultdict
        grouped = defaultdict(float)
        for tx in txs:
            if group_by == 'hour':
                key = tx.created_at.strftime('%H:00')
            else:
                key = tx.created_at.strftime('%Y-%m-%d')
            grouped[key] += tx.amount
        
        text = f"💰 **Revenue Report ({period.capitalize()})**\n\n"
        text += f"Period: {start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}\n"
        text += f"Total: ${total:.2f}\n"
        text += f"Transactions: {count}\n"
        text += f"Average: ${total/count:.2f}\n\n"
        
        text += "**Breakdown:**\n"
        for key, amount in sorted(grouped.items()):
            text += f"• {key}: ${amount:.2f}\n"
        
        # TODO: ارسال به‌عنوان فایل
        
        await update.message.reply_text(text)
    
    # ==================== نگهداری ====================
    
    async def show_maintenance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """نمایش صفحه نگهداری"""
        
        text = (
            "🔧 **Maintenance Tools**\n\n"
            "• Clear cache\n"
            "• Optimize database\n"
            "• Clean old data\n"
            "• Reset user data\n"
            "• System health check"
        )
        
        buttons = [
            [
                InlineKeyboardButton("🧹 Clear Cache", callback_data='admin_maint_cache'),
                InlineKeyboardButton("⚡ Optimize DB", callback_data='admin_maint_optimize')
            ],
            [
                InlineKeyboardButton("🗑️ Clean Old", callback_data='admin_maint_clean'),
                InlineKeyboardButton("🏥 Health Check", callback_data='admin_maint_health')
            ],
            [
                InlineKeyboardButton("🔄 Restart Bot", callback_data='admin_maint_restart'),
                InlineKeyboardButton("⚠️ Reset System", callback_data='admin_maint_reset')
            ],
            [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode='Markdown'
        )
    
    async def health_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بررسی سلامت سیستم"""
        
        issues = []
        
        # بررسی دیتابیس
        try:
            self.db.execute("SELECT 1").scalar()
        except:
            issues.append("❌ Database connection failed")
        
        # بررسی دیسک
        import shutil
        disk = shutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        if free_gb < 1:
            issues.append(f"⚠️ Low disk space: {free_gb:.1f} GB free")
        
        # بررسی حافظه
        import psutil
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            issues.append(f"⚠️ High memory usage: {memory.percent}%")
        
        # بررسی API‌ها
        # TODO
        
        text = "🏥 **System Health Check**\n\n"
        
        if issues:
            text += "**Issues Found:**\n" + "\n".join(issues)
        else:
            text += "✅ All systems operational!"
        
        text += f"\n\nDisk: {free_gb:.1f} GB free\n"
        text += f"Memory: {memory.percent}% used\n"
        text += f"CPU: {psutil.cpu_percent()}%"
        
        await update.message.reply_text(text)
