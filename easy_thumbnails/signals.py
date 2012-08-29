import django.dispatch

saved_file = django.dispatch.Signal(providing_args=['fieldfile'])
"""
A signal sent for each ``FileField`` saved when a model is saved.

* The ``sender`` argument will be the model class.
* The ``fieldfile`` argument will be the instance of the field's file that was
  saved.
"""

thumbnail_created = django.dispatch.Signal()
"""
A signal that gets sent every time a new thumbnail is created.

* The ``sender`` argument is the created ``ThumbnailFile``
"""

thumbnail_missed = django.dispatch.Signal(providing_args=['options'])
"""
A signal that gets sent whenever a thumbnail is passively requested (i.e. when
no render-time generation is wanted, via the ``generate=False`` argument).

* The ``sender`` argument is the ``Thumbnailer``
* The ``options`` are the thumbnail options requested.
"""
