from PIL import Image, ImageChops, ImageDraw
from PIL.GifImagePlugin import GifImageFile
from easy_thumbnails import processors
from unittest import TestCase


class AnimatedGIFProcessorsTests(TestCase):

    demo_gif = 'easy_thumbnails/tests/files/demo.gif'

    def test_scale(self):
        with Image.open(self.demo_gif) as im:
            frames = im.n_frames
            print(frames)
            processed = processors.scale_and_crop(im, (100, 100))
            processed_frames = processed.n_frames
            self.assertEqual(frames, processed_frames)
            print(processed.size)
            self.assertEqual(processed.size, (100, 75))
