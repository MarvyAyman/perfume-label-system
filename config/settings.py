"""
Django settings for the Perfume Label System.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
# In development this falls back to the placeholder below. In production,
# set the DJANGO_SECRET_KEY environment variable instead (see DEPLOYMENT.md).
# Generate one with:
#   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-1b$672lh!yss8@)_np5j6%ininakw93h$m+w9i9d(r@&^!_)c-',
)

# SECURITY WARNING: don't run with debug turned on in production!
# Set DJANGO_DEBUG=False as an environment variable on the server.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# Comma-separated list, e.g. DJANGO_ALLOWED_HOSTS=your-domain.com,123.45.67.89
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()
]

# Needed once you're behind HTTPS on a real domain — comma-separated, e.g.
# DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]

# Turn on once HTTPS is working (after the certbot step in DEPLOYMENT.md) —
# set the DJANGO_HTTPS=True environment variable. Left off by default so the
# site still works over plain HTTP before you have a certificate.
SECURE_SSL_REDIRECT = os.environ.get('DJANGO_HTTPS', 'False') == 'True'
SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'labels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # must sit after Session, before Common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'django.template.context_processors.i18n',  # needed for LANGUAGES/LANGUAGE_BIDI in templates
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# SQLite is fine to start; swap ENGINE/NAME for Postgres/MySQL later if needed.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- Internationalization ---------------------------------------------------
# https://docs.djangoproject.com/en/stable/topics/i18n/

USE_I18N = True
TIME_ZONE = 'Africa/Cairo'
USE_TZ = True

LANGUAGE_CODE = 'de'  # default/fallback language

LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
    ('de', 'Deutsch'),
]

# Languages that read right-to-left — templates use {% if LANGUAGE_BIDI %}
# to flip dir="rtl"/"ltr" automatically, so no per-language template forks.
LANGUAGES_BIDI = ['ar']

LOCALE_PATHS = [
    BASE_DIR / 'labels' / 'locale',
]


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # target for `manage.py collectstatic` in production


# Auth redirects

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'labels:print'
LOGOUT_REDIRECT_URL = 'login'

# --- Keep the user logged in across page refreshes / browser restarts ------
# This is server-side session persistence (Django's built-in, signed session
# cookie) — NOT localStorage. Storing auth state in localStorage is readable
# by any JS on the page (XSS risk), so it's deliberately avoided; the signed,
# httponly session cookie below is the secure way to get the same result.
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14        # session lasts 14 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False        # don't log out when the browser closes
SESSION_SAVE_EVERY_REQUEST = True              # each request pushes the 14-day expiry forward
SESSION_COOKIE_HTTPONLY = True                 # JS on the page can never read the session cookie


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
