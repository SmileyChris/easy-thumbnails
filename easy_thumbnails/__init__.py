# Import the two most common objects so they are more easily accessible.
from files import Thumbnailer, ThumbnailFile

VERSION = (1, 0, 'alpha', 1)


def get_version(join=' '):
    """
    Return the version of this package as a string.

    The version number is built from a ``VERSION`` tuple, which should consist
    of integers, or trailing version information (such as 'alpha', 'beta' or
    'final'). For example:

    >>> VERSION = (2, 0, 6)
    >>> get_version()
    '2.0.6'

    >>> VERSION = (1, 0, 'beta', 2)
    >>> get_version()
    '1.0 beta 2'

    Use the ``join`` argument to join the version elements by an alternate
    character to the default ``' '``. This is useful when building a distutils
    setup module::

        from this_package import get_version

        setup(
            version=get_version(join='-'),
            # ...
        )

    """
    version = []
    for i, bit in enumerate(VERSION):
        if not isinstance(bit, int):
            break
    number = [str(bit) for bit in VERSION]
    number, remainder = number[:i], number[i:]
    if number:
        version.append('.'.join(number))
    if remainder == ['alpha', 0]:
        version.append('pre-alpha')
    elif 'final' not in remainder:
        version.extend(remainder)
    return join.join(version)
