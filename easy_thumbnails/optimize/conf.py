# -*- coding: utf-8 -*-
from easy_thumbnails.conf import Settings


class OptimizeSettings(Settings):
    THUMBNAIL_OPTIMIZE_COMMAND = {'png': None, 'jpeg': None, 'gif': None}
    """
    Postprocess thumbnails of type PNG, GIF or JEPG after transformation but
    before storage.

    Apply an external post processing program to images after they have been
    manipulated by PIL or Pillow. This is strongly recommended by tools such as
    Google's PageSpeed on order to reduce the payload of the thumbnailed image
    files.

    Example::

      THUMBNAIL_OPTIMIZE_COMMAND = {
          'png': '/usr/bin/optipng {filename}',
          'gif': '/usr/bin/optipng {filename}',
          'jpeg': '/usr/bin/jpegoptim {filename}'
      }

    Note that ``optipng`` can also optimize images of type GIF.
    """

settings = OptimizeSettings()
