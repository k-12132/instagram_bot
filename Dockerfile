# استخدام بايثون 3.13
FROM python:3.13-slim

# تعيين مجلد العمل
WORKDIR /app

# نسخ الملفات المطلوبة
COPY requirements.txt .
COPY bot.py .

# تثبيت التبعيات
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل البوت
CMD ["python", "bot.py"]
