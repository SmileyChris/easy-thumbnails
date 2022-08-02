def is_available() -> bool:
    """
    Returns True if SVG support should be available.
    """
    try:
        import easy_thumbnails.VIL.Image
        return True
    except ImportError:
        return False