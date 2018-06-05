import os
from django.core.management import BaseCommand
from shutil import copyfile

from zooniverse_web.models import Galaxy, ImageStore
from zooniverse_web.utility import constants
from zooniverse_web.utility.first_images import construct_image_url
from zooniverse_web.utility.tgss_images import construct_tgss_url


def populate_image_store():

    galaxies = Galaxy.objects.all()

    for galaxy in galaxies:
        for database_type in [constants.FIRST, constants.TGSS]:
            try:
                ImageStore.objects.get(galaxy=galaxy, database_type=database_type)
            except ImageStore.DoesNotExist:
                url = construct_tgss_url(ra=galaxy.ra, dec=galaxy.dec) \
                    if database_type == constants.TGSS \
                    else construct_image_url(ra=galaxy.ra, dec=galaxy.dec, fits=1)

                ImageStore.objects.create(
                    galaxy=galaxy,
                    database_type=database_type,
                    actual_url=url,
                )


def depopulate_image_store():
    ImageStore.objects.all().delete()


class Command(BaseCommand):

    help = 'Populating ImageStore and downloading all images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--task',
            dest='task',
            default='download',
            nargs='?',
            help='[download] for downloading and [reverse] for deleting the downloaded objects'
        )

    def handle(self, *args, **options):

        # checking for options
        if options['task'] == 'download':
            populate_image_store()
        elif options['task'] == 'reverse':
            depopulate_image_store()
        else:
            print('For usage: images -h')
            return
