import os

SITE_ID = 1

MEDIA_ROOT = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
MEDIA_URL = '/media/'

DATABASE_ENGINE = 'sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'easy_thumbnails',
    'easy_thumbnails.optimize',
    'easy_thumbnails.tests',
]

# This is only needed for the 1.4.X test environment
USE_TZ = True

SECRET_KEY = 'easy'

# add a mock image optimizing post processor
THUMBNAIL_OPTIMIZE_COMMAND = {
    'png': 'easy_thumbnails/tests/mockoptim.py {filename}',
    'gif': 'easy_thumbnails/tests/mockoptim.py {filename}',
    'jpg': 'easy_thumbnails/tests/mockoptim.py {filename}',
}

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
    },
    'loggers': {
        'easy_thumbnails.optimize': {
            'handlers': ['console'],
            'level': 'WARN',
        },
    }
}
