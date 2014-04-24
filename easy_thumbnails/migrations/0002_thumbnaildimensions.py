# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('easy_thumbnails', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThumbnailDimensions',
            fields=[
                (u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True)),
                ('thumbnail', models.OneToOneField(to='easy_thumbnails.Thumbnail', to_field=u'id')),
                ('width', models.PositiveIntegerField(null=True)),
                ('height', models.PositiveIntegerField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
