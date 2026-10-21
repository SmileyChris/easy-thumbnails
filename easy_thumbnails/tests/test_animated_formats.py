from io import BytesIO
from PIL import Image, ImageChops, ImageDraw
from easy_thumbnails import processors
from unittest import TestCase
from unittest.mock import patch


def create_animated_image(mode='RGB', format="gif", size=(1000, 1000), no_frames=6, loop=None):
    frames = []
    for i in range(no_frames):
        image = Image.new(mode, size, (255, 255, 255))
        draw = ImageDraw.Draw(image)
        x_bit, y_bit = size[0] // 40 * i, size[1] // 40 * i
        draw.rectangle((x_bit, y_bit * 2, x_bit * 7, y_bit * 3), 'red')
        draw.rectangle((x_bit * 2, y_bit, x_bit * 3, y_bit * 8), 'yellow')
        frames.append(image)
    write_to = BytesIO()
    save_kwargs = {'format': format, 'save_all': True, 'append_images': frames[1:]}
    if loop is not None:
        save_kwargs['loop'] = loop
    frames[0].save(write_to, **save_kwargs)
    im = Image.open(write_to)
    # for debugging
    # with open(f"animated{no_frames}.{format}", "wb") as f:
    #     write_to.seek(0)
    #     f.write(write_to.read())
    return im


class AnimatedFormatProcessorsTests(TestCase):

    def test_scale(self):
        no_frames = 20
        im = create_animated_image(no_frames=no_frames)
        frames_count = im.n_frames
        self.assertEqual(frames_count, no_frames)
        processed = processors.scale_and_crop(im, (100, 100))
        processed_frames_count = processed.n_frames
        self.assertEqual(frames_count, processed_frames_count)
        self.assertEqual(processed.size, (100, 100))

    def test_scale_crop(self):
        frames = 9
        im = create_animated_image(no_frames=frames)
        frames_count = im.n_frames
        self.assertEqual(frames_count, frames)
        processed = processors.scale_and_crop(im, (900, 950), crop=True)
        processed_frames_count = processed.n_frames
        self.assertEqual(frames_count, processed_frames_count)
        self.assertEqual(processed.size, (900, 950))

    def test_colorspace(self):
        # to have a color conversion
        no_frames = 6
        im = create_animated_image(format="png")
        frames_count = im.n_frames
        self.assertEqual(frames_count, no_frames)
        processed = processors.colorspace(im, bw=True)
        processed_frames_count = processed.n_frames
        # indeed processed?
        self.assertEqual(frames_count, processed_frames_count)
        self.assertEqual(processed.mode, "L")
        self.assertEqual(processed.size, (1000, 1000))

    def test_filter(self):
        no_frames = 12
        im = create_animated_image(format="webp", no_frames=no_frames)
        frames_count = im.n_frames
        self.assertEqual(frames_count, no_frames)
        processed = processors.filters(im, detail=True, sharpen=True)
        processed_frames_count = processed.n_frames
        # indeed processed?
        self.assertEqual(frames_count, processed_frames_count)
        self.assertEqual(processed.size, (1000, 1000))

    def test_background(self):
        no_frames = 9
        im = create_animated_image(format="webp", no_frames=no_frames)
        frames_count = im.n_frames
        self.assertEqual(frames_count, no_frames)
        processed = processors.background(im, background="#ff00ff", size=(1000, 1800))
        processed_frames_count = processed.n_frames
        # indeed processed?
        self.assertEqual(frames_count, processed_frames_count)
        self.assertEqual(processed.size, (1000, 1800))

    def test_background_loop_preserved(self):
        no_frames = 5
        loop_value = 3
        im = create_animated_image(format="gif", no_frames=no_frames, loop=loop_value)
        
        original_loop = im.info.get('loop', 0)
        self.assertEqual(original_loop, loop_value)
        
        processed = processors.background(im, background="#00ff00", size=(1200, 1200))
        
        processed_loop = processed.info.get('loop', 0)
        self.assertEqual(processed_loop, original_loop)
        self.assertEqual(processed_loop, loop_value)


class BrokenSecondaryFrameTests(TestCase):
    def create_mpo(self, broken_frame=1, corrupt_data=b''):
        frames = [Image.new('RGB', (40, 30), color) for color in ('red', 'blue', 'green')]
        output = BytesIO()
        frames[0].save(output, format='MPO', save_all=True, append_images=frames[1:])
        data = output.getvalue()
        # Preserve the MP index but remove the JPEG data for a secondary frame.
        offset = 0
        for _ in range(broken_frame):
            offset = data.index(b'\xff\xd8\xff', offset + 3)
        return Image.open(BytesIO(data[:offset] + corrupt_data))

    def test_scale_keeps_readable_primary_frame(self):
        image = self.create_mpo()
        self.assertEqual(image.n_frames, 3)
        image.load()
        expected = image.resize((10, 8))
        result = processors.scale_and_crop(image, (10, 10))
        result.load()
        self.assertEqual(result.size, expected.size)
        self.assertIsNone(ImageChops.difference(result, expected).getbbox())

    def test_scale_ignores_invalid_secondary_jpeg_header(self):
        image = self.create_mpo(corrupt_data=b'not a JPEG image')
        result = processors.scale_and_crop(image, (10, 10))
        result.load()
        self.assertEqual(result.size, (10, 8))
        self.assertGreater(result.getpixel((0, 0))[0], 200)

    def test_colorspace_keeps_readable_primary_frame(self):
        image = self.create_mpo()
        result = processors.colorspace(image, bw=True)
        result.load()
        self.assertEqual(result.size, (40, 30))
        self.assertEqual(result.mode, 'L')

    def test_keeps_all_readable_frames_before_broken_frame(self):
        image = self.create_mpo(broken_frame=2)
        result = processors.scale_and_crop(image, (10, 10))
        self.assertEqual(result.n_frames, 2)
        result.seek(1)
        result.load()
        self.assertEqual(result.size, (10, 8))
        self.assertGreater(result.getpixel((0, 0))[2], 200)

    def test_primary_frame_seek_error_propagates(self):
        image = self.create_mpo()
        with patch.object(image, 'seek', side_effect=ValueError('bad primary')):
            with self.assertRaisesRegex(ValueError, 'bad primary'):
                processors.scale_and_crop(image, (10, 10))

    def test_processing_error_propagates(self):
        image = self.create_mpo()
        with patch.object(image, 'resize', side_effect=ValueError('bad resize')):
            with self.assertRaisesRegex(ValueError, 'bad resize'):
                processors.scale_and_crop(image, (10, 10))
