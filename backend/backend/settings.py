from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-+xc9n#)u3*e85(#^o7&0!h1+iz_7z1*q2lvswe%^$v+z6h71ty'

DEBUG = False

ALLOWED_HOSTS = [
    "scam-detector-1-m22a.onrender.com",
    "localhost",
    "127.0.0.1",
]

# ==========================
# CORS
# ==========================
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "https://scam-detector-1-m22a.onrender.com",
]

# ==========================
# SESSION SETTINGS
# ==========================
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = True
SESSION_SAVE_EVERY_REQUEST = True

# ==========================
# CSRF SETTINGS
# ==========================
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"

CSRF_TRUSTED_ORIGINS = [
    "https://scam-detector-1-m22a.onrender.com",
]