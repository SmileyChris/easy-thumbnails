VERSION = (2, 8, 5, 'final', 0)


def get_version(*args, **kwargs):
    # Don't litter django/__init__.py with all the get_version stuff.
    # Only import if it's actually called.
    from .version_utils import get_version
    return get_version(*args, **kwargs)
