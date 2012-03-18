from django.db.models.fields.files import FileField, ImageField
from easy_thumbnails import files
import warnings
from django.core.exceptions import ImproperlyConfigured

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

        super(ThumbnailerField, self).__init__(*args, **kwargs)

    def south_field_triple(self):
        """
        Return a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.files.FileField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)


class EasyImageField(ThumbnailerField, ImageField):
    """
    An image field which provides easier access for retrieving (and generating)
    thumbnails or other defined image alternatives.

    To use a different file storage for iamge alternatives , provide the
    ``thumbnail_storage`` keyword argument.

    To process the original source image before saving, provide the
    ``process_source`` keyword argument, passing it a usual alternative option
    dictionary. For example::

        EasyImageField(..., process_source=dict(size=(100, 100), sharpen=True))
    """
    attr_class = files.ThumbnailerImageFieldFile

    def __init__(self, *args, **kwargs):
        # Arguments not explicitly defined so that the normal ImageField
        # positional arguments can be used.
        self.resize_source = kwargs.pop('resize_source', None)
        self.process_source = kwargs.pop('process_source', None)
        if self.resize_source and self.process_source:
            raise ImproperlyConfigured("You can not have both 'resize_source' and 'process_source' arguments specified.")
        elif not self.resize_source is None: #elif self.resize_source != None:
            warnings.warn("``resize_source`` option is being depreciated in favor of more generic ``process_source`` name.", DeprecationWarning)
            self.process_source = self.resize_source
            del self.resize_source
        self.alternatives = kwargs.pop('alternatives', None)
        super(EasyImageField, self).__init__(*args, **kwargs)


    def south_field_triple(self):
        """
        Return a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.files.ImageField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

class ThumbnailerImageField(EasyImageField):
    """
    Place holder to allow for backwards compatibility
    """
    def __init__(self, *args, **kwargs):
        warnings.warn("'ThumbnailerImageField' class is being depreciated in favor of more generic 'EasyImageField' name.", DeprecationWarning)
        super(ThumbnailerImageField, self).__init__(*args, **kwargs)
