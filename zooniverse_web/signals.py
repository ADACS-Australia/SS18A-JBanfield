from io import BytesIO

from future.standard_library import install_aliases

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.core.files.base import ContentFile

from PIL import Image

from zooniverse_web.models import ImageStore
from zooniverse_web.utility.first_images import download_first_image
from zooniverse_web.utility.tgss_images import download_tgss_image

install_aliases()
from urllib.parse import urlparse


@receiver(pre_delete, sender=ImageStore, dispatch_uid='delete_image_file')
def delete_image_file(instance, **kwargs):
    """
    Deleting the image when the database object is deleted
    :param instance: instance of the ImageStore object
    :param kwargs: keyword arguments
    """
    if instance.pk:
        instance.image.delete(save=True)


@receiver(pre_save, sender=ImageStore, dispatch_uid='download_image')
def download_image(instance, **kwargs):
    """
    Download the image and save it to the media file
    :param instance: instance of the object
    :param kwargs: keyword arguments
    """

    from os import remove

    if not instance.pk:
        file_url = download_first_image(instance.actual_url, instance.galaxy) \
            if instance.database_type == instance.FIRST \
            else download_tgss_image(instance.actual_url)

        filename = urlparse(file_url).path.split('/')[-1]
        temp_file = Image.open(file_url)
        temp_file_io = BytesIO()
        temp_file.save(temp_file_io, format=temp_file.format)
        instance.image = filename
        instance.image.save(filename, ContentFile(temp_file_io.getvalue()), save=False)

        remove(file_url)
