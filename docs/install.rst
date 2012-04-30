============
Installation
============

Prerequisites
=============

Before installing easy-thumbnails, you'll obviously need to have copy of Django
installed. For the |version| release, Django 1.1+ is required.

By default, all of the image manipulation is handled by the
`Python Imaging Library`__ (a.k.a. PIL), so you'll  want that
installed too::

   $ pip install PIL
   
It appears project isolation from system is using `VirtualEnv`_ is becoming the 
emerging community pattern, you may wish to familiarize yourself with it and/or adopt it. 

.. __: http://www.pythonware.com/products/pil/
.. _VirtualEnv: http://pypi.python.org/pypi/virtualenv

Automatic Installation
======================

The easiest way is to use an automatic package-installation tools like pip_::

    $ pip install easy-thumbnails

.. _pip: http://pip.openplans.org/

Manual Installation
===================

If you prefer not to use an automated package installer, you can
download a copy of easy-thumbnails and install it manually. The
latest release package can be downloaded from `easy-thumbnail's
listing`_ on the Python Package Index.

Once you've downloaded the package, unpack it and run the ``setup.py``
installation script::

    $ python setup.py install

.. _easy-thumbnail's listing: http://pypi.python.org/pypi/easy-thumbnails/

Configuraiton
=============

Add the app to your project settings ``INSTALLED_APPS`` setting (and run ``manage.py syncdb``)::

   INSTALLED_APPS = (
        ...
        'easy_thumbnails',
   )

Customize available (see docs/ref/settings.rst) settings to tailor your specific project's ``settings.py``::

   THUMBNAIL_QUALITY = 85
   THUMBNAIL_SUBDIR = 'easy-thumbnails`
   THUBNAIL_ALIASES =  {
      '': {
            'small': {
               'size': (100, 100),
            },
            'banner': {
               'size': (600, 70),  
            },
       },
       'accounts.UserProfile': {
            'zoomed': {
               'size': (0, 720), 
               'quality': 100, 
               'detail': True, 
               'replace_alpha': '#fff', 
               'sharpen': True, 
               'bw': True,
               'crop': 'smart',
               'upscale': True,
           },
       },   
   }
   
Run `syncdb` command in the projects root directory to generate required tables::

   $ python manage.py syncdb
   