# ai/ai_memory_manager.py
"""
مدیریت حافظه بلندمدت AI با پشتیبان خودکار
- ذخیره خودکار هر ساعت
- پشتیبان‌گیری روزانه
- فشرده‌سازی
- بازیابی از پشتیبان
- آمار حافظه
"""

import pickle
import gzip
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import threading
import schedule
import time
import logging
from typing import Dict, List, Any, Optional
import hashlib
import os

logger = logging.getLogger(__name__)

class AIMemoryManager:
    """
    مدیریت حافظه AI با پشتیبان‌گیری خودکار
    """
    
    def __init__(self, memory_dir: str = "memory", 
                 backup_dir: str = "backups/ai_memory",
                 auto_save_interval: int = 60,  # دقیقه
                 compression: bool = True):
        
        self.memory_dir = Path(memory_dir)
        self.backup_dir = Path(backup_dir)
        self.auto_save_interval = auto_save_interval
        self.compression = compression
        
        # ایجاد پوشه‌ها
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # حافظه‌های مختلف
        self.memories = {
            'patterns': [],        # الگوهای کشف شده
            'learnings': [],        # یادگیری‌ها
            'user_memories': {},    # حافظه کاربران
            'predictions': [],       # پیش‌بینی‌های گذشته
            'correlations': {},      # همبستگی‌ها
            'api_keys': {},          # API keyهای ذخیره شده (encode شده)
            'stats': {}              # آمار
        }
        
        # لاک برای thread safety
        self.lock = threading.Lock()
        
        # بارگذاری حافظه قبلی
        self.load_memory()
        
        # شروع thread پشتیبان‌گیری خودکار
        self.start_auto_save()
        
        logger.info(f"🧠 AIMemoryManager initialized: {self.memory_dir}")
    
    # ==================== توابع ذخیره و بارگذاری ====================
    
    def save_memory(self, memory_type: str = None):
        """
        ذخیره حافظه در فایل
        """
        with self.lock:
            try:
                if memory_type:
                    # ذخیره یک نوع خاص
                    if memory_type in self.memories:
                        self._save_single_memory(memory_type)
                else:
                    # ذخیره همه
                    for mem_type in self.memories:
                        self._save_single_memory(mem_type)
                
                logger.debug(f"💾 Memory saved: {memory_type or 'all'}")
                
            except Exception as e:
                logger.error(f"Error saving memory: {e}")
    
    def _save_single_memory(self, memory_type: str):
        """ذخیره یک نوع حافظه"""
        
        file_path = self.memory_dir / f"{memory_type}.pkl"
        
        # فشرده‌سازی اگر لازم باشد
        if self.compression:
            file_path = Path(str(file_path) + ".gz")
            with gzip.open(file_path, 'wb') as f:
                pickle.dump(self.memories[memory_type], f)
        else:
            with open(file_path, 'wb') as f:
                pickle.dump(self.memories[memory_type], f)
    
    def load_memory(self):
        """بارگذاری حافظه از فایل"""
        
        with self.lock:
            for memory_type in self.memories.keys():
                self._load_single_memory(memory_type)
            
            logger.info(f"📚 Memory loaded: {len(self.memories['patterns'])} patterns, "
                       f"{len(self.memories['learnings'])} learnings, "
                       f"{len(self.memories['user_memories'])} users")
    
    def _load_single_memory(self, memory_type: str):
        """بارگذاری یک نوع حافظه"""
        
        # بررسی فایل معمولی
        file_path = self.memory_dir / f"{memory_type}.pkl"
        if file_path.exists():
            with open(file_path, 'rb') as f:
                self.memories[memory_type] = pickle.load(f)
            return
        
        # بررسی فایل فشرده
        gz_path = self.memory_dir / f"{memory_type}.pkl.gz"
        if gz_path.exists():
            with gzip.open(gz_path, 'rb') as f:
                self.memories[memory_type] = pickle.load(f)
            return
        
        # اگر فایل نبود، مقدار پیش‌فرض
        if memory_type == 'patterns':
            self.memories[memory_type] = []
        elif memory_type == 'learnings':
            self.memories[memory_type] = []
        elif memory_type == 'user_memories':
            self.memories[memory_type] = {}
        elif memory_type == 'predictions':
            self.memories[memory_type] = []
        elif memory_type == 'correlations':
            self.memories[memory_type] = {}
        elif memory_type == 'api_keys':
            self.memories[memory_type] = {}
        elif memory_type == 'stats':
            self.memories[memory_type] = {}
    
    # ==================== توابع پشتیبان‌گیری ====================
    
    def create_backup(self, backup_name: str = None) -> Dict:
        """
        ایجاد پشتیبان کامل از حافظه
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not backup_name:
            backup_name = f"ai_memory_backup_{timestamp}"
        
        backup_file = self.backup_dir / f"{backup_name}.pkl.gz"
        
        try:
            # ذخیره موقت همه حافظه‌ها
            self.save_memory()
            
            # ایجاد بسته کامل
            complete_memory = {
                'timestamp': timestamp,
                'version': '1.0',
                'memories': self.memories,
                'stats': {
                    'patterns': len(self.memories['patterns']),
                    'learnings': len(self.memories['learnings']),
                    'users': len(self.memories['user_memories']),
                    'predictions': len(self.memories['predictions'])
                }
            }
            
            # فشرده‌سازی و ذخیره
            with gzip.open(backup_file, 'wb') as f:
                pickle.dump(complete_memory, f)
            
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            
            logger.info(f"💾 AI Memory backup created: {backup_file} ({size_mb:.2f} MB)")
            
            return {
                'success': True,
                'file': str(backup_file),
                'size_mb': round(size_mb, 2),
                'stats': complete_memory['stats']
            }
            
        except Exception as e:
            logger.error(f"❌ AI Memory backup failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def restore_backup(self, backup_file: str) -> Dict:
        """
        بازیابی حافظه از پشتیبان
        """
        
        backup_path = self.backup_dir / backup_file
        if not backup_path.exists():
            return {'success': False, 'error': 'Backup file not found'}
        
        try:
            with gzip.open(backup_path, 'rb') as f:
                complete_memory = pickle.load(f)
            
            with self.lock:
                self.memories = complete_memory['memories']
                
                # ذخیره بعد از بازیابی
                self.save_memory()
            
            logger.info(f"✅ AI Memory restored from: {backup_file}")
            
            return {
                'success': True,
                'timestamp': complete_memory.get('timestamp'),
                'stats': complete_memory.get('stats')
            }
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def list_backups(self) -> List[Dict]:
        """لیست پشتیبان‌های موجود"""
        
        backups = []
        for backup_file in sorted(self.backup_dir.glob("ai_memory_backup_*.pkl.gz"),
                                  key=lambda p: p.stat().st_mtime,
                                  reverse=True):
            
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            
            backups.append({
                'name': backup_file.name,
                'date': mtime.strftime('%Y-%m-%d %H:%M:%S'),
                'size_mb': round(size_mb, 2),
                'age_days': round((datetime.now() - mtime).days, 1)
            })
        
        return backups
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """پاک کردن پشتیبان‌های قدیمی"""
        
        cutoff = datetime.now() - timedelta(days=keep_days)
        deleted = 0
        
        for backup_file in self.backup_dir.glob("ai_memory_backup_*.pkl.gz"):
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if mtime < cutoff:
                backup_file.unlink()
                deleted += 1
                logger.info(f"🗑️ Deleted old AI memory backup: {backup_file.name}")
        
        return {'deleted': deleted}
    
    # ==================== توابع مدیریت حافظه ====================
    
    def add_pattern(self, pattern: Dict):
        """افزودن الگوی جدید"""
        with self.lock:
            self.memories['patterns'].append({
                **pattern,
                'timestamp': datetime.now().isoformat()
            })
            # محدودیت اندازه
            if len(self.memories['patterns']) > 10000:
                self.memories['patterns'] = self.memories['patterns'][-10000:]
    
    def add_learning(self, learning: Dict):
        """افزودن یادگیری جدید"""
        with self.lock:
            self.memories['learnings'].append({
                **learning,
                'timestamp': datetime.now().isoformat()
            })
            if len(self.memories['learnings']) > 10000:
                self.memories['learnings'] = self.memories['learnings'][-10000:]
    
    def add_user_memory(self, user_id: int, key: str, value: Any):
        """ذخیره حافظه کاربر"""
        with self.lock:
            if user_id not in self.memories['user_memories']:
                self.memories['user_memories'][user_id] = {}
            self.memories['user_memories'][user_id][key] = {
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_user_memory(self, user_id: int, key: str = None) -> Any:
        """دریافت حافظه کاربر"""
        if user_id not in self.memories['user_memories']:
            return None if key else {}
        
        if key:
            data = self.memories['user_memories'][user_id].get(key)
            return data['value'] if data else None
        else:
            return self.memories['user_memories'][user_id]
    
    def add_prediction(self, prediction: Dict):
        """ذخیره پیش‌بینی برای یادگیری آینده"""
        with self.lock:
            self.memories['predictions'].append({
                **prediction,
                'timestamp': datetime.now().isoformat()
            })
            if len(self.memories['predictions']) > 10000:
                self.memories['predictions'] = self.memories['predictions'][-10000:]
    
    def save_api_key(self, user_id: int, api_type: str, api_key: str):
        """ذخیره API key (با encode)"""
        with self.lock:
            if user_id not in self.memories['api_keys']:
                self.memories['api_keys'][user_id] = {}
            
            # encode ساده (در نسخه واقعی از encryption استفاده کن)
            encoded = base64.b64encode(api_key.encode()).decode()
            
            self.memories['api_keys'][user_id][api_type] = {
                'key': encoded,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_api_key(self, user_id: int, api_type: str) -> Optional[str]:
        """دریافت API key ذخیره شده"""
        if user_id not in self.memories['api_keys']:
            return None
        
        data = self.memories['api_keys'][user_id].get(api_type)
        if data:
            # decode
            return base64.b64decode(data['key'].encode()).decode()
        return None
    
    # ==================== آمار ====================
    
    def get_stats(self) -> Dict:
        """دریافت آمار حافظه"""
        
        return {
            'patterns': len(self.memories['patterns']),
            'learnings': len(self.memories['learnings']),
            'users': len(self.memories['user_memories']),
            'predictions': len(self.memories['predictions']),
            'api_keys': sum(len(keys) for keys in self.memories['api_keys'].values()),
            'backups': len(list(self.backup_dir.glob("*.pkl.gz"))),
            'memory_size_mb': self._get_memory_size()
        }
    
    def _get_memory_size(self) -> float:
        """محاسبه حجم حافظه"""
        total = 0
        for file in self.memory_dir.glob("*"):
            total += file.stat().st_size
        return round(total / (1024 * 1024), 2)
    
    # ==================== پشتیبان‌گیری خودکار ====================
    
    def start_auto_save(self):
        """شروع ذخیره و پشتیبان‌گیری خودکار"""
        
        def run_schedule():
            # ذخیره هر 60 دقیقه
            schedule.every(self.auto_save_interval).minutes.do(self.save_memory)
            
            # پشتیبان روزانه
            schedule.every().day.at("02:00").do(self.create_backup)
            
            # پشتیبان هفتگی کامل
            schedule.every().monday.at("03:00").do(self.create_backup, "weekly_backup")
            
            # پاک کردن پشتیبان‌های قدیمی هر هفته
            schedule.every().sunday.at("04:00").do(self.cleanup_old_backups, keep_days=30)
            
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=run_schedule, daemon=True)
        thread.start()
        logger.info(f"⏰ Auto-save scheduled every {self.auto_save_interval} minutes")
