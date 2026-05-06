FROM python:3.10-slim

# C++ aur Audio processing ke liye zaroori tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements file copy karein
COPY requirements.txt .

# 🚨 MAGIC LINE: Pehle sirf CPU wala halka PyTorch install karein (Fast download)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Phir baqi saari libraries install karein
RUN pip install --no-cache-dir -r requirements.txt

# Poora code copy karein
COPY . .

# Server start karne ki command
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "backend.wsgi:application"]