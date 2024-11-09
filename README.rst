===============
Easy Thumbnails
===============

.. image:: https://img.shields.io/pypi/v/easy-thumbnails.svg
    :target: https://pypi.python.org/pypi/easy-thumbnails/

.. image:: https://github.com/SmileyChris/easy-thumbnails/actions/workflows/python.yml/badge.svg
    :alt: Build Status
    :target: https://github.com/SmileyChris/easy-thumbnails/actions/workflows/python.yml


A powerful, yet easy to implement thumbnailing application for Django 4.2+

Below is a quick summary of usage. For more comprehensive information, view the
`full documentation`__ online or the peruse the project's ``docs`` directory.

__ http://easy-thumbnails.readthedocs.org/en/latest/index.html


Breaking News
=============

Version 2.8.0 adds support for thumbnailing SVG images when installed with the ``[svg]`` extra.

Of course it doesn't make sense to thumbnail SVG images, because being in vector format they can
scale to any size without quality of loss. However, users of easy-thumbnails may want to upload and
use SVG images just as if they would be PNG, GIF or JPEG. They don't necessarily care about the
format and definitely don't want to convert them to a pixel based format. What they want is to reuse
their templates with the templatetag thumbnail and scale and crop the images to whatever their
`<img src="..." width="..." height="...">` has been prepared for.

This is done by adding an emulation layer named VIL, which aims to be compatible with the
`PIL <https://python-pillow.org/>`_ library. All thumbnailing operations, such as scaling and
cropping behave like pixel based images. The final filesize of such thumbnailed SVG images doesn't
of course change, but their width/height and bounding box may be adjusted to reflect the desired
size of the thumbnailed image.

.. note:: This feature is new and experimental, hence feedback about its proper functioning in
          third parts applications is highly appreciated.


Installation
============

Run ``pip install easy-thumbnails``.

Add ``easy_thumbnails`` to your ``INSTALLED_APPS`` setting:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'easy_thumbnails',
    )

Run ``manage.py migrate easy_thumbnails``.


Example usage
=============

Thumbnail options can be predefined in ``settings.THUMBNAIL_ALIASES`` or just
specified in the template or Python code when run.

Using a predefined alias
------------------------

Given the following setting:

.. code-block:: python

    THUMBNAIL_ALIASES = {
        '': {
            'avatar': {'size': (50, 50), 'crop': True},
        },
    }

Template:

.. code-block:: html+django

    {% load thumbnail %}
    <img src="{{ profile.photo|thumbnail_url:'avatar' }}" alt="" />

Python:

.. code-block:: python

    from easy_thumbnails.files import get_thumbnailer
    thumb_url = get_thumbnailer(profile.photo)['avatar'].url

Manually specifying size / options
----------------------------------

Template:

.. code-block:: html+django

    {% load thumbnail %}
    <img src="{% thumbnail profile.photo 50x50 crop %}" alt="" />

Python:

.. code-block:: python

    from easy_thumbnails.files import get_thumbnailer
    options = {'size': (100, 100), 'crop': True}
    thumb_url = get_thumbnailer(profile.photo).get_thumbnail(options).url

Using in combination with other thumbnailers
--------------------------------------------

Alternatively, you load the templatetags by {% load easy_thumbnails_tags %} 
instead of traditional {% load thumbnail %}. It's especially useful in 
projects that do make use of multiple thumbnailer libraries that use the 
same name (`thumbnail`) for the templatetag module:

.. code-block:: html+django

    {% load easy_thumbnails_tags %}
    <img src="{% thumbnail profile.photo 50x50 crop %}" alt="" />

Fields
======

You can use ``ThumbnailerImageField`` (or ``ThumbnailerField``) for easier
access to retrieve or generate thumbnail images.

For example:

.. code-block:: python

    from easy_thumbnails.fields import ThumbnailerImageField

    class Profile(models.Model):
        user = models.OneToOneField('auth.User')
        photo = ThumbnailerImageField(upload_to='photos', blank=True)

Accessing the field's predefined alias in a template:

.. code-block:: html+django

    {% load thumbnail %}
    <img src="{{ profile.photo.avatar.url }}" alt="" />

Accessing the field's predefined alias in Python code:

.. code-block:: python

    thumb_url = profile.photo['avatar'].url


Thumbnail options
=================

``crop``
--------

Before scaling the image down to fit within the ``size`` bounds, it first cuts
the edges of the image to match the requested aspect ratio.

Use ``crop="smart"`` to try to keep the most interesting part of the image,

Use ``crop="0,10"`` to crop from the left edge and a 10% offset from the
top edge. Crop from a single edge by leaving dimension empty (e.g.
``crop=",0"``). Offset from the right / bottom by using negative numbers
(e.g., crop="-0,-10").

Often used with the ``upscale`` option, which will allow enlarging of the image
during scaling.

``quality=XX``
--------------

Changes the quality of the output JPEG thumbnail. Defaults to ``85``.

In Python code, this is given as a separate option to the ``get_thumbnail``
method rather than just alter the other.

``keep_icc_profile``
--------------------

If `True`, when saving a thumbnail with the alias that defines this option, the
ICC profile of the image will be preserved in the thumbnail, if present in the first place.


Other options
-------------

Valid thumbnail options are determined by the "thumbnail processors" installed.

See the `reference documentation`__ for a complete list of options provided by
the default thumbnail processors.

__ http://easy-thumbnails.readthedocs.org/en/latest/ref/processors/
