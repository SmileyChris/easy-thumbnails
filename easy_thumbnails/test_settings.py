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
    'easy_thumbnails.tests',
]

SECRET_KEY = '123,sdjfhgu7113o4tsdfy-gkasdhfgi7v293984753'

# This is only needed for the 1.4.X test environment
USE_TZ = True
