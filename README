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

Thumbnails are generated with a ``Thumbnailer`` instance. For example::

    from easy_thumbnails.files import get_thumbnailer

    def square_thumbnail(source):
        thumbnail_options = dict(size=(100, 100), crop=True, bw=True)
        return get_thumbnailer(source).get_thumbnail(thumbnail_options)

By default, ``get_thumbnail`` saves the file (using file storage). The source
file used to instanciate the ``Thumbnailer`` must be one of the following:

* ``Thumbnailer`` instance

* ``FieldFile`` instance (i.e. a model instance file/image field
  property)

* ``File`` or ``Storage`` instance, and for both of these cases the
  ``relative_name`` argument must also be provided

* A string, which will be used as the relative name (the source will be
  set to the default storage)


The ``ThumbnailFile`` object provided makes this easy::

	from easy_thumbnails import ThumbnailFile

	# For an existing file in storage:
	source = ThumbnailFile('animals/aarvark.jpg')
	square_thumbnail(source)
	
	# For a new file:
	picture = open('/home/zookeeper/pictures/my_anteater.jpg')
	source = ThumbnailFile('animals/anteater.jpg', file=picture)
	square_thumbnail(source)
