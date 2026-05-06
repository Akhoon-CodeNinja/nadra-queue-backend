# Python ka official image use karein
FROM python:3.10-slim

# System libraries install karein (FAISS aur Audio processing ke liye zaroori hain)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Project directory set karein
WORKDIR /app

# Requirements copy aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Poora project copy karein
COPY . .

# Static files collect karein
RUN python manage.py collectstatic --noinput

# Gunicorn ke zariye server start karein
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "backend.wsgi:application"]