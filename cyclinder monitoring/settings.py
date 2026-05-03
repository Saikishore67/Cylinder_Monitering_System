from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
# Reads your .env file and loads all values into memory
# Must be called before any os.getenv() calls below

BASE_DIR = Path(__file__).resolve().parent.parent
# Points to the root folder of your project
# Used by Django to find files

SECRET_KEY = os.getenv('SECRET_KEY')
# Loaded from .env — never hardcode this

DEBUG = os.getenv('DEBUG', 'False') == 'True'
# True during development, False in production

ALLOWED_HOSTS = ['*']
# Restrict this to your actual domain in production

INSTALLED_APPS = [
    'django.contrib.admin',       # Admin dashboard at /admin
    'django.contrib.auth',        # Built-in auth system
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',             # Django REST Framework — enables APIs
    'corsheaders',                # Allows Next.js frontend to call this backend
    'sensors',                    # Your app
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # CorsMiddleware must be as high as possible in the list
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cylinder_monitor.urls'
# Tells Django where to find the main URL file

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

WSGI_APPLICATION = 'cylinder_monitor.wsgi.application'

# ── Database ──────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ── REST Framework ────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'sensors.authentication.FirebaseAuthentication',
    ),
    # All endpoints use Firebase token verification by default
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # All endpoints require login by default
    # Individual views can override this with AllowAny
}

# ── CORS ──────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    # Next.js dev server
    # Add your production frontend URL here later
]
CORS_ALLOW_CREDENTIALS = True
# Allows frontend to send cookies and auth headers

# ── Localisation ──────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
# All timestamps stored and displayed in IST
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = 'static/'

FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')