# ============================================================
#  NADRA Queue App – settings.py
# ============================================================

from pathlib import Path

import os
from dotenv import load_dotenv

# .env file load karo
load_dotenv()

# Groq API Key yahan se uthayega
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'dev-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'backend.urls'

WSGI_APPLICATION = 'backend.wsgi.application'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ── INSTALLED APPS ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',

    # Your app
    'accounts',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ── MIDDLEWARE ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # MUST be FIRST
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True

# Production:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://10.0.2.2:8000",
# ]

# ── DATABASE ──────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME'  : BASE_DIR / 'db.sqlite3',
    }
}

# ── DJANGO REST FRAMEWORK ─────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',  # (File uploads ke liye)
        'rest_framework.parsers.FormParser',       #  (Form data ke liye)
    ],
}

# ── EMAIL (Gmail SMTP) ────────────────────────────────────────────────────────
# Step 1: Enable 2-Step Verification on your Google account
# Step 2: Go to https://myaccount.google.com/apppasswords
# Step 3: Create an App Password for "Mail" → copy the 16-char key
# Step 4: Replace the values below with your Gmail and that App Password

EMAIL_BACKEND         = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST            = 'smtp.gmail.com'
EMAIL_PORT            = 587
EMAIL_USE_TLS         = True
EMAIL_HOST_USER       = 'khandilawer1113@gmail.com'       # <-- change this
EMAIL_HOST_PASSWORD   = 'edeksgyflsnfsjhi'        # <-- paste App Password here
DEFAULT_FROM_EMAIL    = 'NADRA Queue App <your_gmail@gmail.com>'  # <-- change this

# ── LOGGING ───────────────────────────────────────────────────────────────────
LOGGING = {
    'version'           : 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module}: {message}',
            'style' : '{',
        },
    },
    'handlers': {
        'console': {
            'class'    : 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level'   : 'DEBUG',
    },
}

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:52869",
    "http://127.0.0.1:52869",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'