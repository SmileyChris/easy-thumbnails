=====
Usage
=====

The common way easy-thumbnails is used is via the ``{% thumbnail %}`` template
tag or ``thumbnail_url`` filter, which generates
images from a model with an ``ImageField``.

Custom database fields are also available for simpler access.

The underlying Python code can be used for lower-level generation of thumbnail
images.

Overview
========

The primary function of easy-thumbnails is to dynamically create thumbnails
based on a source image.

So whenever a thumbnail does not exist or if the source was modified
more recently than the existing thumbnail, a new thumbnail is generated (and
saved).

Thumbnail aliases can be defined in the
:ref:`THUMBNAIL_ALIASES <setting-thumbnail_aliases>` setting, providing
predefined thumbnail options. This also allows for generation of thumbnails
when the source image is uploaded.

Thumbnail options
-----------------

To generate a thumbnail of a source image, you specify options which are
used by the image processors to generate the required image.

``size`` is a required option, and defines the bounds that the generated image
must fit within.

Other options are only provided if the given functionality is required:
   
- ``quality=<N>`` where N is an integer between 1 and 100 specifying output
  JPEG quality. The default is 85.
- ``autocrop`` removes any unnecessary whitespace from the edges of the source
  image.
- ``bw`` converts the image to grayscale.
- ``replace_alpha=#colorcode`` replaces any transparency layer with a solid
  color.
- ``crop=<smart|scale|W,H>`` cuts the edges of the image to match the aspect
  ratio of ``size`` before resizing. 

  - `smart` means the image is incrementally cropped down to the requested size
    by removing slices from edges with the least entropy. 
  - `scale` means at least one dimension fits within the size dimensions given.
  - `W,H` modifies the cropping origin behavior:

    - ``crop="0,0"`` will crop from the left and top edges.
    - ``crop="-10,-0"`` will crop from the right edge (with a 10% offset) and
      the bottom edge.
    - ``crop=",0"`` will keep the default behavior for the x axis (horizontally
      centering the image) and crop from the top edge.

For a complete and detailed list of options, see the :doc:`ref/processors`
reference documentation.


.. _thumbnail-aliases:

Thumbnail aliases
=================

An alias is a specific set of thumbnail options.

Using aliases gives you a single location to define all of your standard
thumbnail sizes/options, and avoids repetition of thumbnail options in your
code and templates.

An alias may be available project-wide, or set to target a specific app, model
or field.

The setting is defined like this::

    THUMBNAIL_ALIASES = {
        <target>: {
            <alias name>: <alias options dictionary>,
            ...
        },
        ...
    }

Use the target ``''`` for project-wide aliases.
Otherwise, the target should be a string which defines the scope of the
contained aliases:

    * ``'sprocket.Widget.image'`` would make the aliases available to only the
      'image' field of a 'Widget' model in an app named 'sprocket'.
    * ``'sprocket.Widget'`` would apply to any field in the 'Widget' model.
    * ``'sprocket'`` would target any field in any model in the app.


Pregeneration
-------------

Some provided signal handlers (along with a new ``saved_file`` signal) allow
for you to have the relevant aliases generated when a file is uploaded.

.. automodule:: easy_thumbnails.signal_handlers
    :members: generate_aliases, generate_aliases_global

In a module that will be executed when Django loads (such as a ``models.py``
file), register one of these signal handlers. For example::

    from easy_thumbnails.signals import saved_file
    from easy_thumbnails.signal_handlers import generate_aliases_global

    saved_file.connect(generate_aliases_global)


Asynchronous Pregeneration
--------------------------

For some use cases, it may not be necessary to have the relevant aliases
generated at the exact moment a file is uploaded. As an alternative, the
pregeneration task can be queued and executed by a background process.

The following example uses `django-celery 
<http://pypi.python.org/pypi/django-celery>`_ in conjunction with `Celery 
<http://celeryproject.org>`_ to achieve this.

models.py::

    from django.dispatch import receiver
    from easy_thumbnails.signals import saved_file
    from myapp import tasks
    
    @receiver(saved_file)
    def generate_thumbnails_async(sender, fieldfile, **kwargs):
        tasks.generate_thumbnails.delay(
            model=sender, pk=fieldfile.instance.pk,
            field=fieldfile.field.name)

tasks.py::

    from celery import task
    from easy_thumbnails.files import generate_all_aliases
    
    @task
    def generate_thumbnails(model, pk, field):
        instance = model._default_manager.get(pk=pk)
        fieldfile = getattr(instance, field)
        generate_all_aliases(fieldfile, include_global=True)

This results in a more responsive experience for the user, particularly
when dealing with large files and/or remote storage.


Setting aliases for your third-party app
----------------------------------------

If you have a distributable app that uses easy-thumbnails and want to provide
an alias, you can modify the aliases at runtime.

For example, put something like this in a module that will execute when Django
initializes (such as ``models.py``)::

    from easy_thumbnails.alias import aliases
    if not aliases.get('badge'):
        aliases.set('badge', {'size': (150, 80), 'crop': True})


Templates
=========

To make the easy-thumbnail template library available for use in your template,
use::
    
    {% load thumbnail %}


.. _thumbnail_url_filter:

``thumbnail_url`` filter
------------------------

.. autofunction:: easy_thumbnails.templatetags.thumbnail.thumbnail_url


.. _thumbnail_tag:

``{% thumbnail %}`` tag
-----------------------

If you want to create a thumbnail *without* providing an alias, use this tag to
generate the thumbnail by specifying all of the required options.

.. autofunction:: easy_thumbnails.templatetags.thumbnail.thumbnail

For a full list of options, read the :doc:`ref/processors` reference
documentation.

Fallback images
---------------

If you need to support fallback or default images at template level you can
use::
    
    {% thumbnail object.image|default:'img/default_image.png' 50x50 %}

Where the image string is relative to your default storage (usually the
``MEDIA_ROOT`` setting).


.. _thumbnailer_filters:

``thumbnailer`` filters
-----------------------

There are two filters that you can use if you want to get direct access to a
thumbnailer in your template. This can be useful when dealing with aliased
thumbnails.

.. autofunction:: easy_thumbnails.templatetags.thumbnail.thumbnailer

.. autofunction:: easy_thumbnails.templatetags.thumbnail.thumbnailer_passive


Models
======

You can use the ``ThumbnailerField`` or ``ThumbnailerImageField`` fields (based
on ``FileField`` and ``ImageField``, respectively) for easier access to
retrieve (or generate) thumbnail images, use different storages and resize
source images before saving.

.. autoclass:: easy_thumbnails.fields.ThumbnailerField

.. autoclass:: easy_thumbnails.fields.ThumbnailerImageField


Python
======

.. currentmodule:: easy_thumbnails.files

Easy thumbnails uses a Django ``File``-like object called a
:class:`Thumbnailer` to generate thumbnail images from the source file which
it references.

``get_thumbnailer``
-------------------

The easy way to create a :class:`Thumbnailer` instance is to use the following
utility function:

.. autofunction:: get_thumbnailer
   :noindex:

Once you have an instance, you can use the :meth:`Thumbnailer.get_thumbnail`
method to retrieve a thumbnail, which will (by default) generate it if it
doesn't exist (or if the source image has been modified since it was created).

For example, assuming an ``aardvark.jpg`` image exists in the default storage::

    from easy_thumbnails.files import get_thumbnailer
    
    thumbnailer = get_thumbnailer('animals/aardvark.jpg')
    
    thumbnail_options = {'crop': True} 
    for size in (50, 100, 250):
        thumbnail_options.update({'size': (size, size)})
        thumbnailer.get_thumbnail(thumbnail_options)

Non-Django file objects
-----------------------

If you need to process a standard file-like object, use :func:`get_thumbnailer`
and provide a ``relative_name`` like this::

	picture = open('/home/zookeeper/pictures/my_anteater.jpg')
	thumbnailer = get_thumbnailer(picture, relative_name='animals/anteater.jpg')
	thumb = thumbnailer.get_thumbnail({'size': (100, 100)})

If you don't even need to save the thumbnail to storage because you are
planning on using it in some more direct way, you can use the
:meth:`Thumbnailer.generate_thumbnail` method. 

Thumbnails generated in this manor don't use any cache reference, i.e. every
call to :meth:`Thumbnailer.get_thumbnail` will generate a fresh thumbnail
image.
