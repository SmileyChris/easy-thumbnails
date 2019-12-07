import logging
import subprocess
from imghdr import what as determinetype
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from easy_thumbnails.optimize.conf import settings


try:
    from subprocess import check_output
except ImportError:
    def check_output(*popenargs, **kwargs):
        """
        Run command with arguments and return its output as a byte string.

        Backported from Python 2.7 as it's implemented as pure python on
        stdlib.
        """
        process = subprocess.Popen(
            stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            error = subprocess.CalledProcessError(retcode, cmd)
            error.output = output
            raise error
        return output


logger = logging.getLogger('easy_thumbnails.optimize')


def optimize_thumbnail(thumbnail):
    '''Optimize thumbnail images by removing unnecessary data'''
    try:
        optimize_command = settings.THUMBNAIL_OPTIMIZE_COMMAND[
            determinetype(thumbnail.path)]
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
            output = check_output(
                optimize_command, stderr=subprocess.STDOUT, shell=True)
            if output:
                logger.warning(
                    '{0} returned {1}'.format(optimize_command, output))
            else:
                logger.info('{0} returned nothing'.format(optimize_command))
            with open(temp_file.name, 'rb') as f:
                thumbnail.file = ContentFile(f.read())
                storage.delete(thumbnail.path)
                storage.save(thumbnail.path, thumbnail)
    except Exception as e:
        logger.error(e)
