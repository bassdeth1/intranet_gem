# Ubicación: /workspaces/intranet_gem/intranet_gem/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure_CAMBIA_ESTA_CLAVE_SECRETA_POR_UNA_NUEVA_Y_UNICA' # ¡GENERA UNA NUEVA!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1',]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000', 'http://127.0.0.1:8000',
    'https://localhost:8000', 'https://127.0.0.1:8000',
]

if 'CODESPACE_NAME' in os.environ and 'GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN' in os.environ:
    CODESPACE_URL_PRIMARY = f"{os.environ['CODESPACE_NAME']}.{os.environ['GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN']}"
    ALLOWED_HOSTS.append(CODESPACE_URL_PRIMARY)
    CSRF_TRUSTED_ORIGINS.append(f'https://{CODESPACE_URL_PRIMARY}')
    CODESPACE_URL_WITH_PORT = f"https://{os.environ['CODESPACE_NAME']}-8000.{os.environ['GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN']}"
    ALLOWED_HOSTS.append(CODESPACE_URL_WITH_PORT)
    CSRF_TRUSTED_ORIGINS.append(CODESPACE_URL_WITH_PORT)

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'intranet_core',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'intranet_gem.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates','DIRS': [os.path.join(BASE_DIR, 'templates')],'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]
WSGI_APPLICATION = 'intranet_gem.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3','NAME': BASE_DIR / 'db.sqlite3',}}
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = 'intranet_core:dashboard'
LOGOUT_REDIRECT_URL = 'intranet_core:dashboard'