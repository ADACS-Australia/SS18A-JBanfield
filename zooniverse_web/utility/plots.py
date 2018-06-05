import astropy.units as u
import pickle
import os

from astropy.coordinates import SkyCoord
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.transform import factor_cmap
from django.conf import settings

from zooniverse_web.models import (
    Galaxy, Response, QuestionResponse
)
from zooniverse_web.utility.constants import display_plot_size_x, display_plot_size_y, sky_projection_plot_x, \
    sky_projection_plot_y, ra_pickle_name, dec_pickle_name

import matplotlib
# this must be used like the following, as there are some crashing issues in second request to the page
# setting up the matplotlib backend as 'Agg'
matplotlib.use('Agg')
# now importing the pyplot
import matplotlib.pyplot as plt


def generate_sky_projection(request):

    # getting pickle files location
    ra_pickle = settings.MEDIA_ROOT + ra_pickle_name
    dec_pickle = settings.MEDIA_ROOT + dec_pickle_name

    # checking pickle exists? if yes, loading from the file
    if os.path.isfile(ra_pickle) and os.path.isfile(dec_pickle):
        with open(ra_pickle, 'rb') as ra_pickle_in:
            ra_rad = pickle.load(ra_pickle_in)

        with open(dec_pickle, 'rb') as dec_pickle_in:
            dec_rad = pickle.load(dec_pickle_in)

    else:  # otherwise reading from database and saving in the pickle files
        # cleaning up pickle files if exists (can only happen if one is missing)
        if os.path.isfile(ra_pickle):
            os.remove(ra_pickle)

        if os.path.isfile(dec_pickle):
            os.remove(dec_pickle)

        galaxies = Galaxy.objects.all()

        ra = []
        dec = []

        for galaxy in galaxies:
            ra.append(galaxy.ra)
            dec.append(galaxy.dec)

        c = SkyCoord(ra=ra, dec=dec, frame='icrs', unit=(u.hourangle, u.degree))
        ra_rad = c.ra.wrap_at(180 * u.deg).radian
        dec_rad = c.dec.radian

        with open(ra_pickle, "wb") as ra_pickle_out:
            pickle.dump(ra_rad, ra_pickle_out)

        with open(dec_pickle, "wb") as dec_pickle_out:
            pickle.dump(dec_rad, dec_pickle_out)

    plt.figure(figsize=(8, 4.2))
    plt.subplot(111, projection="aitoff")
    plt.title("Sky Projection")
    plt.grid(True)
    plt.plot(ra_rad, dec_rad, 'o', markersize=2, alpha=0.3)

    try:
        response = Response.objects.get(survey=request.session['survey_id'],
                                                user=request.user)
        question_responses = QuestionResponse.objects.filter(response=response)

        ra = []
        dec = []
        for response in question_responses:
            ra.append(response.survey_question.survey_element.galaxy.ra)
            dec.append(response.survey_question.survey_element.galaxy.dec)

        c = SkyCoord(ra=ra, dec=dec, frame='icrs', unit=(u.hourangle, u.degree))
        ra_rad2 = c.ra.wrap_at(180 * u.deg).radian
        dec_rad2 = c.dec.radian

        plt.plot(ra_rad2, dec_rad2, '*', markersize=7, alpha=1, color='red')
    except Response.DoesNotExist:  # No response yet
        pass

    # plt.plot(ra_rad, dec_rad, 'o', markersize=2, alpha=0.3)
    plt.subplots_adjust(top=0.95, bottom=0.0)
    image = 'sky_projection_{}.png'.format(request.user.username)
    plt.savefig(settings.MEDIA_ROOT + image)
    # plt.show()
    return settings.MEDIA_URL + image


class Plot:
    label = ''
    script = None
    div = None

    def __init__(self, label):
        self.label = label

        self.script, self.div = components(self._set_plot(), CDN)

    def _set_plot(self):
        fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
        counts = [5, 3, 4, 2, 4, 6]

        source = ColumnDataSource(data=dict(fruits=fruits, counts=counts))

        plot = figure(x_range=fruits, y_range=(2, 8), width=display_plot_size_x, height=display_plot_size_y)
        plot.vbar(x='fruits', top='counts', width=0.9, source=source, legend="fruits",
                  line_color='white', fill_color=factor_cmap('fruits', palette=Spectral6, factors=fruits))
        plot.axis.visible = False
        plot.background_fill_color = "#FFFFFF"
        plot.background_fill_alpha = 0.8
        plot.grid.grid_line_color = None

        return plot


class SkyProjectionPlot(Plot):

    request = None

    def __init__(self, request):
        self.request = request
        super(SkyProjectionPlot, self).__init__(label='Sky Projection')

    def _set_plot(self):
        url = generate_sky_projection(self.request)

        # constructing bokeh figure
        plot = figure(
            x_range=(0, 1),
            y_range=(0, 1),
            width=sky_projection_plot_x,
            height=sky_projection_plot_y,
            logo=None,
            tools=['box_zoom,wheel_zoom,reset,pan'],
        )

        # adding image to the figure
        plot.image_url(
            url=[url], x=0, y=0, w=1, h=1, anchor="bottom_left",
        )

        plot.axis.visible = False
        plot.background_fill_color = "#000000"
        plot.background_fill_alpha = 0.8
        plot.grid.grid_line_color = None
        return plot


def get_plots(request):
    plots = [SkyProjectionPlot(request=request), ]
    return plots
