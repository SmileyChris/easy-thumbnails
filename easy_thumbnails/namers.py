import base64
import os

from easy_thumbnails.utils import sha1_not_used_for_security


def default(thumbnailer, prepared_options, source_filename,
            thumbnail_extension, **kwargs):
    """
    Easy-thumbnails' default name processor.

    For example: ``source.jpg.100x100_q80_crop_upscale.jpg``
    """
    filename_parts = [source_filename]
    if ('%(opts)s' in thumbnailer.thumbnail_basedir or
            '%(opts)s' in thumbnailer.thumbnail_subdir):
        if thumbnail_extension != os.path.splitext(source_filename)[1][1:]:
            filename_parts.append(thumbnail_extension)
    else:
        filename_parts.extend(['_'.join(prepared_options), thumbnail_extension])
    return '.'.join(filename_parts)


def alias(thumbnailer, thumbnail_options, source_filename,
            thumbnail_extension, **kwargs):
    """
    Generate filename based on thumbnail alias name (option ``THUMBNAIL_ALIASES``).

    For example: ``source.jpg.medium_large.jpg``
    """
    return '.'.join([source_filename, thumbnail_options.get('ALIAS', ''), thumbnail_extension])


def hashed(source_filename, prepared_options, thumbnail_extension, **kwargs):
    """
    Generate a short hashed thumbnail filename.

    Creates a 12 character url-safe base64 sha1 filename (plus the extension),
    for example: ``6qW1buHgLaZ9.jpg``.
    """
    parts = ':'.join([source_filename] + prepared_options)
    short_sha = sha1_not_used_for_security(parts.encode('utf-8')).digest()
    short_hash = base64.urlsafe_b64encode(short_sha[:9]).decode('utf-8')
    return '.'.join([short_hash, thumbnail_extension])


def source_hashed(source_filename, prepared_options, thumbnail_extension,
                  **kwargs):
    """
    Generate a thumbnail filename of the source filename and options separately
    hashed, along with the size.

    The format of the filename is a 12 character base64 sha1 hash of the source
    filename, the size surrounded by underscores, and an 8 character options
    base64 sha1 hash of the thumbnail options. For example:
    ``1xedFtqllFo9_100x100_QHCa6G1l.jpg``.
    """
    source_sha = sha1_not_used_for_security(source_filename.encode('utf-8')).digest()
    source_hash = base64.urlsafe_b64encode(source_sha[:9]).decode('utf-8')
    parts = ':'.join(prepared_options[1:])
    parts_sha = sha1_not_used_for_security(parts.encode('utf-8')).digest()
    options_hash = base64.urlsafe_b64encode(parts_sha[:6]).decode('utf-8')
    return '%s_%s_%s.%s' % (
        source_hash, prepared_options[0], options_hash, thumbnail_extension)
