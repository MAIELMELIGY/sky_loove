import os

from .settings import *

CELERY_BROKER_URL = os.getenv('REDIS_URL')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL')


STATIC_ROOT = "/opt/application/webapp/staticfiles"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "DEFAULT-CHARACTER-SET": "utf8",
        # "ENGINE": "dj_db_conn_pool.backends.mysql",
        "NAME": os.environ.get("MYSQL_DATABASE"),
        "USER": os.environ.get("MYSQL_USER"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD"),
        "HOST": os.environ.get("MYSQL_HOST"),
        "PORT": os.environ.get("MYSQL_PORT", 3306),
        "OPTIONS": {
            "sql_mode": "traditional",
        },
    }
}
