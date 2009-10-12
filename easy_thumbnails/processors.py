from PIL import Image, ImageFilter, ImageChops
from easy_thumbnails import utils
import re


def _compare_entropy(start_slice, end_slice, slice, difference):
    """
    Calculate the entropy of two slices (from the start and end of an axis),
    returning a tuple containing the amount that should be added to the start
    and removed from the end of the axis.
    
    """
    start_entropy = utils.image_entropy(start_slice)
    end_entropy = utils.image_entropy(end_slice)
    entropy_difference = abs(start_entropy / end_entropy - 1)
    if entropy_difference < 0.01:
        # Less than 1% difference, remove from both sides.
        if difference >= slice * 2:
            return slice, slice
        half_slice = slice // 2
        return half_slice, slice - half_slice
    if start_entropy > end_entropy:
        return 0, slice
    else:
        return slice, 0


def colorspace(im, bw=False, **kwargs):
    if bw and im.mode != 'L':
        im = im.convert('L')
    elif im.mode not in ('L', 'RGB', 'RGBA'):
        im = im.convert('RGB')
    return im


def autocrop(im, autocrop=False, **kwargs):
    if autocrop:
        bw = im.convert('1')
        bw = bw.filter(ImageFilter.MedianFilter)
        # White background.
        bg = Image.new('1', im.size, 255)
        diff = ImageChops.difference(bw, bg)
        bbox = diff.getbbox()
        if bbox:
            im = im.crop(bbox)
    return im


def scale_and_crop(im, size, crop=False, upscale=False, **kwargs):
    x, y = [float(v) for v in im.size]
    xr, yr = [float(v) for v in size]

    if crop:
        r = max(xr / x, yr / y)
    else:
        r = min(xr / x, yr / y)

    if r < 1.0 or (r > 1.0 and upscale):
        im = im.resize((int(x * r), int(y * r)), resample=Image.ANTIALIAS)

    if crop:
        # Difference (for x and y) between new image size and requested size.
        x, y = im.size
        dx, dy = int(x - min(x, xr)), int(y - min(y, yr))
        if dx or dy:
            # Center cropping (default).
            ex, ey = dx // 2, dy // 2
            box = [ex, ey, size[0] + ex, size[1] + ey]
            # See if an edge cropping argument was provided.
            edge_crop = (isinstance(crop, basestring) and
                         re.match(r'(?:(-?)(\d+))?,(?:(-?)(\d+))?$', crop))
            if edge_crop and filter(None, edge_crop.groups()):
                x_right, x_crop, y_bottom, y_crop = edge_crop.groups()
                if x_crop:
                    offset = min(x * int(x_crop) // 100, dx)
                    if x_right:
                        box[0] = dx - offset
                        box[2] = x - offset
                    else:
                        box[0] = offset
                        box[2] = x - (dx - offset)
                if y_crop:
                    offset = min(y * int(y_crop) // 100, dy)
                    if y_bottom:
                        box[1] = dy - offset
                        box[3] = y - offset
                    else:
                        box[1] = offset
                        box[3] = y - (dy - offset)
            # See if the image should be "smart cropped".
            elif crop == 'smart':
                left = top = 0
                right, bottom = x, y
                while dx:
                    slice = min(dx, max(dx // 5, 10))
                    start = im.crop((left, 0, left + slice, y))
                    end = im.crop((right - slice, 0, right, y))
                    add, remove = _compare_entropy(start, end, slice, dx)
                    left += add
                    right -= remove
                    dx -= slice
                while dy:
                    slice = min(dy, max(dy // 5, 10))
                    start = im.crop((0, top, x, top + slice))
                    end = im.crop((0, bottom - slice, x, bottom))
                    add, remove = _compare_entropy(start, end, slice, dy)
                    top += add
                    bottom -= remove
                    dy -= slice
                box = (left, top, right, bottom)
            # Finally, crop the image!
            im = im.crop(box)
    return im


def filters(im, detail=False, sharpen=False, **kwargs):
    if detail:
        im = im.filter(ImageFilter.DETAIL)
    if sharpen:
        im = im.filter(ImageFilter.SHARPEN)
    return im
