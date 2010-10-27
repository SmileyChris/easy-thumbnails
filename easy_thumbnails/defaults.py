DEBUG = False

DEFAULT_STORAGE = 'easy_thumbnails.storage.ThumbnailFileSystemStorage'
MEDIA_ROOT = ''
MEDIA_URL = ''

BASEDIR = ''
SUBDIR = ''
PREFIX = ''

QUALITY = 85
EXTENSION = 'jpg'
TRANSPARENCY_EXTENSION = 'png'
PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'easy_thumbnails.processors.scale_and_crop',
    'easy_thumbnails.processors.filters',
)
SOURCE_GENERATORS = (
    'easy_thumbnails.source_generators.pil_image',
)
