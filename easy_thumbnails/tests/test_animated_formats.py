from io import BytesIO
from PIL import Image, ImageChops, ImageDraw
from PIL.GifImagePlugin import GifImageFile
from easy_thumbnails import processors
from unittest import TestCase


def create_animated_image(mode='RGB', format="gif", size=(500, 500)):
    frames = []
    for i in range(10):
        image = Image.new(mode, size, (255, 255, 255))
        draw = ImageDraw.Draw(image)
        x_bit, y_bit = size[0] // 10 * i, size[1] // 10 * i
        draw.rectangle((x_bit, y_bit * 2, x_bit * 7, y_bit * 3), 'red')
        draw.rectangle((x_bit * 2, y_bit, x_bit * 3, y_bit * 8), 'red')
        frames.append(image)
    write_to = BytesIO()
    frames[0].save(
        write_to, format=format, save_all=True, append_images=frames[1:]
    )
    return Image.open(write_to)


class AnimatedFormatProcessorsTests(TestCase):

    def test_scale(self):
        im = create_animated_image()
        frames_count = im.n_frames
        self.assertGreater(frames_count, 1)
        processed = processors.scale_and_crop(im, (100, 100))
        processed_frames_count = processed.n_frames
        self.assertEqual(frames_count, processed_frames_count)
        self.assertEqual(processed.size, (100, 100))

    def test_scale_crop(self):
        im = create_animated_image()
        frames_count = im.n_frames
        processed = processors.scale_and_crop(im, (100, 50), crop=True)
        processed_frames_count = processed.n_frames
        self.assertEqual(frames_count, processed_frames_count)
        self.assertEqual(processed.size, (100, 50))

    def test_colorspace(self):
        # to have a color conversion
        im = create_animated_image(format="png")
        frames_count = im.n_frames
        processed = processors.colorspace(im, bw=True)
        processed_frames_count = processed.n_frames
        # indeed processed?
        self.assertEqual(processed.mode, "L")
        self.assertEqual(frames_count, processed_frames_count)
        self.assertEqual(processed.size, (500, 500))

    def test_filter(self):
        # to have a color conversion
        im = create_animated_image(format="webp")
        frames_count = im.n_frames
        processed = processors.filters(im, detail=True, sharpen=True)
        processed_frames_count = processed.n_frames
        # indeed processed?
        self.assertEqual(frames_count, processed_frames_count)
        self.assertEqual(processed.size, (500, 500))

    def test_background(self):
        # to have a color conversion
        im = create_animated_image(format="webp")
        frames_count = im.n_frames
        processed = processors.background(im, background="#ff00ff", size=(500, 800))
        processed_frames_count = processed.n_frames
        # indeed processed?
        self.assertEqual(frames_count, processed_frames_count)
        self.assertEqual(processed.size, (500, 800))
