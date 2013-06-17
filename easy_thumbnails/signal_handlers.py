from django.db.models.fields.files import FileField

from easy_thumbnails import signals


def find_uncommitted_filefields(sender, instance, **kwargs):
    """
    A pre_save signal handler which attaches an attribute to the model instance
    containing all uncommitted ``FileField``s, which can then be used by the
    :func:`signal_committed_filefields` post_save handler.
    """
    uncommitted = instance._uncommitted_filefields = []

    fields = sender._meta.fields
    if kwargs.get('update_fields', None):
        update_fields = set(kwargs['update_fields'])
        fields = update_fields.intersection(fields)
    for field in fields:
        if isinstance(field, FileField):
            if not getattr(instance, field.name)._committed:
                uncommitted.append(field.name)


def signal_committed_filefields(sender, instance, **kwargs):
    """
    A post_save signal handler which sends a signal for each ``FileField`` that
    was committed this save.
    """
    for field_name in getattr(instance, '_uncommitted_filefields', ()):
        fieldfile = getattr(instance, field_name)
        # Don't send the signal for deleted files.
        if fieldfile:
            signals.saved_file.send_robust(sender=sender, fieldfile=fieldfile)


def generate_aliases(fieldfile, **kwargs):
    """
    A saved_file signal handler which generates thumbnails for all field,
    model, and app specific aliases matching the saved file's field.
    """
    # Avoids circular import.
    from easy_thumbnails.files import generate_all_aliases
    generate_all_aliases(fieldfile, include_global=False)


def generate_aliases_global(fieldfile, **kwargs):
    """
    A saved_file signal handler which generates thumbnails for all field,
    model, and app specific aliases matching the saved file's field, also
    generating thumbnails for each project-wide alias.
    """
    # Avoids circular import.
    from easy_thumbnails.files import generate_all_aliases
    generate_all_aliases(fieldfile, include_global=True)
