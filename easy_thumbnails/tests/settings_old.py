"""
Allow older versions of Django to use the same test discovery runner method.
"""
from .settings import *   # NOQA

TEST_RUNNER = 'discover_runner.DiscoverRunner'
