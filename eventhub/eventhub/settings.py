# eventhub/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# This will load your .env file on the server
load_dotenv(os.path.join(BASE_DIR, '.env'))

# --- Core Security & Deployment Settings ---

SECRET_KEY = os.environ.get("SECRET_KEY")

# DEBUG must be False in production
DEBUG = False

# Replace 'yourusername' with your actual PythonAnywhere username
ALLOWED_HOSTS = ['bigbangbashers.pythonanywhere.com']
CSRF_TRUSTED_ORIGINS = ['https://bigbangbashers.pythonanywhere.com']


# --- Application Definition ---

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise is not needed on PythonAnywhere
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eventhub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'eventhub.wsgi.application'

# --- Database ---
# Configure this with your MySQL details from the PythonAnywhere "Databases" tab
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bigbangbashers$eventhubdb', # e.g., 'aprampreet$eventhubdb'
        'USER': 'bigbangbashers',                 # e.g., 'aprampreet'
        'PASSWORD': 'bigbangbashersport8000',      # The password you set on the Databases tab
        'HOST': 'bigbangbashers.mysql.pythonanywhere-services.com',
        'PORT': '3306',
    }
}


# --- Static and Media Files ---

# Static files (CSS, JavaScript)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (User-uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# --- Other Settings ---

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Celery/Redis is not supported on the PythonAnywhere free tier
# CELERY_BROKER_URL = os.environ.get("REDIS_URL")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = "bigbangbashers@gmail.com"

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Jazzmin Admin Theme Settings ---
JAZZMIN_SETTINGS = {
    "site_title": "EventHub Admin",
    "site_header": "EventHub Dashboard",
    "site_brand": "Big Bang Bashers",
    "welcome_sign": "Welcome to your custom dashboard",
    "copyright": "Big Bang Bashers © 2025",
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["auth", "accounts", "core"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "accounts.Profile": "fas fa-id-card",
        "core.Event": "fas fa-calendar-alt",
    },
    "show_ui_builder": True,
}
