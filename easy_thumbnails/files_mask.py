from django.core.files.base import File, ContentFile
from easy_thumbnails import utils
import os
from django.utils.encoding import smart_str, smart_unicode

class MaskFile(File):
    """
    A mask file.
    """
    def __str__(self):
        filename, ext = os.path.splitext(os.path.basename(self.name))
        return smart_str(filename or '')

    def __unicode__(self):
        filename, ext = os.path.splitext(os.path.basename(self.name))
        return smart_unicode(filename or u'')

    def _get_image(self):
        if not hasattr(self, '_image_cache'):
            from easy_thumbnails.source_generators import pil_image
            self._image_cache = pil_image(self)
        return self._image_cache

    def _set_image(self, image):
        """
        Set the image for this file.
        """
        if image:
            self._image_cache = image
        else:
            if hasattr(self, '_image_cache'):
                del self._cached_image

    image = property(_get_image, _set_image)


def get_mask(mask_path):
    path = os.path.join(utils.get_setting('MEDIA_ROOT'), '_masks', mask_path+".png")
    try:
        file = open(path, 'rb')
    except IOError:
        return None
    mask = MaskFile(file)
    return mask
