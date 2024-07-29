Testing
=======

1. Install tox (``pip install tox``)
2. Run ``tox``

To test against other versions of Python, the recommended way is to ``pip
install tox-pyenv`` and install each version in pyenv that you want to test
against.

Run ``tox local <versions>`` to make them available when running tox.

pytest
------

Assuming you're just wanting to test the current development version against
your virtualenv setup, you can alternatively just ``pip install pytest-django testfixtures``
and run ``pytest``.
