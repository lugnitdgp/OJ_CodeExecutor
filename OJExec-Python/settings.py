import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
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

# SECURITY WARNING: Modify this secret key if using in production!
SECRET_KEY = '6few3nci_q_o@l1dlbk81%wcxe!*6r29yu629&d97!hiqat9fa'

FILE_HASHES = {}


