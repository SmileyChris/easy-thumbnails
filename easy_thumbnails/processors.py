import itertools
import re

from django.utils import six
try:
    from PIL import Image, ImageChops, ImageFilter
except ImportError:
    import Image
    import ImageChops
    import ImageFilter

from easy_thumbnails import utils


def _compare_entropy(start_slice, end_slice, slice, difference):
    """
    Calculate the entropy of two slices (from the start and end of an axis),
    returning a tuple containing the amount that should be added to the start
    and removed from the end of the axis.

    """
    start_entropy = utils.image_entropy(start_slice)
    end_entropy = utils.image_entropy(end_slice)
    if end_entropy and abs(start_entropy / end_entropy - 1) < 0.01:
        # Less than 1% difference, remove from both sides.
        if difference >= slice * 2:
            return slice, slice
        half_slice = slice // 2
        return half_slice, slice - half_slice
    if start_entropy > end_entropy:
        return 0, slice
    else:
        return slice, 0


def _points_table():
    """
    Iterable to map a 16 bit grayscale image to 8 bits.
    """
    for i in range(256):
        for j in itertools.repeat(i, 256):
            yield j


def colorspace(im, bw=False, replace_alpha=False, **kwargs):
    """
    Convert images to the correct color space.

    A passive option (i.e. always processed) of this method is that all images
    (unless grayscale) are converted to RGB colorspace.

    This processor should be listed before :func:`scale_and_crop` so palette is
    changed before the image is resized.

    bw
        Make the thumbnail grayscale (not really just black & white).

    replace_alpha
        Replace any transparency layer with a solid color. For example,
        ``replace_alpha='#fff'`` would replace the transparency layer with
        white.

    """
    if im.mode == 'I':
        # PIL (and pillow) have can't convert 16 bit grayscale images to lower
        # modes, so manually convert them to an 8 bit grayscale.
        im = im.point(list(_points_table()), 'L')

    is_transparent = utils.is_transparent(im)
    is_grayscale = im.mode in ('L', 'LA')
    new_mode = im.mode
    if is_grayscale or bw:
        new_mode = 'L'
    else:
        new_mode = 'RGB'

    if is_transparent:
        if replace_alpha:
            if im.mode != 'RGBA':
                im = im.convert('RGBA')
            base = Image.new('RGBA', im.size, replace_alpha)
            base.paste(im, mask=im)
            im = base
        else:
            new_mode = new_mode + 'A'

    if im.mode != new_mode:
        im = im.convert(new_mode)

    return im


def autocrop(im, autocrop=False, **kwargs):
    """
    Remove any unnecessary whitespace from the edges of the source image.

    This processor should be listed before :func:`scale_and_crop` so the
    whitespace is removed from the source image before it is resized.

    autocrop
        Activates the autocrop method for this image.

    """
    if autocrop:
        # If transparent, flatten.
        if utils.is_transparent(im) and False:
            no_alpha = Image.new('L', im.size, (255))
            no_alpha.paste(im, mask=im.split()[-1])
        else:
            no_alpha = im.convert('L')
        # Convert to black and white image.
        bw = no_alpha.convert('L')
        # bw = bw.filter(ImageFilter.MedianFilter)
        # White background.
        bg = Image.new('L', im.size, 255)
        bbox = ImageChops.difference(bw, bg).getbbox()
        if bbox:
            im = im.crop(bbox)
    return im


def scale_and_crop(im, size, crop=False, upscale=False, zoom=None, target=None,
                   **kwargs):
    """
    Handle scaling and cropping the source image.

    Images can be scaled / cropped against a single dimension by using zero
    as the placeholder in the size. For example, ``size=(100, 0)`` will cause
    the image to be resized to 100 pixels wide, keeping the aspect ratio of
    the source image.

    crop
        Crop the source image height or width to exactly match the requested
        thumbnail size (the default is to proportionally resize the source
        image to fit within the requested thumbnail size).

        By default, the image is centered before being cropped. To crop from
        the edges, pass a comma separated string containing the ``x`` and ``y``
        percentage offsets (negative values go from the right/bottom). Some
        examples follow:

        * ``crop="0,0"`` will crop from the left and top edges.

        * ``crop="-10,-0"`` will crop from the right edge (with a 10% offset)
          and the bottom edge.

        * ``crop=",0"`` will keep the default behavior for the x axis
          (horizontally centering the image) and crop from the top edge.

        The image can also be "smart cropped" by using ``crop="smart"``. The
        image is incrementally cropped down to the requested size by removing
        slices from edges with the least entropy.

        Finally, you can use ``crop="scale"`` to simply scale the image so that
        at least one dimension fits within the size dimensions given (you may
        want to use the upscale option too).

    upscale
        Allow upscaling of the source image during scaling.

    zoom
        A percentage to zoom in on the scaled image. For example, a zoom of
        ``40`` will clip 20% off each side of the source image before
        thumbnailing.

    target
        Set the focal point as a percentage for the image if it needs to be
        cropped (defaults to ``(50, 50)``).

        For example, ``target="10,20"`` will set the focal point as 10% and 20%
        from the left and top of the image, respectively. If the image needs to
        be cropped, it will trim off the right and bottom edges until the focal
        point is centered.

        Can either be set as a two-item tuple such as ``(20, 30)`` or a comma
        separated string such as ``"20,10"``.

        A null value such as ``(20, None)`` or ``",60"`` will default to 50%.
    """
    source_x, source_y = [float(v) for v in im.size]
    target_x, target_y = [int(v) for v in size]

    if crop or not target_x or not target_y:
        scale = max(target_x / source_x, target_y / source_y)
    else:
        scale = min(target_x / source_x, target_y / source_y)

    # Handle one-dimensional targets.
    if not target_x:
        target_x = round(source_x * scale)
    elif not target_y:
        target_y = round(source_y * scale)

    if zoom:
        if not crop:
            target_x = round(source_x * scale)
            target_y = round(source_y * scale)
            crop = True
        scale *= (100 + int(zoom)) / 100.0

    if scale < 1.0 or (scale > 1.0 and upscale):
        # Resize the image to the target size boundary. Round the scaled
        # boundary sizes to avoid floating point errors.
        im = im.resize((int(round(source_x * scale)),
                        int(round(source_y * scale))),
                       resample=Image.ANTIALIAS)

    if crop:
        # Use integer values now.
        source_x, source_y = im.size
        # Difference between new image size and requested size.
        diff_x = int(source_x - min(source_x, target_x))
        diff_y = int(source_y - min(source_y, target_y))
        if crop != 'scale' and (diff_x or diff_y):
            if isinstance(target, six.string_types):
                target = re.match(r'(\d+)?,(\d+)?$', target)
                if target:
                    target = target.groups()
            if target:
                focal_point = [int(n) if (n or n == 0) else 50 for n in target]
            else:
                focal_point = 50, 50
            # Crop around the focal point
            halftarget_x, halftarget_y = int(target_x / 2), int(target_y / 2)
            focal_point_x = int(source_x * focal_point[0] / 100)
            focal_point_y = int(source_y * focal_point[1] / 100)
            box = [
                max(0, min(source_x - target_x, focal_point_x - halftarget_x)),
                max(0, min(source_y - target_y, focal_point_y - halftarget_y)),
            ]
            box.append(int(min(source_x, box[0] + target_x)))
            box.append(int(min(source_y, box[1] + target_y)))
            # See if an edge cropping argument was provided.
            edge_crop = (isinstance(crop, six.string_types) and
                         re.match(r'(?:(-?)(\d+))?,(?:(-?)(\d+))?$', crop))
            if edge_crop and filter(None, edge_crop.groups()):
                x_right, x_crop, y_bottom, y_crop = edge_crop.groups()
                if x_crop:
                    offset = min(int(target_x) * int(x_crop) // 100, diff_x)
                    if x_right:
                        box[0] = diff_x - offset
                        box[2] = source_x - offset
                    else:
                        box[0] = offset
                        box[2] = source_x - (diff_x - offset)
                if y_crop:
                    offset = min(int(target_y) * int(y_crop) // 100, diff_y)
                    if y_bottom:
                        box[1] = diff_y - offset
                        box[3] = source_y - offset
                    else:
                        box[1] = offset
                        box[3] = source_y - (diff_y - offset)
            # See if the image should be "smart cropped".
            elif crop == 'smart':
                left = top = 0
                right, bottom = source_x, source_y
                while diff_x:
                    slice = min(diff_x, max(diff_x // 5, 10))
                    start = im.crop((left, 0, left + slice, source_y))
                    end = im.crop((right - slice, 0, right, source_y))
                    add, remove = _compare_entropy(start, end, slice, diff_x)
                    left += add
                    right -= remove
                    diff_x = diff_x - add - remove
                while diff_y:
                    slice = min(diff_y, max(diff_y // 5, 10))
                    start = im.crop((0, top, source_x, top + slice))
                    end = im.crop((0, bottom - slice, source_x, bottom))
                    add, remove = _compare_entropy(start, end, slice, diff_y)
                    top += add
                    bottom -= remove
                    diff_y = diff_y - add - remove
                box = (left, top, right, bottom)
            # Finally, crop the image!
            im = im.crop(box)
    return im


def filters(im, detail=False, sharpen=False, **kwargs):
    """
    Pass the source image through post-processing filters.

    sharpen
        Sharpen the thumbnail image (using the PIL sharpen filter)

    detail
        Add detail to the image, like a mild *sharpen* (using the PIL
        ``detail`` filter).

    """
    if detail:
        im = im.filter(ImageFilter.DETAIL)
    if sharpen:
        im = im.filter(ImageFilter.SHARPEN)
    return im


def background(im, size, background=None, **kwargs):
    """
    Add borders of a certain color to make the resized image fit exactly within
    the dimensions given.

    background
        Background color to use
    """
    if not background:
        # Primary option not given, nothing to do.
        return im
    if not size[0] or not size[1]:
        # One of the dimensions aren't specified, can't do anything.
        return im
    x, y = im.size
    if x >= size[0] and y >= size[1]:
        # The image is already equal to (or larger than) the expected size, so
        # there's nothing to do.
        return im
    im = colorspace(im, replace_alpha=background, **kwargs)
    new_im = Image.new('RGB', size, background)
    if new_im.mode != im.mode:
        new_im = new_im.convert(im.mode)
    offset = (size[0]-x)//2, (size[1]-y)//2
    new_im.paste(im, offset)
    return new_im
