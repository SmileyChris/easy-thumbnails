# For these tests to run successfully, two conditions must be met:
# 1. MEDIA_URL and MEDIA_ROOT must be set in settings
# 2. The user running the tests must have read/write access to MEDIA_ROOT

# Unit tests:
from easy_thumbnails.tests.classes import ThumbnailTest, DjangoThumbnailTest
from easy_thumbnails.tests.templatetags import ThumbnailTagTest
from easy_thumbnails.tests.fields import FieldTest, \
    ImageWithThumbnailsFieldTest, ThumbnailFieldTest
# Doc tests:
from easy_thumbnails.tests.utils import utils_tests
from easy_thumbnails.tests.templatetags import filesize_tests
__test__ = {
    'utils_tests': utils_tests,
    'filesize_tests': filesize_tests,
}
