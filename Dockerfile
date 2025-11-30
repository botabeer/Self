FROM python:3.11-slim

# تعيين متغيرات البيئة
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات أولاً للاستفادة من الكاش
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# إنشاء مجلد قاعدة البيانات
RUN mkdir -p /app/data

# تشغيل التطبيق مع عامل واحد لتجنب تضارب قاعدة البيانات
CMD gunicorn --bind 0.0.0.0:${PORT:-10000} \
    --workers 1 \
    --timeout 120 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    app:app
