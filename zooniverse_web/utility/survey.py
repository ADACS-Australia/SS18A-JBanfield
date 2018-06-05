import re
from bokeh import events

from bokeh.embed import components
from bokeh.models import BoxZoomTool, ResetTool, CustomJS, WheelZoomTool, PanTool, LassoSelectTool, ColumnDataSource, \
    Patch
from bokeh.plotting import figure

from zooniverse_web.models import (
    Survey, SurveyQuestion, SurveyElement,
    Question, QuestionOption, QuestionResponse, QuestionDrawnResponse,
    ImageStore, Galaxy
)
from zooniverse_web.utility import constants
from zooniverse_web.forms.survey.question import Question as Sq
from zooniverse_web.utility.constants import display_image_size
from zooniverse_web.utility.acton_api import (
    initialise_labels_for_two_predictors, predict_and_combine, get_recommendations,
    get_recommendations_from_file, get_user_labels_for_two_predictors, CSV_COMBINED_LATEST
)
from zooniverse_web.utility.first_images import construct_image_url
from zooniverse_web.utility.tgss_images import construct_tgss_url


class ClassifyObject:
    """Class to classify an object (e.g. galaxy)
    """
    questions = []
    divs = []
    scripts = []
    visited = False

    def __init__(self, questions, divs, scripts, visited):
        self.questions = questions
        self.divs = divs
        self.scripts = scripts
        self.visited = visited


def get_bokeh_images(url, field_name, pre_filled=None):
    """Get images to be rendered with bokeh

    Parameters
    ----------
    url:
    field_name:
    pre_filled:
    """
    if not pre_filled:
        x = []
        y = []
    else:
        x = pre_filled['x']
        y = pre_filled['y']

    # callback for LassoSelectTool
    source = ColumnDataSource(data=dict(x=x, y=y))
    callback = CustomJS(args=dict(source=source), code="""
        // get data source from Callback args
        var data = source.data;
        
        // getting the geometry from cb_data parameter of Callback
        var geometry = cb_data['geometry'];
        
        // pushing Selected portions x, y coordinates for drawing border
        for (i=0; i < geometry.x.length; i++) {
            data['x'].push(geometry.x[i]);
            data['y'].push(geometry.y[i]);
        }
        
        // pushing NaN to separate the selected polygon from others
        // this will also be used for detecting how many polygons have been drawn
        data['x'].push(NaN);
        data['y'].push(NaN);
        
        // count number of selections
        var count = 0
        for (i=0; i < data['x'].length; i++) {
            if (isNaN(data['x'][i])) {
                count++;
            }
        }
        
        document.getElementById('field_name').value = count;
        document.getElementById('field_name_data_x').value = data['x'].join(',');
        document.getElementById('field_name_data_y').value = data['y'].join(',');
        
        // emit update of data source
        source.change.emit();
        """.replace('field_name', field_name))

    callback_reset = CustomJS(args=dict(source=source), code="""
        // get data source from Callback args
        var data = source.data;
        
        // getting the double clicked/tapped coordinates
        var clicked_position = cb_obj;
        
        // clearing the lasso select areas on double click/tap on the figure
        if (clicked_position.x >= 0 && clicked_position.x <= 1 && clicked_position.y >= 0 && clicked_position.y <= 1) {
            data['x'] = [];
            data['y'] = [];
        }
        
        // count number of selections
        var count = 0
        for (i=0; i < data['x'].length; i++) {
            if (isNaN(data['x'][i])) {
                count++;
            }
        }
        
        document.getElementById('field_name').value = count;
        document.getElementById('field_name_data_x').value = '';
        document.getElementById('field_name_data_y').value = '';
        
        // emit update of data source
        source.change.emit();
        """.replace('field_name', field_name))

    # polygon to reflect selected area via LassoSelectTool
    polygon = Patch(
        x='x',
        y='y',
        fill_alpha=0.0,
        fill_color='#009933',
        line_width=1,
        line_alpha=1.0,
        line_color='#FF0000',
    )

    tools = [
        BoxZoomTool(),
        LassoSelectTool(callback=callback, select_every_mousemove=False),
        WheelZoomTool(),
        PanTool(),
        ResetTool(),
    ]

    # constructing bokeh figure
    plot = figure(
        x_range=(0, 1),
        y_range=(0, 1),
        width=display_image_size,
        height=display_image_size,
        logo=None,
        tools=tools,
    )

    # adding image to the figure
    plot.image_url(
        url=[url], x=0, y=0, w=1, h=1, anchor="bottom_left",
    )

    # adding polygon to the figure
    plot.add_glyph(source, polygon, selection_glyph=polygon, nonselection_glyph=polygon)
    # adding reset lasso selected areas on double click/tap
    plot.js_on_event(events.DoubleTap, callback_reset)

    plot.axis.visible = False
    plot.background_fill_color = "#000000"
    plot.background_fill_alpha = 0.8
    plot.grid.grid_line_color = None

    script, div = components(plot)
    return script, div


def store_survey_elements(survey, recom, df_fri, df_frii):
    """Match returned recommentations ids with ObjectCatalog entries

    Parameters
    ----------
    survey: zooniverse_web.models.Survey
    recom: acton.proto.wrappers.Recommendations
    df_fri: pandas.DataFrame
    df_frii: pandas.DataFrame
    """
    #
    for recommendation_id in recom.recommendations:
        try:
            first = df_fri.loc[df_fri['idx'] == recommendation_id, 'first'].item()
        except ValueError:
            first = df_frii.loc[df_frii['idx'] == recommendation_id, 'first'].item()

        # Gather the one question we will use here.
        try:
            galaxy = Galaxy.objects.get(first=first)
        except Galaxy.MultipleObjectsReturned:
            galaxy = Galaxy.objects.filter(first=first)[0]

        question = Question.objects.all()[0]

        # Create survey element
        survey_element, created = SurveyElement.objects.get_or_create(
            galaxy=galaxy,
            question=question,
        )

        # Create survey question for this survey element
        SurveyQuestion.objects.create(survey_element=survey_element, survey=survey)

        save_image(galaxy)


def save_image(galaxy):
    """Check if images are available, if not download and store.

    Parameters
    ----------
    galaxy: zooniverse_web.models.Galaxy
    """
    for database_type in [ImageStore.FIRST, ImageStore.TGSS]:
        try:
            ImageStore.objects.get(galaxy=galaxy, database_type=database_type)
        except ImageStore.DoesNotExist:
            url = construct_tgss_url(ra=galaxy.ra, dec=galaxy.dec) \
                if database_type == ImageStore.TGSS \
                else construct_image_url(ra=galaxy.ra, dec=galaxy.dec, fits=1)

            ImageStore.objects.create(
                galaxy=galaxy,
                database_type=database_type,
                actual_url=url,
            )


def generate_recommendations_for_survey(survey):
    """Generate recommendations for a specific survey

    Parameters
    -----------
    survey: zooniverse_web.models.Survey
    """
    recom, df_fri, df_frii = get_recommendations_from_file('predictions_survey_%d.pb' % survey.id)

    store_survey_elements(survey, recom, df_fri, df_frii)


def generate_new_survey(previous_survey=None):
    """Generate a new survey

    Parameters
    -----------
    previous_survey: zooniverse_web.models.Survey
         Latest survey that a user is acting on, if any.
    """
    # Create a survey
    survey = Survey()
    survey.save()

    # Get FR-I/B FR-II/B labels and train a predictor
    if not previous_survey:
        labels_fr_i, labels_fr_ii = initialise_labels_for_two_predictors()
        pred = predict_and_combine(labels_1=labels_fr_i,
                                   labels_2=labels_fr_ii,
                                   predictor='LogisticRegression',
                                   output_file='predictions_survey_%d.pb' % survey.id)
    else:
        labels_fr_i, labels_fr_ii = get_user_labels_for_two_predictors(previous_survey)
        pred = predict_and_combine(labels_1=labels_fr_i,
                                   labels_2=labels_fr_ii,
                                   predictor='LogisticRegression',
                                   output_file='predictions_survey_%d.pb' % survey.id,
                                   csv_file=CSV_COMBINED_LATEST)

    # Get recommendations from predictor
    recom, df_fri, df_frii = get_recommendations(pred)

    # Store predictions as survey elements
    store_survey_elements(survey, recom, df_fri, df_frii)

    # Set new survey as active
    survey.active = True
    survey.save()

    return survey


def get_next_survey_objects(survey_id, start_index=0, response=None):
    """Returns the next set of questions

    Parameters
    ----------
    survey_id:
        Id of the survey
    start_index:
        index from where the questions will start
    response:
        response object of the database model

    Returns
    -------
    survey_objects:
        list of survey objects
    """
    survey = Survey.objects.get(id=survey_id)

    survey_questions = SurveyQuestion.objects.filter(survey=survey)[
                       start_index:start_index + constants.SURVEY_QUESTIONS_PER_PAGE]

    survey_objects = []

    for survey_question in survey_questions:
        visited = False
        galaxy = survey_question.survey_element.galaxy

        # get question choices
        options = QuestionOption.objects.filter(question=survey_question.survey_element.question)

        choices = []
        default_choice = None
        for option in options:
            choices.append((option.option, option.option))
            if option.is_default_option:
                default_choice = option.option

        # overriding the default with provided answers if any
        try:
            default_choice = QuestionResponse.objects.get(
                response=response,
                survey_question=survey_question,
            ).answer
            visited = True
        except QuestionResponse.DoesNotExist:
            pass

        q = Sq(
            name=constants.FORM_QUESTION_PREFIX + survey_question.id.__str__(),
            label=survey_question.survey_element.question.text,
            choices=tuple(choices),
            initial=default_choice,
            question_type=survey_question.survey_element.question.category,
        )

        # getting images for this survey question
        image_stores = ImageStore.objects.filter(galaxy=galaxy)
        divs = []
        scripts = []
        for index, image_store in enumerate(image_stores):
            try:
                question_drawn_response = QuestionDrawnResponse.objects.get(
                    response=response,
                    survey_question=survey_question,
                    image=image_store,
                )
                x_coordinates = question_drawn_response.x_coordinates
                y_coordinates = question_drawn_response.y_coordinates
                pre_filled = dict(
                    x=x_coordinates.split(',') if x_coordinates.count('NaN') > 0 else [],
                    y=y_coordinates.split(',') if y_coordinates.count('NaN') > 0 else [],
                )
                number_of_objects = question_drawn_response.x_coordinates.count('NaN')
            except QuestionDrawnResponse.DoesNotExist:
                x_coordinates = ''
                y_coordinates = ''
                pre_filled = dict(
                    x=[],
                    y=[],
                )
                number_of_objects = 0

            field_name = constants.FORM_QUESTION_PREFIX + survey_question.id.__str__() \
                         + '_' + image_store.database_type.__str__()
            script, div = get_bokeh_images(
                url=image_store.image.url,
                field_name=field_name,
                pre_filled=pre_filled,
            )
            divs.append(
                [
                    div,
                    field_name,
                    number_of_objects,
                    x_coordinates,
                    y_coordinates,
                ]
            )
            scripts.append(script)

        survey_objects.append(ClassifyObject(
            questions=[q],
            divs=divs,
            scripts=scripts,
            visited=visited,
        ))

    return survey_objects


def save_answers(request, response):
    """Save user's answers

    Parameters
    ----------
    request:
    response:
    """
    # pattern for questions
    pattern_1 = constants.FORM_QUESTION_PREFIX + '\d+$'
    # pattern for image selected areas
    pattern_2 = constants.FORM_QUESTION_PREFIX + '\d+_[a-zA-Z0-9_]+$'

    for key in request.POST:
        if re.match(pattern_1, key):
            answer = request.POST[key]
            survey_question = SurveyQuestion.objects.get(id=key.replace(constants.FORM_QUESTION_PREFIX, ''))

            QuestionResponse.objects.update_or_create(
                survey_question=survey_question,
                response=response,
                defaults={
                    'answer': answer,
                }
            )
        elif re.match(pattern_2, key):
            # save answers for selected areas
            # finding id of the survey question
            split_content = key.replace(constants.FORM_QUESTION_PREFIX, '').split('_')
            survey_question_id = split_content[0]
            image_database_type = split_content[1]
            coordinate = split_content[-1]

            survey_question = SurveyQuestion.objects.get(id=survey_question_id)
            # updating the answer
            if coordinate == 'x':
                QuestionDrawnResponse.objects.update_or_create(
                    survey_question=survey_question,
                    response=response,
                    image=ImageStore.objects.get(
                        galaxy=survey_question.survey_element.galaxy,
                        database_type=image_database_type,
                    ),
                    defaults={
                        'x_coordinates': request.POST[key],
                    }
                )
            elif coordinate == 'y':
                QuestionDrawnResponse.objects.update_or_create(
                    survey_question=survey_question,
                    response=response,
                    image=ImageStore.objects.get(
                        galaxy=survey_question.survey_element.galaxy,
                        database_type=image_database_type,
                    ),
                    defaults={
                        'y_coordinates': request.POST[key],
                    }
                )
