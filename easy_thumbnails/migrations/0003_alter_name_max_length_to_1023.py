# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('easy_thumbnails', '0002_thumbnaildimensions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='name',
            field=models.CharField(max_length=1023, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='thumbnail',
            name='name',
            field=models.CharField(max_length=1023, db_index=True),
            preserve_default=True,
        ),
    ]
