from django.template import Library, Node, VariableDoesNotExist, \
    TemplateSyntaxError
from easy_thumbnails import utils
from easy_thumbnails.files import get_thumbnailer
from django.utils.html import escape
import re

register = Library()

RE_SIZE = re.compile(r'(\d+)x(\d+)$')

VALID_OPTIONS = utils.valid_processor_options()
VALID_OPTIONS.remove('size')


def split_args(args):
    """
    Split a list of argument strings into a dictionary where each key is an
    argument name.

    An argument looks like ``crop``, ``crop="some option"`` or ``crop=my_var``.
    Arguments which provide no value get a value of ``True``.

    """
    args_dict = {}
    for arg in args:
        split_arg = arg.split('=', 1)
        if len(split_arg) > 1:
            value = split_arg[1]
        else:
            value = True
        args_dict[split_arg[0]] = value
    return args_dict


class ThumbnailNode(Node):
    def __init__(self, source_var, opts, context_name=None):
        self.source_var = source_var
        self.opts = opts
        self.context_name = context_name

    def render(self, context):
        # Note that this isn't a global constant because we need to change the
        # value for tests.
        raise_errors = utils.get_setting('DEBUG')
        # Get the source file.
        try:
            source = self.source_var.resolve(context)
        except VariableDoesNotExist:
            if raise_errors:
                raise VariableDoesNotExist("Variable '%s' does not exist." %
                        self.source_var)
            return self.bail_out(context)
        if not source:
            if raise_errors:
                raise TemplateSyntaxError(
                    "Variable '%s' is an invalid source." % self.source_var
                )
            return self.bail_out(context)
        # Resolve the thumbnail option values.
        try:
            opts = {}
            for key, value in self.opts.iteritems():
                if hasattr(value, 'resolve'):
                    value = value.resolve(context)
                opts[str(key)] = value
        except Exception:
            if raise_errors:
                raise
            return self.bail_out(context)
        # Size variable can be either a tuple/list of two integers or a
        # valid string.
        size = opts['size']
        if isinstance(size, basestring):
            m = RE_SIZE.match(size)
            if m:
                opts['size'] = (int(m.group(1)), int(m.group(2)))
            else:
                if raise_errors:
                    raise TemplateSyntaxError("%r is not a valid size." % size)
                return self.bail_out(context)
        # Ensure the quality is an integer.
        if 'quality' in opts:
            try:
                opts['quality'] = int(opts['quality'])
            except (TypeError, ValueError):
                if raise_errors:
                    raise TemplateSyntaxError("%r is an invalid quality." %
                                              opts['quality'])
                return self.bail_out(context)

        try:
            thumbnail = get_thumbnailer(source).get_thumbnail(opts)
        except Exception:
            if raise_errors:
                raise
            return self.bail_out(context)
        # Return the thumbnail file url, or put the file on the context.
        if self.context_name is None:
            return escape(thumbnail.url)
        else:
            context[self.context_name] = thumbnail
            return ''

    def bail_out(self, context):
        if self.context_name:
            context[self.context_name] = ''
        return ''


def thumbnail(parser, token):
    """
    Creates a thumbnail of an ImageField.

    Basic tag Syntax::

        {% thumbnail [source] [size] [options] %}

    *source* must be a ``File`` object, usually an Image/FileField of a model
    instance.

    *size* can either be:

    * the size in the format ``[width]x[height]`` (for example,
      ``{% thumbnail person.photo 100x50 %}``) or

    * a variable containing a valid size (i.e. either a string in the
      ``[width]x[height]`` format or a tuple containing two integers):
      ``{% thumbnail person.photo size_var %}``.

    *options* are a space separated list of options which are used when
    processing the image to a thumbnail such as ``sharpen``, ``crop`` and
    ``quality=90``.

    The thumbnail tag can also place a ``ThumbnailFile`` object in the context,
    providing access to the properties of the thumbnail such as the height and
    width::

        {% thumbnail [source] [size] [options] as [variable] %}

    When ``as [variable]`` is used, the tag does not return the absolute URL of
    the thumbnail.

    **Debugging**

    By default, if there is an error creating the thumbnail or resolving the
    image variable then the thumbnail tag will just return an empty string (and
    if there was a context variable to be set then it will also be set to an
    empty string).

    For example, you will not see an error if the thumbnail could not
    be written to directory because of permissions error. To display those
    errors rather than failing silently, set ``THUMBNAIL_DEBUG = True`` in
    your Django project's settings module.

    """
    args = token.split_contents()
    tag = args[0]

    # Check to see if we're setting to a context variable.
    if len(args) > 4 and args[-2] == 'as':
        context_name = args[-1]
        args = args[:-2]
    else:
        context_name = None

    if len(args) < 3:
        raise TemplateSyntaxError("Invalid syntax. Expected "
            "'{%% %s source size [option1 option2 ...] %%}' or "
            "'{%% %s source size [option1 option2 ...] as variable %%}'" %
            (tag, tag))

    opts = {}

    # The first argument is the source file.
    source_var = parser.compile_filter(args[1])

    # The second argument is the requested size. If it's the static "10x10"
    # format, wrap it in quotes so that it is compiled correctly.
    size = args[2]
    match = RE_SIZE.match(size)
    if match:
        size = '"%s"' % size
    opts['size'] = parser.compile_filter(size)

    # All further arguments are options.
    args_list = split_args(args[3:]).items()
    for arg, value in args_list:
        if arg in VALID_OPTIONS:
            if value and value is not True:
                value = parser.compile_filter(value)
            opts[arg] = value
        else:
            raise TemplateSyntaxError("'%s' tag received a bad argument: "
                                      "'%s'" % (tag, arg))
    return ThumbnailNode(source_var, opts=opts, context_name=context_name)


register.tag(thumbnail)
