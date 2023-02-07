import gc
import os
import time
from datetime import date

from django.core.files.storage import get_storage_class
from django.core.management.base import BaseCommand
from django.utils.timezone import datetime, timedelta

from easy_thumbnails.conf import settings
from easy_thumbnails.models import Source


class ThumbnailCollectionCleaner:
    """
    Remove thumbnails and DB references to non-existing source images.
    """
    sources = 0
    thumbnails = 0
    thumbnails_deleted = 0
    orphans_deleted = 0
    source_refs_deleted = 0
    execution_time = 0

    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

    def _get_absolute_path(self, path):
        return os.path.join(settings.MEDIA_ROOT, path)

    def _get_relative_path(self, path):
        return os.path.relpath(path, settings.MEDIA_ROOT)

    def _check_if_exists(self, storage, path):
        try:
            return storage.exists(path)
        except Exception as e:
            self.stderr.write("Something went wrong when checking existance of {}:".format(path))
            self.stderr.write(e)

    def _delete_sources_by_id(self, ids):
        Source.objects.all().filter(id__in=ids).delete()

    def _get_all_thumbfiles_in_storage(self, storage, path=None):
        if path is None:
            path = os.path.join(settings.MEDIA_ROOT, settings.THUMBNAIL_BASEDIR)

        directories, files = storage.listdir(path)
        for file in files:
            yield os.path.join(path, file)

        for dir in directories:
            for file in self._get_all_thumbfiles_in_storage(storage, path=os.path.join(path, dir)):
                yield file

    def clean_up(self, dry_run=False, verbosity=1, last_n_days=0,
                 cleanup_path=None, storage=None, delete_orphans=False):
        """
        Iterate through sources. Delete database references to sources
        not existing, including its corresponding thumbnails (files and
        database references).
        """
        if (last_n_days > 0 or cleanup_path) and delete_orphans:
            self.stdout.write("WARNING! Conflicting options: "
                              "--delete-orphans not implemented with --last-n-days or --path.")
            delete_orphans = False

        if dry_run:
            self.stdout.write("Dry run...")

        if not storage:
            storage = get_storage_class(settings.THUMBNAIL_DEFAULT_STORAGE)()

        thumbfiles_in_storage = set()
        if delete_orphans:
            thumbfiles_in_storage = set(self._get_all_thumbfiles_in_storage(storage))

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
                    self.stdout.write("Source not present: {}".format(abs_source_path))
                self.source_refs_deleted += 1
                sources_to_delete.append(source.id)

                for thumb in source.thumbnails.all():
                    self.thumbnails_deleted += 1
                    abs_thumbnail_path = self._get_absolute_path(thumb.name)

                    if self._check_if_exists(storage, abs_thumbnail_path):
                        if not dry_run:
                            storage.delete(abs_thumbnail_path)
                        if verbosity > 0:
                            self.stdout.write("Deleting thumbnail: {}".format(abs_thumbnail_path))
            elif delete_orphans:
                for thumb in source.thumbnails.all():
                    abs_thumbnail_path = self._get_absolute_path(thumb.name)
                    try:
                        thumbfiles_in_storage.remove(abs_thumbnail_path)
                    except KeyError:
                        # thumbfile has just not been generated yet, so, ignore this exception
                        pass

            if len(sources_to_delete) >= 1000 and not dry_run:
                self._delete_sources_by_id(sources_to_delete)
                sources_to_delete = []

        if not dry_run:
            self._delete_sources_by_id(sources_to_delete)

        for abs_orphan_path in thumbfiles_in_storage:
            self.orphans_deleted += 1
            if not dry_run:
                storage.delete(abs_orphan_path)
            if verbosity > 0:
                self.stdout.write("Deleting orphan: {}".format(abs_orphan_path))

        self.execution_time = round(time.time() - time_start)

    def print_stats(self):
        """
        Print statistics about the cleanup performed.
        """
        self.stdout.write(
            "{0:-<48}".format(datetime.now().strftime('%Y-%m-%d %H:%M ')))
        self.stdout.write("{0:<40} {1:>7}".format("Sources checked:", self.sources))
        self.stdout.write("{0:<40} {1:>7}".format(
            "Source references deleted from DB:", self.source_refs_deleted))
        self.stdout.write("{0:<40} {1:>7}".format("Thumbnails deleted from disk:",
                                    self.thumbnails_deleted))
        self.stdout.write("{0:<40} {1:>7}".format("Orphans deleted from disk:",
                          self.orphans_deleted))
        self.stdout.write("(Completed in {} seconds)\n".format(self.execution_time))


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
            type=int,
            help='The number of days back in time to clean thumbnails for.')
        parser.add_argument(
            '--path',
            action='store',
            dest='cleanup_path',
            type=str,
            help='Specify a path to clean up.')
        parser.add_argument(
            '--delete-orphans',
            action='store_true',
            dest='delete_orphans',
            default=False,
            help='Check for files in storage that have no source and delete them.')

    def handle(self, *args, **options):
        tcc = ThumbnailCollectionCleaner(self.stdout, self.stderr)
        tcc.clean_up(
            dry_run=options.get('dry_run', False),
            verbosity=int(options.get('verbosity', 1)),
            last_n_days=int(options.get('last_n_days', 0)),
            cleanup_path=options.get('cleanup_path'),
            delete_orphans=options.get('delete_orphans'))
        tcc.print_stats()
