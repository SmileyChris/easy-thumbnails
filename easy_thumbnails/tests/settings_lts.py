"""
Allow LTS version of Django to use the same test discovery runner method.
"""
from .settings_old import *   # NOQA

TEST_RUNNER = 'discover_runner.DiscoverRunner'
