=======================
Animated images support
=======================

Support for animated image formats in easy-thumbnails is experimental and must be activated
manually, via `SETTINGS`.

Example settings, that will preserve GIF, WEBP and PNG formats, but wont allow animations on
PNGs.

.. code-block:: python

    THUMBNAIL_IMAGE_SAVE_OPTIONS = {
        "GIF": {"save_all": True},  # to save all frames available
        "WEBP": {"save_all": True},
        "PNG": {"save_all": False},  # dont allow animated PNGs
    }
    THUMBNAIL_PRESERVE_EXTENSIONS = ("webp", "gif", "png")


There have been issues with conversion from GIF to WEBP, so it's currently not recommended to
enable this specific conversion for animated images.


Remark
======

In the future, Easy Thumbnails might preserve animated images by default, and/or provide the
option to enable/disable animations for each generated thumbnail.