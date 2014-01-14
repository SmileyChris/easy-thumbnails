# -*- coding: utf-8 -*-
import logging
from subprocess import check_output, STDOUT
from imghdr import what as determinetype
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from conf import settings

logger = logging.getLogger('easy_thumbnails.optimize')


def optimize_thumbnail(thumbnail):
    '''Optimize thumbnail images by removing unnecessary data'''
    try:
        optimize_command = settings.THUMBNAIL_OPTIMIZE_COMMAND[determinetype(thumbnail.path)]
        if not optimize_command:
            return
    except (TypeError, KeyError, NotImplementedError):
        return
    storage = thumbnail.storage
    try:
        with NamedTemporaryFile() as temp_file:
            thumbnail.seek(0)
            temp_file.write(thumbnail.read())
            temp_file.flush()
            optimize_command = optimize_command.format(filename=temp_file.name)
            output = check_output(optimize_command, stderr=STDOUT, shell=True)
            if output:
                logger.warn('%s returned %s' % (optimize_command, output))
            else:
                logger.info('%s returned nothing' % optimize_command)
            with open(temp_file.name, 'rb') as f:
                thumbnail.file = ContentFile(f.read())
                storage.delete(thumbnail.path)
                storage.save(thumbnail.path, thumbnail)
    except Exception as e:
        logger.error(e)
