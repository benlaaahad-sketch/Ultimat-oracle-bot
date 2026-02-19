# utils/auto_backup.py
"""
اسکریپت پشتیبان‌گیری خودکار از کل سیستم
این اسکریپت به صورت cron اجرا می‌شود
"""

import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path
import shutil
import json
import logging
import argparse

# تنظیم لاگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('auto_backup')

def create_system_backup(backup_dir: str = "backups", 
                        include_logs: bool = True,
                        compress: bool = True) -> str:
    """
    ایجاد پشتیبان کامل از سیستم
    
    Returns:
        مسیر فایل پشتیبان
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"system_backup_{timestamp}"
    backup_path = Path(backup_dir) / backup_name
    
    try:
        # ایجاد پوشه موقت
        temp_dir = backup_path.with_suffix('.tmp')
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. دیتابیس
        if Path("data/oracle.db").exists():
            shutil.copy2("data/oracle.db", temp_dir / "database.sqlite")
            logger.info("✅ Database backed up")
        
        # 2. حافظه AI
        if Path("memory").exists():
            shutil.copytree("memory", temp_dir / "memory", dirs_exist_ok=True)
            logger.info("✅ AI Memory backed up")
        
        # 3. تنظیمات
        config_files = ["config.py", ".env"]
        for cf in config_files:
            if Path(cf).exists():
                shutil.copy2(cf, temp_dir / cf)
        logger.info("✅ Config files backed up")
        
        # 4. لاگ‌ها (اختیاری)
        if include_logs and Path("logs").exists():
            log_dir = temp_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            # فقط 5 لاگ آخر
            logs = sorted(Path("logs").glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
            for log in logs:
                shutil.copy2(log, log_dir / log.name)
            logger.info(f"✅ {len(logs)} log files backed up")
        
        # 5. فایل info
        info = {
            'timestamp': timestamp,
            'datetime': datetime.now().isoformat(),
            'files': [str(f.relative_to(temp_dir)) for f in temp_dir.rglob("*") if f.is_file()],
            'system': {
                'python': sys.version,
                'cwd': str(Path.cwd())
            }
        }
        
        with open(temp_dir / "backup_info.json", 'w') as f:
            json.dump(info, f, indent=2)
        
        # ایجاد فایل نهایی
        if compress:
            final_file = Path(backup_dir) / f"{backup_name}.zip"
            with zipfile.ZipFile(final_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in temp_dir.rglob("*"):
                    if file.is_file():
                        zipf.write(file, file.relative_to(temp_dir))
            
            # پاک کردن پوشه موقت
            shutil.rmtree(temp_dir)
            
            size_mb = final_file.stat().st_size / (1024 * 1024)
            logger.info(f"✅ System backup created: {final_file} ({size_mb:.2f} MB)")
            
            return str(final_file)
        else:
            # rename پوشه موقت به نام نهایی
            final_path = Path(backup_dir) / backup_name
            temp_dir.rename(final_path)
            logger.info(f"✅ System backup created: {final_path}")
            return str(final_path)
            
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return ""

def cleanup_old_backups(backup_dir: str = "backups", keep_days: int = 7):
    """پاک کردن پشتیبان‌های قدیمی"""
    
    cutoff = datetime.now().timestamp() - (keep_days * 24 * 3600)
    deleted = 0
    
    for item in Path(backup_dir).iterdir():
        if item.is_file() and item.suffix in ['.zip', '.gz']:
            if item.stat().st_mtime < cutoff:
                item.unlink()
                deleted += 1
                logger.info(f"🗑️ Deleted old backup: {item.name}")
    
    logger.info(f"🧹 Cleanup completed: {deleted} files deleted")
    return deleted

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto backup system")
    parser.add_argument("--action", choices=['backup', 'cleanup'], default='backup')
    parser.add_argument("--keep-days", type=int, default=7)
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        backup_file = create_system_backup()
        if backup_file:
            print(f"BACKUP_FILE={backup_file}")
    else:
        cleanup_old_backups(keep_days=args.keep_days)
