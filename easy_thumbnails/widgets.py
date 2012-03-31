from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe
from easy_thumbnails.files import get_thumbnailer


class ImageClearableFileInput(ClearableFileInput):
    template_with_initial = u'%(clear_template)s<br />'\
        u'%(input_text)s: %(input)s'
    template_with_thumbnail = u'%(template)s<br />'\
        u'<a href="%(source_url)s" target="_blank">%(thumb)s</a>'

    def __init__(self, thumbnail_options=None, attrs=None):
        thumbnail_options = thumbnail_options or {}
        thumbnail_options = thumbnail_options.copy()
        if not 'size' in thumbnail_options:
            thumbnail_options['size'] = (80, 80)
        self.thumbnail_options = thumbnail_options.copy()
        super(ImageClearableFileInput, self).__init__(attrs)

    def thumbnail_id(self, name):
        return '%s_thumb_id' % name

    def get_thumbnail(self, value):
        thumbnailer = get_thumbnailer(value, value.name)
        thumbnailer.source_storage = value.storage
        if hasattr(value, 'thumbnail_storage'):
            thumbnailer.thumbnail_storage = value.thumbnail_storage
        return thumbnailer.get_thumbnail(self.thumbnail_options)

    def render(self, name, value, attrs=None):
        output = super(ImageClearableFileInput, self).render(name, value, attrs)
        if not value:
            return output
        thumb = self.get_thumbnail(value)
        substitution = {
            'template': output,
            'thumb': thumb.tag(id=self.thumbnail_id(name)),
            'source_url': value.storage.url(value.name),
        }
        return mark_safe(self.template_with_thumbnail % substitution)
