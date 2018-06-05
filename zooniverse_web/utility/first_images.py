from astropy.utils.data import download_file
from astropy.io import fits
from matplotlib.image import imsave
from django.conf import settings
from astropy import visualization as vis

import logging

logger = logging.getLogger(__name__)


def replace_space(string):
    return string.replace(' ', '%20')


def replace_plus_minus(string):
    return str(string).replace('-', '%2D').replace('+', '%2B')


def remove_plus_minus(string):
    return str(string).replace('-', '').replace('+', '')


def construct_image_url(ra, dec, size=4.5, maxint=10, fits=0):

    ra_dec = "{} {}".format(remove_plus_minus(ra),
                            remove_plus_minus(dec))

    ra_dec = replace_space(ra_dec)

    url = "https://third.ucllnl.org/cgi-bin/firstimage?" \
          "RA={}&" \
          "Dec=&Equinox=J2000&" \
          "ImageSize={}&" \
          "MaxInt={}&" \
          "FITS={}".format(ra_dec, size, maxint, fits)

    return url


def download_first_image(url, galaxy):
    """
    Download first image from the url
    :param url: link of the image
    :param galaxy: galaxy object
    :return: url of the saved image
    """
    stretch = vis.MinMaxInterval() + vis.AsinhStretch(0.01)

    file_url = settings.MEDIA_ROOT + 'temp_images/' + galaxy.first + '.png'
    try:
        imsave(file_url, stretch(fits.open(download_file(url, cache=True))[0].data), cmap='inferno')
    except OSError:
        logger.info("Something is wrong with the fits file for url = {}".format(url))
        logger.error(OSError)
        file_url = settings.MEDIA_ROOT + 'temp_images/no_image.png'

    return file_url
