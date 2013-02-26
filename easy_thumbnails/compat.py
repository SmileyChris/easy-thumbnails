import sys

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,
else:
    string_types = basestring,


try:
    # Under Python 2.x cStringIO is much faster
    # than StringIO or io.BytesIO, so even though
    # io.BytesIO is available since Python 2.6,
    # we're trying cStringIO first.
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

try:
    from base64 import decodebytes as base64_decodebytes
except ImportError:
    from base64 import decodestring as base64_decodebytes


