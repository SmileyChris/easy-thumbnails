============
Installation
============

Before installing easy-thumbnails, you'll obviously need to have copy of
Django installed. For the |version| release, both Django 1.4 and Django 1.7 or
above is supported.

By default, all of the image manipulation is handled by the
`Python Imaging Library`__ (a.k.a. PIL), so you'll probably want that
installed too.

.. __: http://www.pythonware.com/products/pil/


Installing easy-thumbnails
==========================

The easiest way is to use an automatic package-installation tools like pip__.

.. __: http://pip.openplans.org/

Simply type::

    pip install easy-thumbnails

Manual installation
-------------------

If you prefer not to use an automated package installer, you can
download a copy of easy-thumbnails and install it manually. The
latest release package can be downloaded from `easy-thumbnail's
listing on the Python Package Index`__.

.. __: http://pypi.python.org/pypi/easy-thumbnails/

Once you've downloaded the package, unpack it and run the ``setup.py``
installation script::

    python setup.py install


Configuring your project
========================

In your Django project's settings module, add easy-thumbnails to your
``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        ...
        'easy_thumbnails',
    )

If you are using Django 1.7 or later, run ``python manage.py migrate easy_thumbnails``.
Otherwise, just run ``python manage.py syncdb``.

You're done! You'll want to head on over now to the
:doc:`usage documentation <usage>`.


Using with Django South
=======================

Django South migrations are stored in the ``south_migrations`` sub-package.

In order to use South with easy_thumbnails, you will need to customize the
``SOUTH_MIGRATION_MODULES`` setting:

.. code-block:: python

    SOUTH_MIGRATION_MODULES = {
        'easy_thumbnails': 'easy_thumbnails.south_migrations',
    }
