import gc
import os
import time
from datetime import datetime, date, timedelta
from optparse import make_option

from django.core.files.storage import get_storage_class
from django.core.management.base import BaseCommand
from easy_thumbnails.conf import settings
from easy_thumbnails.models import Source


class ThumbnailCollectionCleaner(object):
    """
    Remove thumbnails and DB references to non-existing source images.
    """
    sources = 0
    thumbnails = 0
    thumbnails_deleted = 0
    source_refs_deleted = 0
    execution_time = 0

    def _get_absolute_path(self, path):
        return os.path.join(settings.MEDIA_ROOT, path)

    def _get_relative_path(self, path):
        return os.path.relpath(path, settings.MEDIA_ROOT)

    def _check_if_exists(self, storage, path):
        try:
            return storage.exists(path)
        except Exception as e:
            print("Something went wrong when checking existance of %s:" % path)
            print(str(e))

    def _delete_sources_by_id(self, ids):
        Source.objects.all().filter(id__in=ids).delete()

    def clean_up(self, dry_run=False, verbosity=1, last_n_days=0,
                 cleanup_path=None, storage=None):
        """
        Iterate through sources. Delete database references to sources
        not existing, including its corresponding thumbnails (files and
        database references).
        """
        if dry_run:
            print ("Dry run...")

        if not storage:
            storage = get_storage_class(settings.THUMBNAIL_DEFAULT_STORAGE)()

        sources_to_delete = []
        time_start = time.time()

        query = Source.objects.all()
        if last_n_days > 0:
            today = date.today()
            query = query.filter(
                modified__range=(today - timedelta(days=last_n_days), today))
        if cleanup_path:
            query = query.filter(name__startswith=cleanup_path)

        for source in queryset_iterator(query):
            self.sources += 1
            abs_source_path = self._get_absolute_path(source.name)

            if not self._check_if_exists(storage, abs_source_path):
                if verbosity > 0:
                    print ("Source not present:", abs_source_path)
                self.source_refs_deleted += 1
                sources_to_delete.append(source.id)

                for thumb in source.thumbnails.all():
                    self.thumbnails_deleted += 1
                    abs_thumbnail_path = self._get_absolute_path(thumb.name)

                    if self._check_if_exists(storage, abs_thumbnail_path):
                        if not dry_run:
                            storage.delete(abs_thumbnail_path)
                        if verbosity > 0:
                            print ("Deleting thumbnail:", abs_thumbnail_path)

            if len(sources_to_delete) >= 1000 and not dry_run:
                self._delete_sources_by_id(sources_to_delete)
                sources_to_delete = []

        if not dry_run:
            self._delete_sources_by_id(sources_to_delete)
        self.execution_time = round(time.time() - time_start)

    def print_stats(self):
        """
        Print statistics about the cleanup performed.
        """
        print(
            "{0:-<48}".format(str(datetime.now().strftime('%Y-%m-%d %H:%M '))))
        print("{0:<40} {1:>7}".format("Sources checked:", self.sources))
        print("{0:<40} {1:>7}".format(
            "Source references deleted from DB:", self.source_refs_deleted))
        print("{0:<40} {1:>7}".format("Thumbnails deleted from disk:",
                                    self.thumbnails_deleted))
        print("(Completed in %s seconds)\n" % self.execution_time)


def queryset_iterator(queryset, chunksize=1000):
    """
    The queryset iterator helps to keep the memory consumption down.
    And also making it easier to process for weaker computers.
    """
    if queryset.exists():
        primary_key = 0
        last_pk = queryset.order_by('-pk')[0].pk
        queryset = queryset.order_by('pk')
        while primary_key < last_pk:
            for row in queryset.filter(pk__gt=primary_key)[:chunksize]:
                primary_key = row.pk
                yield row
            gc.collect()


class Command(BaseCommand):
    help = """ Deletes thumbnails that no longer have an original file. """

    # Legacy options, not needed in Django 1.8+
    option_list = getattr(BaseCommand, 'option_list', ()) + (
        make_option(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Dry run the execution.'),
        make_option(
            '--last-n-days',
            action='store',
            dest='last_n_days',
            default=0,
            type='int',
            help='The number of days back in time to clean thumbnails for.'),
        make_option(
            '--path',
            action='store',
            dest='cleanup_path',
            type='string',
            help='Specify a path to clean up.'),
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Dry run the execution.')
        parser.add_argument(
            '--last-n-days',
            action='store',
            dest='last_n_days',
            default=0,
            type='int',
            help='The number of days back in time to clean thumbnails for.')
        parser.add_argument(
            '--path',
            action='store',
            dest='cleanup_path',
            type='string',
            help='Specify a path to clean up.')

    def handle(self, *args, **options):
        tcc = ThumbnailCollectionCleaner()
        tcc.clean_up(
            dry_run=options.get('dry_run', False),
            verbosity=int(options.get('verbosity', 1)),
            last_n_days=int(options.get('last_n_days', 0)),
            cleanup_path=options.get('cleanup_path'))
        tcc.print_stats()
