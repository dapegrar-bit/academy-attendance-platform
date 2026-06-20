from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'local-dev-secret-key-change-me')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')


def csv_env(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]

ALLOWED_HOSTS = csv_env('ALLOWED_HOSTS', 'localhost,127.0.0.1,.onrender.com')
CSRF_TRUSTED_ORIGINS = csv_env('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000,https://*.onrender.com')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'attendance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'academy_platform.urls'

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
                'attendance.context_processors.branding',
            ],
        },
    },
]

WSGI_APPLICATION = 'academy_platform.wsgi.application'
ASGI_APPLICATION = 'academy_platform.asgi.application'

# قاعدة البيانات
# محليًا: يستخدم SQLite للتجربة فقط.
# على Render/السيرفر: يجب استخدام PostgreSQL عبر DATABASE_URL حتى لا تضيع البيانات عند إعادة التشغيل أو النشر.
from django.core.exceptions import ImproperlyConfigured

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
REQUIRE_DATABASE_URL = os.environ.get('REQUIRE_DATABASE_URL', 'False').lower() in ('true', '1', 'yes')
RUNNING_ON_RENDER = bool(os.environ.get('RENDER') or os.environ.get('RENDER_SERVICE_ID') or os.environ.get('RENDER_EXTERNAL_HOSTNAME'))

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=not DEBUG,
        )
    }
elif REQUIRE_DATABASE_URL or (RUNNING_ON_RENDER and not DEBUG):
    raise ImproperlyConfigured(
        'DATABASE_URL مطلوب في بيئة الإنتاج/Render. '
        'لا تستخدم SQLite على Render لأنها لا تحفظ البيانات بعد إعادة التشغيل أو إعادة النشر. '
        'أنشئ PostgreSQL ثم أضف DATABASE_URL في Environment Variables.'
    )
else:
    SQLITE_PATH = os.environ.get('SQLITE_PATH', str(BASE_DIR / 'db.sqlite3'))
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': SQLITE_PATH,
        }
    }

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'auth'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'auth'

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# إعدادات البريد: افتراضيًا يتم طباعة الرسائل في السجلات. أضف SMTP عبر متغيرات البيئة لتفعيل الإرسال الحقيقي.
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@academy.local')
