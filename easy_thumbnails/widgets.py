from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe
from django.utils.html import escape

class ImageClearableFileInput(ClearableFileInput):
    template_with_initial = u'%(clear_template)s<br />%(input_text)s: %(input)s'

    def img_id(self, name):
        return name + "_img_id"

    def render(self, name, value, attrs=None):
        html = super(ImageClearableFileInput, self).render(name, value, attrs)
        img = u'<img id="%s" src="%s"/>' % (self.img_id(name), escape(value.url))
        html = img + html
        return mark_safe(html)
