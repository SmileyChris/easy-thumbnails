=======================================
Optimizing Images using a Postprocessor
=======================================

The PIL and the Pillow libraries do a great job when is comes to crop, rotate
or resize images. However, they both operate poorly when it comes to optimizing
the payload of the generated files.

For this feature, two portable command line programs can fill the gap:
jpegoptim_ and optipng_. They both are open source, run on a huge range of
platforms, and can reduce the file size of an image by often more than 50%
without loss of quality.

Optimizing such images is a big benefit in terms of loading time and is
therefore strongly recommended by tools such as Google's PageSpeed_. Moreover,
if every website operator cares about, it reduces the overall Internet traffic
and thus greenhouse gases by some googolth percent.

Support for these postprocessors (or other similar ones) is available as an
optional feature in easy-thumbnails.


Installation and configuration
==============================

Install one or both of the above programs on your operating system.

In your Django project's settings module, add the optimizing postprocessor to
your configuration settings::

	INSTALLED_APP = (
	    ...
	    'easy_thumbnails',
	    'easy_thumbnails.optimize',
	    ...
	)

There is one configuration settings dictionary:

.. autoattribute::
   easy_thumbnails.optimize.conf.OptimizeSettings.THUMBNAIL_OPTIMIZE_COMMAND

.. _jpegoptim: http://freecode.com/projects/jpegoptim
.. _optipng: http://optipng.sourceforge.net/
.. _PageSpeed: https://developers.google.com/speed/pagespeed/
