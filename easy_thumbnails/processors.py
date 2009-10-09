from PIL import Image, ImageFilter, ImageChops
from easy_thumbnails import utils
import re


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
            box = [ex, ey, x - ex, y - ey]
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
                    slice = min(dx, 10)
                    l_sl = im.crop((0, 0, slice, y))
                    r_sl = im.crop((x - slice, 0, x, y))
                    if utils.image_entropy(l_sl) >= utils.image_entropy(r_sl):
                        right -= slice
                    else:
                        left += slice
                    dx -= slice
                while dy:
                    slice = min(dy, 10)
                    t_sl = im.crop((0, 0, x, slice))
                    b_sl = im.crop((0, y - slice, x, y))
                    if utils.image_entropy(t_sl) >= utils.image_entropy(b_sl):
                        bottom -= slice
                    else:
                        top += slice
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
