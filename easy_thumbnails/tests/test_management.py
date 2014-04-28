from easy_thumbnails.tests import utils as test


class ThumbnailCleanupTests(test.BaseTest):

    def test_can_import(self):
        """
        Just a simple test to see if we can actually import the command without
        any syntax errors.
        """
        import easy_thumbnails.management.commands.thumbnail_cleanup   # NOQA
