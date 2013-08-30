Changes
=======

next
---

* Added configuration directives THUMBNAIL_POSTPROCESS_PNG, THUMBNAIL_POSTPROCESS_GIF and
  THUMBNAIL_POSTPROCESS_JPEG. They can optionally be used to specify a filtering executable, such
  as 'optipng' or 'jpegoptim', which are available for reducing the payload of images. Using these
  optional filters can dramatically increase the loading time of webpages.

current
---

* Some more Django 1.5 fixes.

* Fix an issue with ``Thumbnail.url`` not working correctly.

* Add the ability to generate retina quality thumbnails in addition to the
  standard ones (off by default).

* Make ``replace_alpha`` actually work correctly.

1.2
---

* Django 1.5 compatibility.

* Fixed a problem with the ``ImageClearableFileInput`` widget.

1.1
---

* Added a way to avoid generating thumbnails if they don't exist already (with
  a signal to deal with them elsewhere).

* Added a ``thumbnailer_passive`` filter to allow templates to use the
  non-generating thumbnails functionality when dealing with aliases.

1.0.3
-----

* Changed the exception to catch from 1.0.2 to IOError.

1.0.2
-----

* Catch an OSError exception when trying to get the EXIF data of a touchy
  image.

1.0.1
-----

* Fix a Django 1.2 backwards incompatibility in ``easy_thumbnails.conf``

* Introduced a ``thumbnail_created`` signal.

1.0
---

* Introduction of aliased thumbnails.

* Start of sane versioning numbers.
