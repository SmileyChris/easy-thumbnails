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
        prepared_opts = ['{size[0]}x{size[1]}'.format(**self)]

        opts_text = ''
        if 'quality' in self:
            opts_text += 'q{quality}'.format(**self)
        if 'subsampling' in self and str(self['subsampling']) != '2':
            opts_text += 'ss{subsampling}'.format(**self)
        prepared_opts.append(opts_text)

        for key, value in sorted(self.items()):
            if key == key.upper():
                # Uppercase options aren't used by prepared options (a primary
                # use of prepared options is to generate the filename -- these
                # options don't alter the filename).
                continue
            if not value or key in ['size', 'quality', 'subsampling']:
                continue
            if value is True:
                prepared_opts.append(key)
                continue
            if not isinstance(value, str):
                try:
                    value = ','.join([str(item) for item in value])
                except TypeError:
                    value = str(value)
            prepared_opts.append('{0}-{1}'.format(key, value))

        return prepared_opts
