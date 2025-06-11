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

Animated GIF
============

Thumbnailing animated GIFs requires extra processing. To avoid this, you can enable the
`RGB_ALWAYS` loading strategy for the GifImagePlugin by adding this to your project:

.. code-block:: python

    from PIL import GifImagePlugin
    GifImagePlugin.LOADING_STRATEGY = GifImagePlugin.LoadingStrategy.RGB_ALWAYS

This setting is an optional optimization because it changes how all GIFs are loaded by
Pillow, not just animated GIFs. The `Pillow GIF docs
<https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif/>`_
explain how this settings works and you can decide if it's the right choice for
your project.

Remark
======

In the future, Easy Thumbnails might preserve animated images by default, and/or provide the
option to enable/disable animations for each generated thumbnail.
