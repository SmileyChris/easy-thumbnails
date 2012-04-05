================
Image Processors
================

Easy thumbnails generates thumbnail images by passing the source image through
a series of image processors. Each processor may alter the image, often
dependent on the options it receives.

This makes the system very flexible, as the processors an image passes through
can be defined in :ref:`THUMBNAIL_PROCESSORS <setting-thumbnail_processors>`
and even overridden by an individual :class:`easy_thumbnails.files.Thumbnailer`
(via the :attr:`processors` attribute).

Built-in processors
===================

Following is a list of the built-in processors, along with the thumbnail
options which they use.

.. automodule:: easy_thumbnails.processors
   :members:


Custom processors
=================

You can replace or leave out any default processor as suits your needs.
Following is an explanation of how to create and activate a custom processor.

When defining the
:ref:`THUMBNAIL_PROCESSORS setting <setting-thumbnail_processors>`, remember
that this is the order through which the processors are run. The image received
by a processor is the output of the previous processor.

Create the processor
--------------------

First create a processor like this::

    def whizzbang_processor(image, bang=False, **kwargs):
    	"""
    	Whizz bang the source image.

    	"""
        if bang:
            image = whizz(image)
        return image

The first argument for a processor is the source image.

All other arguments are keyword arguments which relate to the list of options
received by the thumbnail generator (including ``size`` and ``quality``).
Ensure you list all arguments which could be used (giving them a default value
of ``False``), as the processors arguments are introspected to generate a list
of valid options.

You must also use ``**kwargs`` at the end of your argument list because all
options used to generate the thumbnail are passed to processors, not just the
ones defined.

Whether a processor actually modifies the image or not, they must always return
an image. 

Use the processor
-----------------

Next, add the processor to
:ref:`THUMBNAIL_PROCESSORS <setting-thumbnail_processors>` in your settings
module::

    from easy_thumbnails import defaults

    THUMBNAIL_PROCESSORS = defaults.PROCESSORS + (
        'wb_project.thumbnail_processors.whizzbang_processor',
    )
