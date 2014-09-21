# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('storage_hash', models.CharField(max_length=40, db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('storage_hash', models.CharField(max_length=40, db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('source', models.ForeignKey(related_name='thumbnails', to='easy_thumbnails.Source')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='thumbnail',
            unique_together=set([('storage_hash', 'name', 'source')]),
        ),
        migrations.AlterUniqueTogether(
            name='source',
            unique_together=set([('storage_hash', 'name')]),
        ),
    ]
