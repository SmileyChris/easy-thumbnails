Changes
=======

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
