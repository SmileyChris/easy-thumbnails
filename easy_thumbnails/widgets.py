from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe
from easy_thumbnails.files import get_thumbnailer

class ImageClearableFileInput(ClearableFileInput):
    template_with_initial = u'%(clear_template)s<br />%(input_text)s: %(input)s'

    def __init__(self, thumbnail_size=(80, 80), thumbnail_options={}, attrs=None):
        self.thumbnail_size = thumbnail_size
        self.thumbnail_options = thumbnail_options
        super(ImageClearableFileInput, self).__init__(attrs)

    def img_id(self, name):
        return name + "_img_id"

    def render(self, name, value, attrs=None):
        html = super(ImageClearableFileInput, self).render(name, value, attrs)
        opts = self.thumbnail_options.copy()
        opts['size'] = self.thumbnail_size
        img = get_thumbnailer(value).get_thumbnail(opts).tag(id=self.img_id(name))
        img = u'<a href="%s" target="_blank">%s</a>' % (value.url, img)
        html = img + html
        return mark_safe(html)
