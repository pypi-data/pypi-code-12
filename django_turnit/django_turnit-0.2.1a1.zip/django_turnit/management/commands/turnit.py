# -*- coding: utf-8 -*-
"""
Bunch of commands to update thumbnails

:creationdate: 07/03/16 14:57
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_turnit.management.command.turnit

"""
import logging
import sys
import timeit
from multiprocessing import Pool

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db import transaction

from django_turnit.backends import get_backend_class
from django_turnit.utilities import get_file_field_from_id

__author__ = 'fguerin'
logger = logging.getLogger('django_turnit.management.command.turnit')


class Command(BaseCommand):
    # args = "file field instances in <app_label>.<model_name>.<pk>.<field> format"
    verbosity = None
    dry_run = False
    force = False
    file_field_list = None
    processes = 1

    def add_arguments(self, parser):
        parser.add_argument('-n', '--dry-run', dest='dry_run', action='store_true', default=False,
                            help="If set, no actions are performed to database.")
        parser.add_argument('-f', '--force', dest='force', action='store_true', default=False,
                            help="If set, forces the generation of the thumbnails, even if they already exists.")
        # parser.add_argument('-p', '--process', dest='processes', action='store', default=1,
        #                     help="If set, <processes> are launched to perform the update.")
        parser.add_argument(dest='args', help="file field instances in <app_label>.<model_name>.<pk>.<field> format. "
                                              "You can set many args to command.", nargs='+', )

    def handle(self, *args, **options):
        self.verbosity = options.get('verbosity')
        self.dry_run = options.get('dry_run')
        self.force = options.get('force')
        self.file_field_list = []
        self.processes = int(options.get('processes', 1))

        if not args:
            raise CommandError('You MUST provide at least 1 argument to the turnit command.')

        for arg in args:
            file_field = get_file_field_from_id(arg, strict=False)
            settings.DEBUG and logger.debug('Command::handle() file_field = %s', file_field)
            self.file_field_list.extend(file_field)

        # self.file_field_list = list(itertools.chain(*self.file_field_list))
        settings.DEBUG and logger.debug(u'Command::handle(%s) %d files found', args, len(self.file_field_list))

        tic = timeit.default_timer()
        thumbnailer_class = get_backend_class()
        # if self.processes == 1:
        for file_field, item_id in self.file_field_list:
            run_thumbnailer((thumbnailer_class, file_field, item_id))
        toc = timeit.default_timer()
        print >> self.stderr, 'Execution time = %s' % (toc - tic)
        print >> self.stderr, '%d files thumnailed' % (len(self.file_field_list))
        return 0


def run_thumbnailer((thumbnailer_class, file_field, item_id)):
    tic = timeit.default_timer()
    pdf_thumbnailer = thumbnailer_class(file_field, item_id)
    pdf_thumbnailer.get_thumbnails()
    toc = timeit.default_timer()
    print >> sys.stderr, "%s file processed in %s seconds" % (file_field, toc - tic)
