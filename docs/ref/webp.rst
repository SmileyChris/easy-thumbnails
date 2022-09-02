================
Add WebP support
================

WebP is an image format employing both lossy and lossless compression. The format is a new open
standard for lossy compressed true-color graphics on the web, producing much smaller files of
comparable image quality to the older JPEG scheme.

This format is currently not supported by browsers in the same way as, for instance JPEG, PNG or
GIF. This means that it can not be used as a replacement inside an ``<img src="..." />`` tag.
A list of browsers supporting WebP can be found on caniuse_.

.. _caniuse: https://caniuse.com/#search=webp

Therefore, we can not use WebP as a drop-in replacement for JPEG or PNG, but instead must offer
the image alongside with one of our well-known formats. To achieve this, we use the Picture_
element such as:

.. _Picture: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/picture

.. code-block:: html

	<picture>
	  <source srcset="/path/to/image.webp" type="image/webp">
	  <img src="/path/to/image.jpg">
	</picture>

This means that we must continue to keep the thumbnailed images in either JPEG or PNG format.
Every time an image is thumbnailed, a corresponding image must be generated using the WebP
format. We can use this short function:

.. code-block:: python

	def store_as_webp(sender, **kwargs):
	    webp_path = sender.storage.path('.'.join([sender.name, 'webp']))
	    sender.image.save(webp_path, 'webp')

We then connect this funtion to the signal handler offerd by Easy-Thumbnails. A good place to
register that handler is the ``ready()`` method inside our AppConfig_:

.. _AppConfig: https://docs.djangoproject.com/en/stable/ref/applications/#django.apps.AppConfig

.. code-block:: python

	...

	def ready(self):
	    from easy_thumbnails.signals import thumbnail_created
	    thumbnail_created.connect(store_as_webp)

The last thing to do, is to rewrite the Django templates used to render image elements:

.. code-block:: django

	{% load thumbnail %}
	...
	<picture>
	  {% thumbnail image 400x300 as thumb %}
	  <source srcset="{{ thumb.url }}.webp" type="image/webp" />
	  <img src="{{ thumb.url }}" width="{{ thumb.width }}" height="{{ thumb.height }}" />
	</picture>


Remark
======

In the future, Easy Thumbnails might support WebP natively. This however means that it must
be usable as ``<img ...>`` -tag, supported by all browsers, and fully integrated into tools
such as django-filer_.

Until that happens, I recommend to proceed with the workarround described here.

.. _django-filer: https://django-filer.readthedocs.io/en/latest/
