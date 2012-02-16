===============
Easy Thumbnails
===============

The powerful, yet easy to implement thumbnailing application for Django.

To install this application into your project, just add it to your
``INSTALLED_APPS`` setting (and run ``manage.py syncdb``)::

    INSTALLED_APPS = (
        ...
        'easy_thumbnails',
    )


Template usage
==============

To generate thumbnails in your template, use the ``{% thumbnail %}`` tag. To
make this tag available for use in your template, use::
    
    {% load thumbnail %}

Basic tag Syntax::

    {% thumbnail [source] [size] [options] %}

*source* must be a ``File`` object, usually an Image/FileField of a model
instance.

*size* can either be:

* the size in the format ``[width]x[height]`` (for example,
  ``{% thumbnail person.photo 100x50 %}``) or

* a variable containing a valid size (i.e. either a string in the
  ``[width]x[height]`` format or a tuple containing two integers):
  ``{% thumbnail person.photo size_var %}``.

* you can resize and keep the original image ratio by specifying a
  0 width or 0 height (for example,
  ``{% thumbnail person.photo 100x0 %}`` will create a non-cropped 
  thumbnail which is 100 pixels wide)

*options* are a space separated list of options which are used when processing
the image to a thumbnail such as ``sharpen``, ``crop`` and ``quality=90``.


Model usage
===========

You can use the ``ThumbnailerField`` or ``ThumbnailerImageField`` fields (based
on ``FileField`` and ``ImageField``, respectively) for easier access to
retrieve (or generate) thumbnail images.

By passing a ``resize_source`` argument to the ``ThumbnailerImageField``, you
can resize the source image before it is saved::

    class Profile(models.Model):
        user = models.ForeignKey('auth.User')
        avatar = ThumbnailerImageField(
            upload_to='avatars',
            resize_source=dict(size=(50, 50), crop='smart'),
        )


Lower level usage
=================

Thumbnails are generated with a ``Thumbnailer`` instance. Usually you'll use
the ``get_thumbnailer`` method to generate one of these, for example::

    from easy_thumbnails.files import get_thumbnailer

    def square_thumbnail(source):
        thumbnail_options = dict(size=(100, 100), crop=True, bw=True)
        return get_thumbnailer(source).get_thumbnail(thumbnail_options)

See the docs directory for more comprehensive usage documentation.