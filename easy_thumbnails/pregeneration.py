from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.files import FileField
import warnings
from easy_thumbnails.files import get_thumbnailer

_pregen_registry = {}


class RegisterError(Exception):
    pass


class AliasNotFound(Exception):
    pass


def register(model, fields, aliases, on_save=False):
    """
    Register an ImageField to the registry.

    The ``model`` argument should be a Django Model and ``fields`` either a
    string or list of strings for the field names of ``ImageField``s on the
    model.

    The ``aliases`` argument should be a dictionary of aliases where each key
    is the alias name and the value is an options dictionary.

    Finally, the optional ``on_save`` can be used to ensure the thumbnail(s)
    are updated when the model is saved (defaults to ``False``).

    """
    if not fields:
        raise RegisterError('No fields were specified')

    if not aliases:
        raise RegisterError('No aliases were specified')

    # Ensure fields is actually a list of fields.
    if isinstance(fields, basestring):
        fields = [fields]

    # Check that the model actually *has* those fields and that they are
    # ImageFields.
    opt = model._meta
    for field_name in fields:
        try:
            field = opt.get_field(field_name)
        except FieldDoesNotExist:
            raise RegisterError('The model %s does not have a field named %s' %
                                (model.__name__, field_name))
        if not isinstance(field, FileField):
            raise RegisterError('%s.%s is not a FileField' % (model.__name__,
                                                              field_name))

    model_fields = _pregen_registry.setdefault(model, {})
    field_aliases = model_fields.setdefault(model, {})

    for alias, opts in aliases.iteritems():
        for field_name in fields:
            if alias in field_aliases:
                warnings.warn('Alias %r is being overridden for %s.%s' %
                              (alias, model.__name__, field_name))
            field_aliases[alias] = (opts, on_save)


def get_thumbnail(field_file, alias):
    """
    Get a thumbnail file by looking up an alias in the pregeneration registry
    for an FieldFile.

    """
    aliases = _get_aliases(field_file)
    alias_bits = aliases.get(alias)
    if not alias:
        raise AliasNotFound('Alias %r not found' % alias)

    return get_thumbnailer(field_file).get_thumbnail(alias_bits[0])


def build_aliases(field_file, save_only=True):
    """
    Build aliased thumbnails for a FieldFile.

    If the ``save_only`` field is set to True (which is the default) then
    only aliases which are registered with ``on_save=True`` will be built. 

    No error is raised if ``field`` doesn't have any aliases registered, but it
    is expected that it is a model field.

    """
    thumbnailer = get_thumbnailer(field_file)

    count = 0
    aliases = _get_aliases(field_file)
    for opts, on_save in aliases.values():
        if on_save or not save_only:
            thumbnailer.get_thumbnail(opts)
            count += 1
    return count


def _get_aliases(field_file):
    if not field_file or not hasattr(field_file, 'field'):
        return {}
    field = field_file.field

    model_fields = _pregen_registry.get(field.model)
    if not model_fields:
        return {}
    
    field_aliases = model_fields.get(field.name)
    return field_aliases or {}


def pregenerate_listener(sender, **options):
    pass