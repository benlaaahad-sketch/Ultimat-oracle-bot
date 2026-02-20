FROM python:3.11-slim

WORKDIR /app

# نصب وابستگی‌های سیستم
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
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
COPY utils/ ./utils/

# نصب وابستگی‌های پایتون
RUN pip install --no-cache-dir -r requirements.txt

# متغیرهای محیطی
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# اجرای ربات
CMD ["python", "main.py"]
