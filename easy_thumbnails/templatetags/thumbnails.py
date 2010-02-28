"""
Redundant module retained for backwards compatibility with early versions of
easy-thumbnail.

Previously, easy-thumbnails used ``{% load thumbnails %}`` rather than
``{% load thumbnail %}``

Using ``{% load thumbnail %}``  makes it easier now to drop this library in as
a direct replacement for sorl-thumbnail.

"""

from easy_thumbnails.templatetags.thumbnail import *
