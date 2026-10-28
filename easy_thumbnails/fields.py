from django.db.models import signals
from django.db.models.fields.files import FileField, ImageField
from easy_thumbnails import files


class ThumbnailerField(FileField):
    """
    A file field which provides easier access for retrieving (and generating)
    thumbnails.

    To use a different file storage for thumbnails, provide the
    ``thumbnail_storage`` keyword argument.
    """
    attr_class = files.ThumbnailerFieldFile

    def __init__(self, *args, **kwargs):
        # Arguments not explicitly defined so that the normal ImageField
        # positional arguments can be used.
        self.thumbnail_storage = kwargs.pop('thumbnail_storage', None)

        super().__init__(*args, **kwargs)


class ThumbnailerImageField(ThumbnailerField, ImageField):
    """
    An image field which provides easier access for retrieving (and generating)
    thumbnails.

    To use a different file storage for thumbnails, provide the
    ``thumbnail_storage`` keyword argument.

    To thumbnail the original source image before saving, provide the
    ``resize_source`` keyword argument, passing it a usual thumbnail option
    dictionary. For example::

        ThumbnailerImageField(
            ..., resize_source=dict(size=(100, 100), sharpen=True))
    """
    attr_class = files.ThumbnailerImageFieldFile

    def __init__(self, *args, **kwargs):
        # Arguments not explicitly defined so that the normal ImageField
        # positional arguments can be used.
        self.resize_source = kwargs.pop('resize_source', None)

        super().__init__(*args, **kwargs)


def _resize_source_images(sender, instance, raw=False, update_fields=None,
                          **kwargs):
    # Dimension columns may be collected before ImageField.pre_save().
    if raw:
        return
    for field in sender._meta.fields:
        if (isinstance(field, ThumbnailerImageField) and field.resize_source
                and (field.width_field or field.height_field)
                and (update_fields is None or field.name in update_fields)):
            image = getattr(instance, field.attname)
            if image and not image._committed:
                image.save(image.name, image.file, save=False)


def _connect_resize_source_images(sender, **kwargs):
    if any(isinstance(field, ThumbnailerImageField) and field.resize_source
           and (field.width_field or field.height_field)
           for field in sender._meta.fields):
        signals.pre_save.connect(_resize_source_images, sender=sender, weak=False)


signals.class_prepared.connect(_connect_resize_source_images, weak=False)
