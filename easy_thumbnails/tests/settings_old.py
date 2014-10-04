"""
Don't add the test app to pre-1.7 versions of Django (since it's unnecessary
and we use the new application registry).
"""
from .settings import *   # NOQA

INSTALLED_APPS = INSTALLED_APPS[:]
INSTALLED_APPS.remove('easy_thumbnails.tests.apps.EasyThumbnailsTestConfig')
