========
Settings
========

The following settings can be specified in your Django project's settings
module to alter the behaviour of easy-thumbnails.

THUMBNAIL_DEBUG
	Default: ``False``

	If this boolean setting is set to ``True``, display errors creating a
	thumbnail when using the :ref:`thumbnail_tag` rather than failing silently.

.. _setting-thumbnail_quality:

THUMBNAIL_QUALITY
	Default: ``85``

	The default quality level for JPG images on a scale from 1 (worst) to 95
	(best). Technically, values up to 100 are allowed, but this is not
	recommended.

THUMBNAIL_DEFAULT_STORAGE
	Default: ``'easy_thumbnails.storage.ThumbnailFileSystemStorage'``

	The default Django storage for thumbnails.

THUMBNAIL_MEDIA_ROOT
	Default: ``''``

	Used by easy-thumbnail's default storage to locate where thumbnails are
	stored on the file system.

	If not provided, Django's standard ``MEDIA_ROOT`` setting is used.

THUMBNAIL_MEDIA_URL
	Default: ``''``

	Used by easy-thumbnail's default storage to build the absolute URL for a
	generated thumbnail.

	If not provided, Django's standard ``MEDIA_URL`` setting is used.

THUMBNAIL_BASEDIR
	Default: ``''``

	Save thumbnail images to a directory directly off ``MEDIA_ROOT``, still
	keeping the relative directory structure of the source image.

	For example, using the ``{% thumbnail "photos/1.jpg" 150x150 %}`` tag with
	a ``THUMBNAIL_BASEDIR`` of ``'thumbs'`` would result in the following
	thumbnail filename::

		MEDIA_ROOT + 'thumbs/photos/1_jpg_150x150_q85.jpg'

THUMBNAIL_SUBDIR
	Default: ``''``

	Save thumbnail images to a sub-directory relative to the source image.

	For example, using the ``{% thumbnail "photos/1.jpg" 150x150 %}`` tag with
	a ``THUMBNAIL_SUBDIR`` of ``'thumbs'`` would result in the following
	thumbnail filename::

		MEDIA_ROOT + 'photos/thumbs/1_jpg_150x150_q85.jpg'

THUMBNAIL_PREFIX
	Default: ``''``

	Prepend thumbnail filenames with the specified prefix.

	For example, using the ``{% thumbnail "photos/1.jpg" 150x150 %}`` tag with
	a ``THUMBNAIL_PREFIX`` of ``'thumbs_'`` would result in the following
	thumbnail filename::

		MEDIA_ROOT + 'photos/thumbs_1_jpg_150x150_q85.jpg'

.. _setting-thumbnail_processors:

THUMBNAIL_PROCESSORS
	Default::

		(
		    'easy_thumbnails.processors.colorspace',
		    'easy_thumbnails.processors.autocrop',
		    'easy_thumbnails.processors.scale_and_crop',
		    'easy_thumbnails.processors.filters',
		)

	The :doc:`processors` through which the source image is run when you create
	a thumbnail.

	The order of the processors is the order in which they are sequentially
	called to process the image.

THUMBNAIL_SOURCE_GENERATORS
	Default::

		(
		    'easy_thumbnails.source_generators.pil_image',
		)

	The :doc:`source_generators` through which the base image is created from
	the source file.

	The order of the processors is the order in which they are sequentially
	tried.

.. _setting-thumbnail_extension:

THUMBNAIL_EXTENSION
	Default: ``'jpg'``

	The type of image to save thumbnails with no transparency layer as.

	Note that changing the extension will most likely cause the
	``THUMBNAIL_QUALITY`` setting to have no effect.

.. _setting-thumbnail_transparency_extension:

THUMBNAIL_TRANSPARENCY_EXTENSION
	Default: ``'png'``

	The type of image to save thumbnails with a transparency layer (e.g. GIFs
	or transparent PNGs).

.. _setting-thumbnail_preserve_extensions:

THUMBNAIL_PRESERVE_EXTENSIONS
	Default: ``None``

	To preserve specific extensions, for instance if you always want to create 
	lossless PNG thumbnails from PNG sources, you can specify these extensions 
	using this setting, for example::
		
		THUMBNAIL_PRESERVE_EXTENSIONS = ('png',)
		
	All extensions should be lowercase.

	Instead of a tuple, you can also set this to ``True`` in order to always 
	preserve the original extension.

THUMBNAIL_CHECK_CACHE_MISS
	Default: ``False``

	If this boolean setting is set to ``True``, and a thumbnail cannot
	be found in the database tables, we ask the storage if it has the
	thumbnail. If it does we add the row in the database, and we don't
	need to generate the thumbnail.

	Switch this to True if your easy_thumbnails_thumbnail table has been wiped
	but your storage still has the thumbnail files.

THUMBNAIL_DEFAULT_OPTIONS
	Default: ``None``

	Set this to a dictionary of options to provide as the default for all
	thumbnail calls. For example, to make all images greyscale::

		THUMBNAIL_DEFAULT_OPTIONS = {'bw': True}

.. _setting-thumbnail_aliases:

THUMBNAIL_ALIASES
	Default: ``None``

	A dictionary of predefined alias options for different targets. See the
	:ref:`usage documentation <thumbnail-aliases>` for details.
