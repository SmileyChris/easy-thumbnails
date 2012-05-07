============
Installation
============

Before installing easy-thumbnails, you'll obviously need to have copy of Django
installed. For the |version| release, Django 1.1 is required.

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

You may also want to set up some :doc:`easy-thumbnails related settings
<ref/settings>`.
