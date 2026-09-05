import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail — single inbox: indistylex@gmail.com (Gmail SMTP + App Password)
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'indistylex@gmail.com')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', SUPPORT_EMAIL)
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # Gmail requires From address to match MAIL_USERNAME
    MAIL_DEFAULT_SENDER = os.environ.get(
        'MAIL_DEFAULT_SENDER',
        ('Indistylex', SUPPORT_EMAIL),
    )

    # Razorpay
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
    RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET')

    # OAuth - Google
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

    # OAuth - Facebook
    FACEBOOK_CLIENT_ID = os.environ.get('FACEBOOK_APP_ID', '')
    FACEBOOK_CLIENT_SECRET = os.environ.get('FACEBOOK_APP_SECRET', '')

    # File Uploads (default 20 MB — product forms often attach several photos)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 20 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

    # CSRF — token check is enough behind Nginx/ProxyFix; strict referrer
    # checks falsely fail on privacy browsers / www↔apex redirects.
    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT', 7200))
    WTF_CSRF_SSL_STRICT = os.environ.get('WTF_CSRF_SSL_STRICT', 'False').lower() == 'true'

    # Redis / Caching
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300

    # Celery
    CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # Pagination
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 10
    ADMIN_ITEMS_PER_PAGE = 20

    # Currency
    CURRENCY = 'INR'
    CURRENCY_SYMBOL = '₹'

    # Admin
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'indistylex@gmail.com')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-this-password')

    # AI product autofill (admin) — set GEMINI_API_KEY and/or OPENAI_API_KEY
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_VISION_MODEL = os.environ.get('GEMINI_VISION_MODEL', 'gemini-2.5-flash')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_VISION_MODEL = os.environ.get('OPENAI_VISION_MODEL', 'gpt-4o-mini')

    # Social profiles
    SOCIAL_FACEBOOK = os.environ.get('SOCIAL_FACEBOOK', 'https://www.facebook.com/indistylex')
    SOCIAL_INSTAGRAM = os.environ.get('SOCIAL_INSTAGRAM', 'https://www.instagram.com/indistylex_clothing')
    SOCIAL_TWITTER = os.environ.get('SOCIAL_TWITTER', 'https://twitter.com/indistylex')
    SOCIAL_PINTEREST = os.environ.get('SOCIAL_PINTEREST', 'https://www.pinterest.com/indistylex')
    SOCIAL_WHATSAPP = os.environ.get('SOCIAL_WHATSAPP', 'https://wa.me/916394142176')

    # Session security (permanent sessions refreshed each request)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', 28800))  # 8 hours
    SESSION_COOKIE_NAME = '__indistylex_sid'
    SESSION_REFRESH_EACH_REQUEST = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 604800  # 7 days
    REMEMBER_COOKIE_SECURE = os.environ.get('REMEMBER_COOKIE_SECURE', 'False').lower() == 'true'
    REMEMBER_COOKIE_SAMESITE = 'Lax'

    # Password hashing
    BCRYPT_LOG_ROUNDS = 13

    # JWT
    JWT_TOKEN_LIFETIME_DAYS = 7

    # Security headers
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files

    # Bump when logo/favicon/brand assets change (cache-busts browser tabs).
    ASSET_VERSION = os.environ.get('ASSET_VERSION', '20260903')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///Indistylex_dev.db'
    )
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    BCRYPT_LOG_ROUNDS = 12


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    REMEMBER_COOKIE_SECURE = os.environ.get(
        'REMEMBER_COOKIE_SECURE',
        os.environ.get('SESSION_COOKIE_SECURE', 'False'),
    ).lower() == 'true'
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME', 'http')
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost'
    CACHE_TYPE = 'SimpleCache'
    RATELIMIT_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
