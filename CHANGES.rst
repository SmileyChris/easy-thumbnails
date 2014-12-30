Changes
=======

2.2.1 (2014-12-30)
------------------

* Fixed: Option ``zoom`` can also be used by itself, without combining it with ``crop``.

2.2 (2014-10-04)
----------------

* Fix migrations for Django 1.7 final.

* Fix contain bad image EXIFs being able to still raise an exception.

2.1 (2014-08-13)
----------------

* Fix Python 3.4 installation issue.

* Avoid an OverflowError due to invalid EXIF data.

* Fix bug causing JPEG images to be saved without optimization :(

* JPEG files can now be saved with progressive encoding. By default, any image
  with a dimension larger than 100px will be saved progressively. Configured
  with the ``THUMBNAILER_PROGRESSIVE`` setting.

2.0.1 (2014-04-26)
------------------

* Fix packaging issue with old south migrations.

2.0 (2014-04-25)
----------------

* Use Django 1.7 migrations. Thanks Trey Hunner.
  **Note**: if using South, read the installation docs for required settings
  changes.

* Make ThumbnailerImageField.resize_source reflect change in extension.

* Add ``target`` option to the scale_and_crop processor, allowing for image
  focal points when cropping (or zooming) an image.

* Add a THUMBNAIL_NAMER option which takes a function used to customize
  the thumbnail filename.

* New ``subsampling`` option to reduce color subsampling of JPEG images,
  providing sharper color borders for a small increase in file size.

* Reimplementation of the ``thumbnail_cleanup`` command. Thanks Jørgen
  Abrahamsen

* More efficient thumbnail default storage. Thanks Sandip Agarwal.

1.5 (2014-03-05)
----------------

* Better support for multiple source generators.

* Update method used to check for modification dates of source and thumbnail
  images. Thanks Ben Roberts.

* Better thumbnail_high_resolution handling, including the ability to switch on
  and off explicitly with a ``HIGH_RESOLUTION`` thumbnail option.

* Added configuration option to specify the infix used for high resolution
  image handling.

* Optional postprocessor for image optimization. Thanks Jacob Rief!

* More remote storages optimization

* Thumbnail dimensions can now optionally be cached. Thanks David Novakovic.

* New ``zoom`` option to generate a thumbnail of a source image with a
  percentage clipped off each side.

* New ``background`` source processor that can add a border color to ensure
  scaled images fit within the exact dimensions given.

1.4 (2013-09-23)
----------------

* Considerable speed up for remote storages by reducing queries.
  Brent O'Connor spent a lot of time debugging this, so thank you epicserve!

* Allow the ``{% thumbnail %}`` tag to also accept aliases. Thanks Simon Meers!

* Make ``replace_alpha`` actually work correctly.

* Fixes exception being raised when image exists in cache but is doesn't
  actually exist in the storage.

* Fixes Python 2.5 compatibility.

1.3 (2013-06-17)
----------------

* Some more Django 1.5 fixes.

* Fix an issue with ``Thumbnail.url`` not working correctly.

* Add the ability to generate retina quality thumbnails in addition to the
  standard ones (off by default).

1.2 (2013-01-23)
----------------

* Django 1.5 compatibility.

* Fixed a problem with the ``ImageClearableFileInput`` widget.

1.1 (2012-08-29)
----------------

* Added a way to avoid generating thumbnails if they don't exist already (with
  a signal to deal with them elsewhere).

* Added a ``thumbnailer_passive`` filter to allow templates to use the
  non-generating thumbnails functionality when dealing with aliases.

1.0.3 (2012-05-30)
------------------

* Changed the exception to catch from 1.0.2 to IOError.

1.0.2 (2012-05-29)
------------------

* Catch an OSError exception when trying to get the EXIF data of a touchy
  image.

1.0.1 (2012-05-23)
------------------

* Fix a Django 1.2 backwards incompatibility in ``easy_thumbnails.conf``

* Introduced a ``thumbnail_created`` signal.

1.0 (2012-05-07)
----------------

* Introduction of aliased thumbnails.

* Start of sane versioning numbers.
