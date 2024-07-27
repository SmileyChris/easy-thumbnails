from django import forms
from easy_thumbnails.widgets import ImageClearableFileInput

from .models import TestImage


class TestImageForm(forms.ModelForm):
    class Meta:
        model = TestImage
        fields = ["title", "image"]
        widgets = {
            "image": ImageClearableFileInput,
        }
