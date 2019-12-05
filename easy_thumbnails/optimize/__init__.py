from django.dispatch import receiver
from easy_thumbnails.optimize.post_processor import optimize_thumbnail

try:
    from easy_thumbnails.signals import thumbnail_created

    @receiver(thumbnail_created)
    def thumbnail_created_callback(sender, **kwargs):
        optimize_thumbnail(sender)
except ImportError:
    pass
