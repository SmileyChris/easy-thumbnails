from io import BytesIO
from PIL import Image, ImageChops, ImageDraw
from easy_thumbnails import processors
from unittest import TestCase


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
