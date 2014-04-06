# encoding: utf8
from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('storage_hash', models.CharField(max_length=40, db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                u'unique_together': set([('storage_hash', 'name')]),
                u'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('storage_hash', models.CharField(max_length=40, db_index=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('source', models.ForeignKey(to='easy_thumbnails.Source', to_field=u'id')),
            ],
            options={
                u'unique_together': set([('storage_hash', 'name', 'source')]),
            },
            bases=(models.Model,),
        ),
    ]
