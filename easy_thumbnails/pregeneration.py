def register(model, field, aliases, on_save=False):
    """
    Register an ImageField to the registry.

    The ``model`` argument should be a django Model and ``field`` either a
    string or list of strings for the field names of ``ImageField``s on the
    model.

    The ``aliases`` argument should be a dictionary of aliases where each key
    is the alias name and the value is an options dictionary.

    Finally, the optional ``on_save`` can be used to ensure the thumbnail(s)
    are updated when the model is saved (defaults to ``False``).

    """
    pass


def get_thumbnail(profile_field, alias):
    """
    Get thumbnail file by looking up an alias in the pregen registry for an
    ImageField.

    """
    pass
