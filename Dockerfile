# Dockerfile برای اجرای ربات در کانتینر
FROM python:3.10-slim

WORKDIR /app

# نصب وابستگی‌های سیستم
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# کپی فایل‌های مورد نیاز
COPY requirements.txt .
COPY config.py .
COPY main.py .
COPY bot/ ./bot/
COPY core/ ./core/
COPY database/ ./database/
COPY ai/ ./ai/
COPY web3_analyzer/ ./web3_analyzer/
COPY sports_analyzer/ ./sports_analyzer/
COPY event_analyzer/ ./event_analyzer/
COPY payment/ ./payment/
COPY admin/ ./admin/
COPY marketing/ ./marketing/
COPY utils/ ./utils/

# نصب وابستگی‌های پایتون
RUN pip install --no-cache-dir -r requirements.txt

# ایجاد پوشه‌های مورد نیاز
RUN mkdir -p data logs memory backups

# متغیرهای محیطی
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# حجم‌ها برای داده‌های پایدار
VOLUME ["/app/data", "/app/logs", "/app/memory", "/app/backups"]

# اجرای ربات
CMD ["python", "main.py"]
