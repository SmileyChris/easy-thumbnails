from easy_thumbnails.processors import scale_and_crop
from PIL import Image


im = Image.open('/home/chris/Pictures/luke-small.jpg')

scale_and_crop(im, (600, 600), crop="smart").show()




#target_width = 500
#dx = im.size[0] - target_width
#
#left, top = 0, 0
#right, bottom = im.size
#
#while dx:
#    slice = min(dx, max(dx / 5, 10))
#    print [left, top, right, bottom]
#    half = (right - left) // 2
#    print half
#    start = im.crop([left, top, left + slice, bottom])
#    end = im.crop([right - slice, top, right, bottom])
#    start_e = image_entropy(start)
#    end_e = image_entropy(end)
#    print start_e, end_e
#    if start_e >= end_e:
#        right -= slice
#    else:
#        left += slice
#    dx -= slice
#
#im.crop([left, top, right, bottom]).show()