from django.apps import AppConfig


class EasyThumbnails(AppConfig):
    name = 'easy_thumbnails'
    verbose_name = "Easy Thumbnails"

    def ready(self):
        from django.conf import settings
        from easy_thumbnails.signals import thumbnail_created
        if hasattr(settings, 'THUMBNAIL_OPTIMIZE_COMMAND'):
            from easy_thumbnails.optimize.post_processor import optimize_thumbnail
            assert isinstance(settings.THUMBNAIL_OPTIMIZE_COMMAND, dict)
            thumbnail_created.connect(optimize_thumbnail, dispatch_uid='optimize_thumbnail')
