from django import VERSION
from easy_thumbnails.tests.fields import ThumbnailerFieldTest
from easy_thumbnails.tests.files import FilesTest
from easy_thumbnails.tests.processors import ScaleAndCropTest, ColorspaceTest
from easy_thumbnails.tests.source_generators import PilImageTest
from easy_thumbnails.tests.templatetags import ThumbnailTagTest
from easy_thumbnails.tests.models import FileManagerTest

if VERSION[:2] >= (1, 3):
    from easy_thumbnails.tests.widgets import ImageClearableFileInput
