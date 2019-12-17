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

.. note:: Starting with version 2.8 there is no need anymore to add
	`easy_tumbnails.optimize` to `settings.INSTALLED_APPS`.


Installation and configuration
==============================

Install one or both of the above programs on your operating system.

Then add the full qualified path to the Python dict named ``THUMBNAIL_OPTIMIZE_COMMAND``.
For example:

.. code-block:: python

	THUMBNAIL_OPTIMIZE_COMMAND = {
	    'gif': '/usr/bin/optipng {filename}',
	    'jpeg': '/user/bin/jpegoptim {filename}',
	    'png': '/usr/bin/optipng {filename}'
	}

.. _jpegoptim: http://freecode.com/projects/jpegoptim
.. _optipng: http://optipng.sourceforge.net/
.. _PageSpeed: https://developers.google.com/speed/pagespeed/
