from easy_thumbnails.conf import settings


class Aliases(object):
    """
    A container which stores and retrieves named easy-thumbnail options
    dictionaries.
    """

    def __init__(self, populate_from_settings=True):
        """
        Initialize the Aliases object.

        :param populate_from_settings: If ``True`` (default) then populate the
            initial aliases from settings. See :meth:`populate_from_settings`.
        """
        self._aliases = {}
        if populate_from_settings:
            self.populate_from_settings()

    def populate_from_settings(self):
        """
        Populate the aliases from the ``THUMBNAIL_ALIASES`` setting.
        """
        settings_aliases = settings.THUMBNAIL_ALIASES
        if settings_aliases:
            for target, aliases in settings_aliases.items():
                target_aliases = self._aliases.setdefault(target, {})
                target_aliases.update(aliases)

    def set(self, alias, options, target=None):
        """
        Add an alias.

        :param alias: The name of the alias to add.
        :param options: The easy-thumbnails options dictonary for this alias
            (should include ``size``).
        :param target: A field, model, or app to limit this alias to
            (optional).
        """
        target = self._coerce_target(target) or ''
        target_aliases = self._aliases.setdefault(target, {})
        target_aliases[alias] = options

    def get(self, alias, target=None):
        """
        Get a dictionary of aliased options.

        :param alias: The name of the aliased options.
        :param target: Get alias for this specific target (optional).

        If no matching alias is found, returns ``None``.
        """
        for target_part in reversed(list(self._get_targets(target))):
            options = self._get(target_part, alias)
            if options:
                return options
        return self._get('', alias)

    def all(self, target=None, include_global=True):
        """
        Get a dictionary of all aliases and their options.

        :param target: Include aliases for this specific field, model or app
            (optional).
        :param include_global: Include all non target-specific aliases
            (default ``True``).

        For example::

            >>> aliases.all(target='my_app.MyModel')
            {'small': {'size': (100, 100)}, 'large': {'size': (400, 400)}}
        """
        aliases = {}
        for target_part in self._get_targets(target, include_global):
            aliases.update(self._aliases.get(target_part, {}))
        return aliases

    def _get(self, target, alias):
        """
        Internal method to get a specific alias.
        """
        if target not in self._aliases:
            return
        return self._aliases[target].get(alias)

    def _get_targets(self, target, include_global=True):
        """
        Internal iterator to split up a complete target into the possible parts
        it may match.

        For example::

            >>> list(aliases._get_targets('my_app.MyModel.somefield'))
            ['', 'my_app', 'my_app.MyModel', 'my_app.MyModel.somefield']
        """
        target = self._coerce_target(target)
        if include_global:
            yield ''
        if not target:
            return
        target_bits = target.split('.')
        for i in range(len(target_bits)):
            yield '.'.join(target_bits[:i + 1])

    def _coerce_target(self, target):
        """
        Internal method to coerce a target to a string.

        The assumption is that if it is not ``None`` and not a string, it is
        a Django ``FieldFile`` object.
        """
        if not target or isinstance(target, basestring):
            return target
        model = target.instance.__class__
        return '%s.%s.%s' % (
            model._meta.app_label,
            model.__name__,
            target.field.name,
        )


aliases = Aliases()
