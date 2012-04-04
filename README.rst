===============
Easy Thumbnails
===============

The powerful, yet easy to implement thumbnailing application for Django. Below is a 'get you going' summary of usage,
For a complete documentations please see "full documentation":http://easy-thumbnails.readthedocs.org/en/latest/index.html
or the documentation *docs/* folder. 


Quick Setup
===========

To use this app in your application project install the latest version by running::

   pip install git+git://github.com/SmileyChris/easy-thumbnails.git 

Add the app to your project settings ``INSTALLED_APPS`` setting (and run ``manage.py syncdb``)::

   INSTALLED_APPS = (
        ...
        'easy_thumbnails',
   )

Specify global or per model predefined image alternatives through the ``THUMBNAIL_ALIASES`` settings::

   THUBNAIL_ALIASES =  {'small': {'size': (100, 100)
                        'all_settings_sample': {
                           'size': (0, 720), 
                           'quality': 100, 
                           'autocrop': True, 
                           'bw': True,
                           'crop' True, 
                           detail=True, replace_alpha='#fff', sharpen=True, upscale=True),          }, 
                        'large': {'size': (400, 400)}}

Template usage
==============

Thumbnails (processed images) can be rendered in the template using the  ``{% thumbnail %}`` tag, the shortcut 
``{% thumbnail_url %}`` tag, the ``{% with photo=person.photo|thumbnailer %}`` filter, or directly by accessing the  
``Thumbnailer`` field on an instance {{ person.image.large }} where image is of type ``ThumbnailerImageField``. 
The latter three require that ``THUMBNAIL_ALIASES`` are specified to work as advertised. 

Tag {% thubmanil %} Usage
-------------------------

To generate thumbnails in your template using the ``{% thumbnail %}`` tag make it first available in your template::
    
    {% load thumbnail %}

Afterwards tag syntax is as follows::

    {% thumbnail source size [options] [as var name] %}

**source** must be a ``File`` object, either a django vanilla  ``ImageField`` or ``FileField``, or an easy thumbnails
``ThumbnailerImageField``/``ThumbnailerField``, or one derived and compatible from either of those. 

**size** parameter can either be:

- the size in the format ``[width]x[height]`` for example, ``{% thumbnail person.photo 100x50 %}``
- a variable containing a valid size, i.e. either a string in the ``[width]x[height]`` format or a 
  tuple containing two integers: ``{% thumbnail person.photo size_var %}``.
- you can resize and keep the original image ratio by specifying a 0 width or 0 height. For example,
  ``{% thumbnail person.photo 100x0 %}`` will create a non-cropped thumbnail which is 100 pixels wide.
- 0 can be specified for either the width or height, which resize the image but keep the aspect ration on that axis.
  Example `300x0` will resize the image to 300 pixels wide and keep the aspect ration for height. 

**options** are a space separated list of options which are used when processing the image during save operation. 
The order does matter and these can be any of the below:
   
- ``quality=[N]`` where N is a number between 1 and 100 specifying output JPG quality. If omitted the default is to 
  85 or as specified by your project's ``THUMBNAIL_QUALITY`` setting.
- ``autocrop=[False|True]`` default is False. Removes any unnecessary whitespace from the edges of the source image.
  This processor should be listed before crop so the whitespace is removed from the source image before it is resized.
- ``bw=[False|True]`` default is False. Converts image to grayscale. This processor should be listed before 
  `scale_and_crop` so palette is changed before the image is resized.
- ``replace_alpha=#colorcode`` default is leave unchanged, this processor replaces any transparency layer 
  with a solid color. For example, ``replace_alpha='#fff'`` would replace the transparency layer with  white. 
- ``crop=[False|smart|scale|W,H]`` default is False, cropping image method, used in conjunction with [size] setting. 
  - `smart` means the image is incrementally cropped down to the requested size by removing slices from edges 
     with the least entropy. 
  - `scale` means at least one dimension fits within the size dimensions given.
  - `N,W` setting modifies cropping origin behavior:
    - ``crop="0,0"`` will crop from the left and top edges.
    - ``crop="-10,-0"`` will crop from the right edge (with a 10% offset) and the bottom edge.
    - ``crop=",0"`` will keep the default behavior for the x axis (horizontally centering the image) 
      and crop from the top edge.
   
**as var_name** allows you to put back the generated ``Thumbnailer`` instance back into the template context under
specified ``var_name``. Example::
   
   {% thumbnail person.photo 100x50 as person_photo %}
   <img alt={{person.about}} src={{person_photo.url}}>

Filter {% with photo=person.photo|thumbnailer %} Usage
------------------------------------------------------

The thumbnailer filter when applied to an image field returns a ``Thumbnailer`` instance. The main purpose of this it
to access predefined ``THUBNAIL_ALIASES``. To use load the filter by including ``{% load thumbnailer %}`` at top of 
your template and use following syntax::

   {% with photo=person.photo|thumbnailer %}
      {% if photo %}
         <a href="{{ photo.large.url }}">
             {{ photo.square.tag }}
         </a>
      {% else %}
         <img href="{% static 'template/fallback.png' %}" alt="" />
      {% endif %}
   {% endwith %}

Tag {% thubmanil_url %} Usage
-----------------------------

A shortcut tag that outputs the url for the specified thumbnail alias, if the specified alias does not exist an empty
string is returned. Sample template usage::

   <img href="{{ person.photo|thumbnail_url:'small' }}" alt="">


Thumbnailer field on a model instance
-------------------------------------

Models that utilize the ``ThumbnailerImageField`` field can have their image alises accessed in the template like so::

   <img alt="{{person_instance.about}}" src="{{person_instance.photo.small.url}}">

Model usage
===========

You can use the ``ThumbnailerField`` or ``ThumbnailerImageField`` fields (based
on ``FileField`` and ``ImageField``, respectively) for easier access to
retrieve (or generate) thumbnail images.

By passing a ``resize_source`` argument to the ``ThumbnailerImageField``, you
can resize and pre-process the source image before it is saved::

   class Person(models.Model):
      user = models.ForeginKey(User)
      photo = ThumbnailerImageField(..., resize_source = {
               'size': (0, 720), 
               'quality': 100, 
               ...
               'upscale': True)
               }),        

Afterwards specified thumbnail aliases can be access like so in your python code::

   small_photo = person_instance.photo['small']
   avatar_photo = person_instance.photo['avatar']

Lower level usage
=================

Thumbnails are generated with a ``Thumbnailer`` instance. Usually you'll use
the ``get_thumbnailer`` method to generate one of these, for example::

   from easy_thumbnails.files import get_thumbnailer
   def square_thumbnail(source):
      thumbnail_options = dict(size=(100, 100), crop=True, bw=True)
      return get_thumbnailer(source).get_thumbnail(thumbnail_options)

Aliases are generated using the ``Alias`` instance. In most situations specifying ``THUMBNAIL_ALIASES`` is preferred
and sufficient. However one can also specify aliases at run runtime like so::

    from easy_thumbnails.alias import aliases
    aliases.set('new_alias', options={
               'size': (0, 720), 
               'quality': 100, 
               ...
               'upscale': True)
               }, 
               target='accounts.profile.photo')
               