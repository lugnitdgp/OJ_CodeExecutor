import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_ROOT = os.path.join(BASE_DIR, "static")

# DATABASES = {
#     'default': {
#         # Database driver
#         'ENGINE': 'django.db.backends.sqlite3',
#         # Replace below with Database Name if using other database engines
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    "django.contrib.auth",
    'accounts.apps.AccountsConfig',
    "interface.apps.InterfaceConfig",
    'django_celery_results',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': 5432,
    }
}

SECRET_KEY = config("SECRET_KEY")

CELERY_BROKER_URL = config("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

FILE_HASHES = {}

basedir = os.path.abspath(os.path.dirname(__file__))

enginedir = os.path.abspath(os.path.join(basedir, "safeexec"))

engine_path = os.path.join(enginedir, "safeexec")

staticdir = os.path.abspath(os.path.join(basedir, "static"))
