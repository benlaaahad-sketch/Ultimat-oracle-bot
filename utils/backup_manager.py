# utils/backup_manager.py
"""
مدیریت خودکار پشتیبان‌گیری از کل سیستم
- پشتیبان‌گیری از دیتابیس
- پشتیبان‌گیری از حافظه AI
- پشتیبان‌گیری از فایل‌های تنظیمات
- فشرده‌سازی خودکار
- پاک کردن پشتیبان‌های قدیمی
- آپلود به فضای ابری (اختیاری)
"""

import os
import shutil
import zipfile
import gzip
import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
import threading
import time
import schedule
from typing import Dict, List, Optional
import hashlib

logger = logging.getLogger(__name__)

class BackupManager:
    """
    مدیریت خودکار پشتیبان‌گیری با قابلیت زمان‌بندی
    """
    
    def __init__(self, backup_dir: str = "backups", 
                 db_path: str = "data/oracle.db",
                 memory_dir: str = "memory",
                 config_files: List[str] = None,
                 auto_backup_interval: int = 24):  # ساعت
        
        self.backup_dir = Path(backup_dir)
        self.db_path = Path(db_path)
        self.memory_dir = Path(memory_dir)
        self.config_files = config_files or ["config.py", ".env"]
        self.auto_backup_interval = auto_backup_interval
        
        # ایجاد پوشه backup اگر وجود ندارد
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # آمار
        self.stats = {
            'total_backups': 0,
            'last_backup': None,
            'total_size_mb': 0,
            'backup_history': []
        }
        
        # لاگ
        logger.info(f"📦 BackupManager initialized: {self.backup_dir}")
        
        # شروع thread پشتیبان‌گیری خودکار
        self.start_auto_backup()
    
    def create_backup(self, backup_name: str = None) -> Dict:
        """
        ایجاد پشتیبان کامل از سیستم
        
        Args:
            backup_name: نام دلخواه برای پشتیبان (اختیاری)
        
        Returns:
            اطلاعات پشتیبان ایجاد شده
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not backup_name:
            backup_name = f"backup_{timestamp}"
        
        backup_file = self.backup_dir / f"{backup_name}.zip"
        
        logger.info(f"🔄 Creating backup: {backup_name}")
        
        try:
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                
                # 1. پشتیبان‌گیری از دیتابیس
                if self.db_path.exists():
                    # کپی موقت دیتابیس (برای جلوگیری از قفل شدن)
                    temp_db = self.backup_dir / "temp_db.sqlite"
                    shutil.copy2(self.db_path, temp_db)
                    zipf.write(temp_db, "database/oracle.db")
                    temp_db.unlink()  # حذف فایل موقت
                    logger.info(f"  ✅ Database backed up: {self.db_path}")
                
                # 2. پشتیبان‌گیری از حافظه AI
                if self.memory_dir.exists():
                    for mem_file in self.memory_dir.glob("*"):
                        if mem_file.is_file():
                            zipf.write(mem_file, f"memory/{mem_file.name}")
                    logger.info(f"  ✅ AI Memory backed up: {self.memory_dir}")
                
                # 3. پشتیبان‌گیری از فایل‌های تنظیمات
                for config_file in self.config_files:
                    config_path = Path(config_file)
                    if config_path.exists():
                        zipf.write(config_path, f"config/{config_path.name}")
                        logger.info(f"  ✅ Config backed up: {config_file}")
                
                # 4. پشتیبان‌گیری از لاگ‌ها (فقط آخرین)
                log_dir = Path("logs")
                if log_dir.exists():
                    for log_file in sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]:
                        zipf.write(log_file, f"logs/{log_file.name}")
                
                # 5. ایجاد فایل اطلاعات
                info = {
                    'backup_name': backup_name,
                    'timestamp': timestamp,
                    'datetime': datetime.now().isoformat(),
                    'files': [str(f) for f in zipf.namelist()],
                    'size_bytes': 0,
                    'checksum': None
                }
                
                # نوشتن فایل info
                zipf.writestr("backup_info.json", json.dumps(info, indent=2))
            
            # محاسبه سایز و checksum
            size_bytes = backup_file.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            # محاسبه MD5 checksum
            with open(backup_file, 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
            
            # به‌روزرسانی آمار
            self.stats['total_backups'] += 1
            self.stats['last_backup'] = datetime.now().isoformat()
            self.stats['total_size_mb'] += size_mb
            self.stats['backup_history'].append({
                'name': backup_name,
                'time': timestamp,
                'size_mb': round(size_mb, 2),
                'md5': md5
            })
            
            # نگه داشتن فقط ۱۰۰ رکورد آخر
            if len(self.stats['backup_history']) > 100:
                self.stats['backup_history'] = self.stats['backup_history'][-100:]
            
            logger.info(f"✅ Backup completed: {backup_file} ({size_mb:.2f} MB)")
            
            return {
                'success': True,
                'file': str(backup_file),
                'name': backup_name,
                'size_mb': round(size_mb, 2),
                'md5': md5,
                'files_count': len(info['files'])
            }
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_ai_memory_backup(self) -> Dict:
        """
        پشتیبان‌گیری اختصاصی از حافظه AI
        (این تابع هر ساعت فراخوانی می‌شود)
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"ai_memory_{timestamp}"
        backup_file = self.backup_dir / f"{backup_name}.pkl.gz"
        
        try:
            if not self.memory_dir.exists():
                return {'success': False, 'error': 'Memory directory not found'}
            
            # جمع‌آوری همه فایل‌های حافظه
            memory_data = {
                'timestamp': datetime.now().isoformat(),
                'files': {}
            }
            
            for mem_file in self.memory_dir.glob("*.pkl"):
                with open(mem_file, 'rb') as f:
                    memory_data['files'][mem_file.name] = pickle.load(f)
            
            # فشرده‌سازی و ذخیره
            with gzip.open(backup_file, 'wb') as f:
                pickle.dump(memory_data, f)
            
            size_kb = backup_file.stat().st_size / 1024
            
            logger.info(f"🧠 AI Memory backup: {backup_file} ({size_kb:.1f} KB)")
            
            return {
                'success': True,
                'file': str(backup_file),
                'size_kb': round(size_kb, 1)
            }
            
        except Exception as e:
            logger.error(f"❌ AI Memory backup failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def restore_backup(self, backup_file: str, restore_ai_memory: bool = True) -> Dict:
        """
        بازیابی از پشتیبان
        
        Args:
            backup_file: نام فایل پشتیبان
            restore_ai_memory: آیا حافظه AI هم بازیابی شود؟
        """
        
        backup_path = self.backup_dir / backup_file
        
        if not backup_path.exists():
            return {'success': False, 'error': 'Backup file not found'}
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                
                # بررسی فایل info
                if 'backup_info.json' in zipf.namelist():
                    info = json.loads(zipf.read('backup_info.json'))
                
                # بازیابی دیتابیس
                if 'database/oracle.db' in zipf.namelist():
                    # پشتیبان‌گیری از دیتابیس فعلی (قبل از بازنویسی)
                    current_backup = self.create_backup("before_restore")
                    
                    # بازنویسی
                    zipf.extract('database/oracle.db', 'data/')
                    logger.info("  ✅ Database restored")
                
                # بازیابی حافظه AI
                if restore_ai_memory:
                    for mem_file in zipf.namelist():
                        if mem_file.startswith('memory/'):
                            zipf.extract(mem_file, './')
                            logger.info(f"  ✅ Restored: {mem_file}")
                
                # بازیابی تنظیمات
                for config_file in zipf.namelist():
                    if config_file.startswith('config/'):
                        zipf.extract(config_file, './')
                        logger.info(f"  ✅ Restored: {config_file}")
            
            logger.info(f"✅ Restored from: {backup_file}")
            
            return {
                'success': True,
                'backup': backup_file,
                'timestamp': info.get('timestamp') if 'info' in locals() else None
            }
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def cleanup_old_backups(self, keep_days: int = 7) -> Dict:
        """
        پاک کردن پشتیبان‌های قدیمی
        
        Args:
            keep_days: تعداد روزهایی که پشتیبان نگه داشته شود
        """
        
        cutoff = datetime.now() - timedelta(days=keep_days)
        deleted = []
        kept = []
        
        for backup_file in self.backup_dir.glob("backup_*.zip"):
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if mtime < cutoff:
                size = backup_file.stat().st_size / (1024 * 1024)
                backup_file.unlink()
                deleted.append({
                    'name': backup_file.name,
                    'size_mb': round(size, 2),
                    'age_days': (datetime.now() - mtime).days
                })
                logger.info(f"🗑️ Deleted old backup: {backup_file.name}")
            else:
                kept.append(backup_file.name)
        
        # پاک کردن پشتیبان‌های AI Memory قدیمی
        for mem_backup in self.backup_dir.glob("ai_memory_*.pkl.gz"):
            mtime = datetime.fromtimestamp(mem_backup.stat().st_mtime)
            if mtime < cutoff:
                mem_backup.unlink()
                logger.info(f"🗑️ Deleted old AI memory: {mem_backup.name}")
        
        result = {
            'success': True,
            'deleted_count': len(deleted),
            'deleted': deleted,
            'kept_count': len(kept),
            'kept': kept[:10]  # فقط ۱۰ تا برای نمایش
        }
        
        logger.info(f"🧹 Cleanup completed: {len(deleted)} backups deleted")
        
        return result
    
    def list_backups(self) -> List[Dict]:
        """لیست تمام پشتیبان‌های موجود"""
        
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("backup_*.zip"), 
                                  key=lambda p: p.stat().st_mtime, 
                                  reverse=True):
            
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            
            # خواندن info اگر موجود باشد
            info = {}
            try:
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    if 'backup_info.json' in zipf.namelist():
                        info = json.loads(zipf.read('backup_info.json'))
            except:
                pass
            
            backups.append({
                'name': backup_file.name,
                'date': mtime.strftime('%Y-%m-%d %H:%M:%S'),
                'size_mb': round(size_mb, 2),
                'age_days': round((datetime.now() - mtime).days, 1),
                'info': info
            })
        
        return backups
    
    def start_auto_backup(self):
        """شروع پشتیبان‌گیری خودکار در thread جدا"""
        
        def run_schedule():
            schedule.every(self.auto_backup_interval).hours.do(self.create_backup)
            schedule.every().hour.do(self.create_ai_memory_backup)
            schedule.every().day.at("03:00").do(self.cleanup_old_backups, keep_days=KEEP_BACKUPS_DAYS)
            
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=run_schedule, daemon=True)
        thread.start()
        logger.info(f"⏰ Auto-backup scheduled every {self.auto_backup_interval} hours")
    
    def get_stats(self) -> Dict:
        """دریافت آمار پشتیبان‌گیری"""
        
        return {
            'total_backups': self.stats['total_backups'],
            'last_backup': self.stats['last_backup'],
            'total_size_mb': round(self.stats['total_size_mb'], 2),
            'backup_dir': str(self.backup_dir),
            'free_space_mb': self._get_free_space(),
            'recent_backups': self.list_backups()[:5]
        }
    
    def _get_free_space(self) -> float:
        """دریافت فضای خالی دیسک (مگابایت)"""
        import shutil
        disk = shutil.disk_usage(self.backup_dir)
        return disk.free / (1024 * 1024)
