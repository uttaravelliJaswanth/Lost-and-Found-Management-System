"""
Django settings for the NITC Lost and Found Management System.

Technology stack (SRS 2.4 / 2.5): Python + Django, SQLite, Pillow,
HTML / CSS / JavaScript via Django templates.

The project is configured for LOCAL DEVELOPMENT by default (SRS 6.2).
Production hardening required by NFR-10 is switched on automatically when
DJANGO_DEBUG is set to "False" (see the bottom of this file).
"""
import os
from pathlib import Path

import shutil
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


IS_VERCEL = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))

# ---------------------------------------------------------------------------
# Core security settings (NFR-10)
# ---------------------------------------------------------------------------
# A development-only fallback key is used when DJANGO_SECRET_KEY is not set.
# NEVER use the fallback in production - set DJANGO_SECRET_KEY instead.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-nitc-lost-found-group18-change-me",
)
DEBUG = env_bool("DJANGO_DEBUG", not IS_VERCEL)
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "127.0.0.1,localhost,testserver,.vercel.app",
    ).split(",")
    if h.strip()
]
if os.environ.get("VERCEL_URL"):
    ALLOWED_HOSTS.append(os.environ["VERCEL_URL"])

CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
]
if os.environ.get("VERCEL_URL"):
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.environ['VERCEL_URL']}")

# ---------------------------------------------------------------------------
# Applications (NFR-13: separation of models, forms, views, urls, templates)
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",          # FR-34, FR-35 - Django Admin
    "django.contrib.auth",           # FR-01..FR-03, NFR-07
    "django.contrib.contenttypes",
    "django.contrib.sessions",       # Session class (Class Diagram 1)
    "django.contrib.messages",       # success / info / error feedback (3.1)
    "django.contrib.staticfiles",
    # Project apps
    "accounts.apps.AccountsConfig",  # Class Diagram 1
    "items.apps.ItemsConfig",        # Class Diagram 2
    "claims.apps.ClaimsConfig",      # Class Diagram 3
    "dashboard.apps.DashboardConfig",  # DashboardService (Class Diagram 3)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # NFR-09
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lostfound.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "items.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "lostfound.wsgi.application"

# ---------------------------------------------------------------------------
# Database - SQLite (SRS 2.5 / 6.1), managed via Django ORM + migrations
# ---------------------------------------------------------------------------
# Use a shared persistent database in production; SQLite is local only.
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(
        DATABASE_URL, conn_max_age=0 if IS_VERCEL else 60,
        ssl_require=IS_VERCEL,
    )}
    if IS_VERCEL and DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
        raise ImproperlyConfigured("Vercel requires a PostgreSQL DATABASE_URL.")
elif IS_VERCEL:
    raise ImproperlyConfigured("Set DATABASE_URL to a persistent PostgreSQL database before deploying.")
else:
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }}

# ---------------------------------------------------------------------------
# Authentication (NFR-07: Django password management)
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# UI-02: unauthenticated users are redirected to the login page.
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:dashboard"
LOGOUT_REDIRECT_URL = "items:home"

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files (CSS / JavaScript) and media files (uploaded photographs)
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Uploaded photographs are stored as media files; only their reference
# is kept in the database (SRS 2.1 item 4, 6.1).
MEDIA_URL = "/media/"
if IS_VERCEL:
    MEDIA_ROOT = Path("/tmp/media")
    _bundled_media = BASE_DIR / "media"
    if _bundled_media.exists() and not MEDIA_ROOT.exists():
        shutil.copytree(_bundled_media, MEDIA_ROOT, dirs_exist_ok=True)
    else:
        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
else:
    MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# ---------------------------------------------------------------------------
# Application-specific settings
# ---------------------------------------------------------------------------
# FR-09 / NFR-03 / NFR-11: photo upload restrictions.
LOSTFOUND_MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB
LOSTFOUND_ALLOWED_PHOTO_TYPES = ("image/jpeg", "image/png", "image/webp")

# TBD-04: The SRS (Appendix B.5 / Appendix C) records that the current
# implementation does NOT restrict claims to FOUND reports. That behaviour is
# the default here; set LOSTFOUND_RESTRICT_CLAIMS_TO_FOUND=True to enforce it
# once the requirement is confirmed.
LOSTFOUND_RESTRICT_CLAIMS_TO_FOUND = env_bool("LOSTFOUND_RESTRICT_CLAIMS_TO_FOUND", False)

LOSTFOUND_ITEMS_PER_PAGE = 12
LOSTFOUND_RECENT_ON_HOME = 8

# ---------------------------------------------------------------------------
# Production hardening (NFR-10, SRS 3.4) - applied when DEBUG is disabled.
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    X_FRAME_OPTIONS = "DENY"

# Google OAuth: enabled only when both credentials are configured.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_LOGIN_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
INSTALLED_APPS += ["allauth", "allauth.account", "allauth.socialaccount", "allauth.socialaccount.providers.google"]
MIDDLEWARE += ["allauth.account.middleware.AccountMiddleware"]
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend", "allauth.account.auth_backends.AuthenticationBackend"]
SOCIALACCOUNT_LOGIN_ON_GET = False
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = False
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = False
SOCIALACCOUNT_PROVIDERS = {"google": {"SCOPE": ["profile", "email"], "OAUTH_PKCE_ENABLED": True}}
if GOOGLE_LOGIN_ENABLED:
    SOCIALACCOUNT_PROVIDERS["google"]["APP"] = {"client_id": GOOGLE_CLIENT_ID, "secret": GOOGLE_CLIENT_SECRET, "key": ""}
