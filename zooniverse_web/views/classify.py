from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from zooniverse_web.models import (
    Survey, SurveyQuestion, Response
)
from zooniverse_web.utility import constants
from zooniverse_web.utility.plots import get_plots
from zooniverse_web.utility.survey import (
    get_next_survey_objects, save_answers, generate_new_survey, generate_recommendations_for_survey
)


@login_required
def classify(request):

    # fixing the object index for pagination
    if request.method != 'POST':
        start_index = 0

        try:
            # setting the survey to the latest
            # need to work if retrieves old classification jobs (paused jobs)
            request.session['survey_id'] = Survey.objects.filter(active=True).order_by('-creation_date').first().id
            survey = Survey.objects.get(id=request.session['survey_id'])
        except AttributeError:
            # Create prediction w/ Acton and create new survey
            survey = generate_new_survey()

        try:
            response = Response.objects.get(
                user=request.user,
                survey=survey,
            )
        except Response.DoesNotExist:
            response = None
    else:
        start_index = request.POST.get('start_index')
        survey = Survey.objects.get(id=request.session['survey_id'])
        # create a new response if it is not there
        response, created = Response.objects.get_or_create(
            user=request.user,
            survey=survey,
        )

        next_action = request.POST.get('next_action', None)

        if not next_action:  # have come from original_page
            from_page = 'original'
            next_action = request.POST.get('submit', None)
        else:
            from_page = 'intermediate'

        if next_action == 'Back':
            start_index = max(int(start_index) - constants.SURVEY_QUESTIONS_PER_PAGE, 0)
        else:
            # checking out for available latest surveys
            if from_page != 'intermediate':  # do not check it if coming from intermediate page
                # saving the answers for the questions
                save_answers(request, response)

                latest_survey = Survey.objects.filter(active=True).order_by('-creation_date').first()

                # checking if this is the last page
                if next_action == 'Finish':
                    # setting the survey as finished
                    response.status = Response.FINISHED
                    response.save()

                    # redirecting to thank you page
                    return render(
                        request,
                        'classify/completed.html',
                        {
                            'user': request.user,
                            'latest_survey': latest_survey,
                        }
                    )

                if latest_survey.id != request.session['survey_id']:
                    # bring up the intermediate page
                    return render(
                        request,
                        'classify/intermediate.html',
                        {
                            'next_action': next_action,
                            'latest_survey': latest_survey,
                            'start_index': start_index,
                        }
                    )
            else:
                # mark the current survey as finished
                response.status = Response.FINISHED
                response.save()

                # redirect to the classify page
                if request.POST.get('submit', None) == 'Latest':
                    return redirect(reverse('classify'))

            # update the start index
            start_index = int(start_index) + constants.SURVEY_QUESTIONS_PER_PAGE

        if next_action == 'More!':
            generate_recommendations_for_survey(survey)

    survey_objects = get_next_survey_objects(
        survey_id=request.session['survey_id'],
        start_index=start_index,
        response=response,
    )

    # setting the text for the forward button
    submit_text = 'Save and Next'
    total = SurveyQuestion.objects.filter(survey=survey).count()

    if start_index + constants.SURVEY_QUESTIONS_PER_PAGE >= total:
        submit_text = 'Finish'

    plots = get_plots(request)

    return render(
        request,
        'classify/classify.html',
        {
            'rows': survey_objects,
            'plots': plots,
            'start_index': start_index,
            'submit_text': submit_text,
            'first_page': True if start_index == 0 else False,
        }
    )
