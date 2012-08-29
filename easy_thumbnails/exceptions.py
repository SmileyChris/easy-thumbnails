class EasyThumbnailsError(Exception):
    pass


class InvalidImageFormatError(EasyThumbnailsError):
    pass


# Make this error silent when it crops up in a template (most likely via
# Thumbnailer.__getitem__).
InvalidImageFormatError.silent_variable_failure = True
