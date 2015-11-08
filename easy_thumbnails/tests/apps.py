try:
    from django.apps import AppConfig
except ImportError:
    # Early Django versions import everything in test, avoid the failure due to
    # AppConfig only existing in 1.7+
    AppConfig = object


class EasyThumbnailsTestConfig(AppConfig):
    name = 'easy_thumbnails.tests'
    label = 'easy_thumbnails_tests'
