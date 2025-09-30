from pathlib import Path
import os
from dotenv import load_dotenv

def strtobool(value: str) -> bool:
    v = value.strip().lower()
    if v in {"y","yes","t","true","on","1"}: return True
    if v in {"n","no","f","false","off","0"}: return False
    raise ValueError(f"Valor booleano inválido: {value}")

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ===== Ambiente / Segurança =====
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG      = strtobool(os.getenv('DEBUG', 'False'))
PRODUCTION = strtobool(os.getenv('PRODUCTION', 'False'))

SITE_HOST   = os.getenv('SITE_HOST', '127.0.0.1').strip()      # ex.: 147.79.82.119
IS_HTTPS    = strtobool(os.getenv('IS_HTTPS', 'False'))        # False por enquanto
SITE_PREFIX = os.getenv('SITE_PREFIX', '').rstrip('/')         # "" no dev, "/colmeia-online" no prod

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
if SITE_HOST and SITE_HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(SITE_HOST)

SCHEME = 'https' if IS_HTTPS else 'http'

# em vez de apenas [f'{SCHEME}://{SITE_HOST}'], use:
CSRF_TRUSTED_ORIGINS = list({
    f'http://{SITE_HOST}',
    f'https://{SITE_HOST}',
})

USE_X_FORWARDED_HOST = True
if IS_HTTPS:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ===== Banco (SQLite em DEV, Postgres em PROD) =====
if PRODUCTION:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("PG_NAME", "colmeia_db"),
            "USER": os.getenv("PG_USER", "colmeia_user"),
            "PASSWORD": os.getenv("PG_PASSWORD", ""),
            "HOST": os.getenv("PG_HOST", "127.0.0.1"),
            "PORT": os.getenv("PG_PORT", "5432"),
        }
    }
else:
    # Em dev, use SQLite; você pode manter DB_NAME no .env, senão cai no 'db.sqlite3'
    sqlite_name = os.getenv('DB_NAME', 'db') + '.sqlite3'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / sqlite_name,
        }
    }

# Application definition
INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    "accounts",
    "apiary",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

SESSION_COOKIE_PATH = "/colmeia-online"
CSRF_COOKIE_PATH    = "/colmeia-online"

SESSION_COOKIE_NAME = "colmeia_sessionid"
CSRF_COOKIE_NAME    = "colmeia_csrftoken"

SESSION_COOKIE_SECURE = False  # mude p/ True quando usar HTTPS
CSRF_COOKIE_SECURE    = False
SESSION_COOKIE_SAMESITE = "Lax"

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'core.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ===== Locale/Timezone =====
LANGUAGE_CODE = 'pt-BR'
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ===== Subcaminho e arquivos estáticos/mídia =====
# Em prod, teremos SITE_PREFIX="/colmeia-online"; no dev fica vazio.
FORCE_SCRIPT_NAME = SITE_PREFIX if SITE_PREFIX else None

def _url_with_prefix(suffix: str) -> str:
    prefix = SITE_PREFIX if SITE_PREFIX else ''
    return f"{prefix}{suffix}"

STATIC_URL = _url_with_prefix('/static/')
MEDIA_URL  = _url_with_prefix('/media/')

# Onde o collectstatic deposita os arquivos para o Nginx em PROD
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT  = BASE_DIR / 'media'

# Em DEV, se você tem uma pasta-fonte de estáticos do projeto, declare aqui:
if DEBUG:
    # use "static_src" como origem (evita conflito com STATIC_ROOT)
    STATICFILES_DIRS = [BASE_DIR / 'static_src'] if (BASE_DIR / 'static_src').exists() else []

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
