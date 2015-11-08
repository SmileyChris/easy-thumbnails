from django.test import TestCase

from easy_thumbnails import namers


class FakeThumbnailer(object):

    def __init__(self, basedir='', subdir=''):
        self.thumbnail_basedir = basedir
        self.thumbnail_subdir = subdir


class Default(TestCase):

    def test_basic(self):
        filename = namers.default(
            thumbnailer=FakeThumbnailer(),
            prepared_options=['100x100', 'q80', 'crop', 'upscale'],
            source_filename='source.jpg',
            thumbnail_extension='jpg',
        )
        self.assertEqual(filename, 'source.jpg.100x100_q80_crop_upscale.jpg')

    def test_subdir_opts(self):
        filename = namers.default(
            thumbnailer=FakeThumbnailer(subdir='%(opts)s'),
            prepared_options=['100x100', 'q80', 'crop', 'upscale'],
            source_filename='source.gif',
            thumbnail_extension='png',
        )
        self.assertEqual(filename, 'source.gif.png')

    def test_basedir_opts(self):
        filename = namers.default(
            thumbnailer=FakeThumbnailer(basedir='%(opts)s'),
            prepared_options=['100x100', 'q80', 'crop', 'upscale'],
            source_filename='source.gif',
            thumbnail_extension='png',
        )
        self.assertEqual(filename, 'source.gif.png')


class Hashed(TestCase):

    def test_basic(self):
        filename = namers.hashed(
            thumbnailer=FakeThumbnailer(),
            prepared_options=['100x100', 'q80', 'crop', 'upscale'],
            source_filename='source.jpg',
            thumbnail_extension='jpg',
        )
        self.assertEqual(filename, '6qW1buHgLaZ9.jpg')


class Alias(TestCase):

    def test_basic(self):
        filename = namers.alias(
            thumbnailer=FakeThumbnailer(),
            prepared_options=['100x100', 'q80', 'crop', 'upscale'],
            thumbnail_options={'size': (100, 100), 'ALIAS': 'medium_large'},
            source_filename='source.jpg',
            thumbnail_extension='jpg',
        )
        self.assertEqual(filename, 'source.jpg.medium_large.jpg')


class SourceHashed(TestCase):

    def test_basic(self):
        filename = namers.source_hashed(
            thumbnailer=FakeThumbnailer(),
            prepared_options=['100x100', 'q80', 'crop', 'upscale'],
            source_filename='source.jpg',
            thumbnail_extension='jpg',
        )
        self.assertEqual(filename, '1xedFtqllFo9_100x100_QHCa6G1l.jpg')
