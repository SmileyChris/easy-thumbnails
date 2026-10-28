from django.db import models

from easy_thumbnails.fields import ThumbnailerField, ThumbnailerImageField


class TestModel(models.Model):
    avatar = ThumbnailerField(upload_to='avatars')
    picture = ThumbnailerImageField(upload_to='pictures',
                                    resize_source=dict(size=(10, 10)))


class Profile(models.Model):
    avatar = ThumbnailerField(upload_to='avatars')
    logo = models.FileField(upload_to='avatars')

    class Meta:
        app_label = 'easy_thumbnails_tests'


class DimensionModel(models.Model):
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    picture = ThumbnailerImageField(
        upload_to='pictures', width_field='width', height_field='height',
        resize_source={'size': (100, 100)})
    label = models.CharField(max_length=20, default='')


class DimensionChild(DimensionModel):
    extra = models.CharField(max_length=20, default='')
