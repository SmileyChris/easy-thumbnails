===============
easy-thumbnails
===============

The powerful, yet easy to implement thumbnailing application for Django. Below is a 'get you going' summary of usage,
For a complete documentations please see "full documentation":http://easy-thumbnails.readthedocs.org/en/latest/index.html
or the documentation *docs/* folder. 

Installation
============

To use this app in your application project install Python Imaging Library if it's not installed on system and 
then install the latest::

   $ pip install PIL
   $ pip install easy_thumbnails
   
Configuration
=============

Add the app to your project settings ``INSTALLED_APPS`` setting (and run ``manage.py syncdb``)::

   INSTALLED_APPS = (
        ...
        'easy_thumbnails',
   )

Specify global or per model predefined image alternatives through the ``THUMBNAIL_ALIASES`` settings like so::

   THUBNAIL_ALIASES =  {
      'small': {
         'size': (100, 100),
      }
      'banner': {
         'size': (600, 70),  
      }
      'zoomed': {
         'size': (0, 720), 
         'quality': 100, 
         'detail': True, 
         'replace_alpha': '#fff', 
         'sharpen' :True, 
         'bw': True,
         'crop': 'smart',
         'upscale' True,
      }
   }
   
Run `syncdb` command in the projects root directory to generate required tables::

   $ python manage.py syncdb
   

Template Usage
==============

Thumbnails (processed images) can be rendered in the template using the  ``{% thumbnail %}`` tag, the shortcut 
``{% thumbnail_url %}`` tag, the ``{% with photo=person.photo|thumbnailer %}`` filter, or directly by accessing the  
``Thumbnailer`` field on an instance {{ person.image.large }} where image is of type ``ThumbnailerImageField``. 
The latter three require that ``THUMBNAIL_ALIASES`` are specified to work as advertised. 

For a complete full documentation see ``docs/usage.rst``.

Tag {% thumbnail %} Usage
-------------------------

Add ``{% load thumbnail %}`` at the top of your template and use syntax ``{% thumbnail source size [options] [as var name] %}``::

   {% thumbnail person.photo 100x50 as person_photo %}
   <img alt={{person.about}} src={{person_photo.url}}>

Filter {% with photo=person.photo|thumbnailer %} Usage
------------------------------------------------------

The thumbnailer filter when applied to an image field returns a ``ThumbnailFile`` instance. The main purpose of this it
to access predefined ``THUBNAIL_ALIASES``::

   {% load thumbnailer %}
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

A shortcut tag that outputs the url for the specified thumbnail alias::

   {% load thumbnail_url %}
   <img href="{{ person.photo|thumbnail_url:'small' }}" alt="">


Thumbnailer field on a model instance
-------------------------------------

Models that utilize the ``ThumbnailerImageField`` field can have their image aliases accessed in the template like so::

   <img alt="{{person_instance.about}}" src="{{person_instance.photo.small.url}}">

Model usage
===========

You can use the ``ThumbnailerField`` or ``ThumbnailerImageField`` fields (based
on ``FileField`` and ``ImageField``, respectively) for easier access to
retrieve (or generate) thumbnail images.::

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

Further documentation
=====================

Please see ``docs/*`` for further documentation. 