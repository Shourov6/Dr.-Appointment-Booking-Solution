"""
Django settings for DrSeba.com project.
"""

import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured('Set SECRET_KEY in the environment when DEBUG is disabled.')
    SECRET_KEY = 'django-insecure-local-development-only'

SHOW_DEMO_CREDENTIALS = DEBUG and os.getenv('SHOW_DEMO_CREDENTIALS', 'True').lower() == 'true'
DEMO_LOGIN_PASSWORD = os.getenv('DEMO_LOGIN_PASSWORD', 'DemoLogin123!')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'accounts',
    'doctors',
    'appointments',
    'payments',
    'dashboards',
    'ai_recommender',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.UserRoleMiddleware',
]

ROOT_URLCONF = 'drseba.urls'

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
                'django.template.context_processors.static',
                'accounts.context_processors.language_context',
                'accounts.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'drseba.wsgi.application'

# Database configuration
# Supported engines:
# - django.db.backends.postgresql (Supabase/PostgreSQL)
# - django.db.backends.mysql
# - django.db.backends.sqlite3
DB_ENGINE_CHOICE = os.getenv(
    'DB_ENGINE',
    'django.db.backends.sqlite3',
)
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DATABASE_URL')

if DATABASE_URL:
    from urllib.parse import parse_qs, unquote, urlparse

    database_url = urlparse(DATABASE_URL)
    database_query = parse_qs(database_url.query)

    if database_url.scheme not in ('postgres', 'postgresql'):
        raise ImproperlyConfigured(
            'DATABASE_URL must use a postgres:// or postgresql:// scheme.'
        )

    ssl_mode = (
        database_query.get('sslmode', ['require'])[0]
        if database_query.get('sslmode')
        else os.getenv('DB_SSLMODE', 'require')
    )
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': database_url.path.lstrip('/') or os.getenv('DB_NAME', 'postgres'),
            'USER': database_url.username or os.getenv('DB_USER', 'postgres'),
            'PASSWORD': unquote(database_url.password) if database_url.password else os.getenv('DB_PASSWORD', ''),
            'HOST': database_url.hostname or os.getenv('DB_HOST', ''),
            'PORT': str(database_url.port or os.getenv('DB_PORT', '5432')),
            'OPTIONS': {'sslmode': ssl_mode},
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '0')),
        }
    }
elif DB_ENGINE_CHOICE in (
    'django.db.backends.postgresql',
    'django.db.backends.postgresql_psycopg2',
):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'postgres'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', ''),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {'sslmode': os.getenv('DB_SSLMODE', 'require')},
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '0')),
        }
    }
elif DB_ENGINE_CHOICE == 'django.db.backends.mysql':
    # MySQL Configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'drseba_healthcare'),
            'USER': os.getenv('DB_USER', 'drseba_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            'ATOMIC_REQUESTS': True,
            'CONN_MAX_AGE': 0,  # Close connections after each request
        }
    }
else:
    # SQLite Configuration (Default for local development)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation - Removed strict validators for user-friendly registration
AUTH_PASSWORD_VALIDATORS = [
    # Allow any password for now - user friendly registration
]

# Internationalization
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Dhaka')
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login/Logout redirects
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF settings - Allow localhost and external domains (Serveo, ngrok)
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://localhost',
    'http://127.0.0.1',
    'https://127.0.0.1:8000',
    'https://localhost:8000',
    'https://localhost',
    'https://127.0.0.1',
]

# Add any *.serveo.net domains
CSRF_TRUSTED_ORIGINS += [
    'https://*.serveo.net',
    'http://*.serveo.net',
]

# CSRF Cookie settings
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Must be False for JavaScript to access CSRF token via forms
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS

# Message tags
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
