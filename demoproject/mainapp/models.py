from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField


class TestImage(models.Model):
    title = models.CharField(max_length=100)
    image = ThumbnailerImageField(upload_to="images")

    def __str__(self):
        return self.title
