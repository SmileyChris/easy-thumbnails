from easy_thumbnails.conf import settings


class ThumbnailOptions(dict):

    def __init__(self, *args, **kwargs):
        self._prepared_options = None
        super().__init__(*args, **kwargs)
        if settings.THUMBNAIL_DEFAULT_OPTIONS:
            for key, value in settings.THUMBNAIL_DEFAULT_OPTIONS.items():
                self.setdefault(key, value)
        self.setdefault('quality', settings.THUMBNAIL_QUALITY)
        self.setdefault('subsampling', 2)

    def prepared_options(self):
        prepared_opts = ['%sx%s' % tuple(self['size'])]

        subsampling = str(self['subsampling'])
        if subsampling == '2':
            subsampling_text = ''
        else:
            subsampling_text = 'ss%s' % subsampling
        prepared_opts.append('q%s%s' % (self['quality'], subsampling_text))

        for key, value in sorted(self.items()):
            if key == key.upper():
                # Uppercase options aren't used by prepared options (a primary
                # use of prepared options is to generate the filename -- these
                # options don't alter the filename).
                continue
            if not value or key in ('size', 'quality', 'subsampling'):
                continue
            if value is True:
                prepared_opts.append(key)
                continue
            if not isinstance(value, str):
                try:
                    value = ','.join([str(item) for item in value])
                except TypeError:
                    value = str(value)
            prepared_opts.append('%s-%s' % (key, value))

        return prepared_opts
