"""
This allows usage of `easy-thumbnails` in templates 
by {% load easy_thumbnails_tags %} instead of traditional
{% load thumbnail %}. It's specifically useful in projects
that do make use of multiple thumbnailer libraries (for
instance `easy-thumbnails` alongside `sorl-thumbnail`).
"""
from .thumbnail import *
