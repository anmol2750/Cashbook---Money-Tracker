from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-cashbook-development-key-change-before-deploying"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "cashbook",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "cashbook.middleware.UserLanguageMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
AUTH_USER_MODEL = "cashbook.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("hi", "हिन्दी"),
    ("as", "অসমীয়া"),
    ("bn", "বাংলা"),
    ("gu", "ગુજરાતી"),
    ("kn", "ಕನ್ನಡ"),
    ("ks", "کٲشُر"),
    ("ml", "മലയാളം"),
    ("mr", "मराठी"),
    ("ne", "नेपाली"),
    ("or", "ଓଡ଼ିଆ"),
    ("pa", "ਪੰਜਾਬੀ"),
    ("sa", "संस्कृतम्"),
    ("ta", "தமிழ்"),
    ("te", "తెలుగు"),
    ("ur", "اردو"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if not DEBUG or os.environ.get("EMAIL_HOST")
    else "django.core.mail.backends.console.EmailBackend"
)
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", DEFAULT_EMAIL_BACKEND)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "").strip().lower() in {"1", "true", "yes"}
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Cashbook <noreply@localhost>")
EMAIL_VERIFICATION_OTP_TTL_SECONDS = int(os.environ.get("EMAIL_VERIFICATION_OTP_TTL_SECONDS", "600"))
EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS = int(os.environ.get("EMAIL_VERIFICATION_RESEND_COOLDOWN_SECONDS", "60"))
EMAIL_VERIFICATION_MAX_ATTEMPTS = int(os.environ.get("EMAIL_VERIFICATION_MAX_ATTEMPTS", "5"))
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"
