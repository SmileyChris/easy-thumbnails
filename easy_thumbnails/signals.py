import django.dispatch

saved_file = django.dispatch.Signal(providing_args=['fieldfile'])
"""
A signal sent for each ``FileField`` saved when a model is saved.

* The ``sender`` argument will be the model class.
* The ``fieldfile`` argument will be the instance of the field's file that was
  saved.
"""
