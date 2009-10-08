DEBUG = False

DEFAULT_STORAGE = 'easy_thumbnails.storage.ThumbnailFileSystemStorage'
MEDIA_ROOT = ''
MEDIA_URL = ''

BASEDIR = ''
SUBDIR = ''
PREFIX = ''

QUALITY = 85
EXTENSION = 'jpg'
PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'easy_thumbnails.processors.scale_and_crop',
    'easy_thumbnails.processors.filters',
)
IMAGEMAGICK_FILE_TYPES = ('eps', 'pdf', 'psd')
