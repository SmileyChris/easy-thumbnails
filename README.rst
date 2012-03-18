===============
Easy Thumbnails
===============

The powerful, yet easy to implement thumbnailing application for Django. Below is a quick summary of usage,
For a complete documenations please see "full documenation":http://easy-thumbnails.readthedocs.org/en/latest/index.html
or the documenation *docs/* folder. 

To install this application into your project, just add it to your
``INSTALLED_APPS`` setting (and run ``manage.py syncdb``)::

    INSTALLED_APPS = (
        ...
        'easy_thumbnails',
    )


Template usage
==============

There are two ways to generate thumbnails in a template. One is to use the template {% thumbnail %} tag the other is 
to use image 'alternatives'  that you define on the image field itself, {{ foo_instance.image.large }}.

Image Alternatives
------------------
To take advantage of dynamic image alternatives generation use ``ThumbnailerImageField`` for your model image fields and specify
the settings like in a similiar fassion as below::

   image = ThumbnailerImageField(
        upload_to=get_upload_path, 
        # reduce the original only if needed keeping aspect ratio and  highest quality
        'process_source': dict(size=(0, 1080), quality=100),
        # we use alternatives instead of original so that thumbnail/image settings 
        # such us JPEG quiality can be quickly adjusted for the whole site
        alternatives = {
            'thumbnail_small': dict(size=(100, 100), autocrop=True, crop='smart', detail=True, upscale=True), 
            'thumbnail_medium': dict(size=(160, 160), autocrop=True, crop='smart', detail=True, upscale=True), 
            'thumbnail_large': dict(size=(220,220), autocrop=True, crop='smart', detail=True, upscale=True),
            'small': dict(size=(0, 480), crop=True, upscale=True),
            'medium': dict(size=(0, 600), crop=True, upscale=True),
            'large': dict(size=(0, 720), crop=True, upscale=True),
            'all_settings_sample': dict(size=(0, 720), quality=100, autocrop=True, bw=True, crop=True, detail=True, replace_alpha='#fff', sharpen=True, upscale=True),
        }
    )
    
Then in your template you can reffer to the specified altenratives as so::

   <a href='{{productimage.image.large.url}}'>
   <img class='product media thumbnail medium' alt='{{productimage.image.name}} - {{productimage.image.description}}' 
        src='{{productimage.image.thumbnail_medium.url}}' >
   </a>


Tempplate Tag Usage
-------------------

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

You can use the ``ThumbnailerField`` or ``EasyImageField`` fields (based
on ``FileField`` and ``ImageField``, respectively) for easier access to
retrieve (or generate) thumbnail images. 

By passing a ``process_source`` and ``alternatives`` arguments to the ``ThumbnailerImageField``, you
can resize the source image on save and provide quick image alternatives in your python code or templates::

   from easy_thumbnails.fields import ThumbnailerImageField
   class Profile(models.Model):
      user = models.ForeignKey('auth.User')
      avatar = EasyImageField(
         upload_to='avatars',
         process_source=dict(size=(0, 720), quality=95, autocrop=True, bw=False, crop=True, detail=False, replace_alpha=False, sharpen=False, upscale=True),
         alternatives = {
            'small': dict(size=(100, 134), autocrop=True, crop=True, upscale=True), 
            'medium': dict(size=(160, 214), autocrop=True, crop=True, upscale=True), 
            'large': dict(size=(220, 294), autocrop=True, crop=True, upscale=True), 
        }
    )

Then you can utilize you alternatives in your python code like so::
    
   >>> Profile.objects.all()[0].avatar.large
   <ThumbnailFile: accounts/profile/image-4.jpg.220x294_q85_autocrop_crop_upscale.jpg>
   >>> ProductCategory.objects.all()[0].get_image().image.small
   <ThumbnailFile: accounts/profile/image-4.jpg.100x134_q85_autocrop_crop_upscale.jpg>
   

Lower level usage
=================

Thumbnails are generated with a ``Thumbnailer`` instance. Usually you'll use
the ``get_thumbnailer`` method to generate one of these, for example::

    from easy_thumbnails.files import get_thumbnailer

    def square_thumbnail(source):
        thumbnail_options = dict(size=(100, 100), crop=True, bw=True)
        return get_thumbnailer(source).get_thumbnail(thumbnail_options)

See the docs directory for more comprehensive usage documentation.

Image Processors
================

For a list of avaiable processing options and how to specify custom image processors please see the :doc:`ref/processors` reference
documentation.