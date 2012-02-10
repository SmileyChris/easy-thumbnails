from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe
#from django.utils.html import escape
from django.template import Context, Template

class ImageClearableFileInput(ClearableFileInput):
    template_with_initial = u'%(clear_template)s<br />%(input_text)s: %(input)s'

    def __init__(self, size="80x80", attrs=None):
        self.size = size
        super(ImageClearableFileInput, self).__init__(attrs)

    def img_id(self, name):
        return name + "_img_id"

    def render(self, name, value, attrs=None):
        html = super(ImageClearableFileInput, self).render(name, value, attrs)
        t = Template("{% load thumbnail %}{% thumbnail v " + self.size + " %}")
        c = Context({"v": value})
        img = u'<img id="%s" src="%s"/>' % (self.img_id(name), t.render(c))
        img = u'<a href="%s" target="_blank">%s</a>' % (value.url, img)
        html = img + html
        return mark_safe(html)
