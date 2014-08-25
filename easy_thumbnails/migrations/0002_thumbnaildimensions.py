# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('easy_thumbnails', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThumbnailDimensions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('width', models.PositiveIntegerField(null=True)),
                ('height', models.PositiveIntegerField(null=True)),
                ('thumbnail', models.OneToOneField(related_name=b'dimensions', to='easy_thumbnails.Thumbnail')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
