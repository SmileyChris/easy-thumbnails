Changes
=======

HEAD
----

* Better support for multiple source generators.

* Update method used to check for modification dates of source and thumbnail
  images. Thanks Ben Roberts.

* Better thumbnail_high_resolution handling.

* Added configuration option to specify the infix used for high resolution image
  handling.

1.4
---

* Considerable speed up for remote storages by reducing queries.
  Brent O'Connor spent a lot of time debugging this, so thank you epicserve!

* Allow the ``{% thumbnail %}`` tag to also accept aliases. Thanks Simon Meers!

* Make ``replace_alpha`` actually work correctly.

* Fixes exception being raised when image exists in cache but is doesn't
  actually exist in the storage.

* Fixes Python 2.5 compatibility.

1.3
---

* Some more Django 1.5 fixes.

* Fix an issue with ``Thumbnail.url`` not working correctly.

* Add the ability to generate retina quality thumbnails in addition to the
  standard ones (off by default).

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
