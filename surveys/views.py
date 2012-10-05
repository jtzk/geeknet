from django.shortcuts import render_to_response, get_object_or_404
from surveys.models import Survey, Choice, Question
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db.models import Sum
from surveys.forms import SurveyCreationForm

def index(request):
    latest_survey_list = Survey.objects.all().order_by('-pub_date')[:5]
    popular_survey_list = Survey.objects.annotate(tvotes=Sum('question__choice__votes')).order_by('-tvotes').filter(tvotes__gt=1)[:5]
    all_survey_list = Survey.objects.order_by('id')
    return render_to_response('surveys/index.html', {'all_survey_list': all_survey_list, 'latest_survey_list': latest_survey_list, 'popular_survey_list': popular_survey_list})

def detail(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)
    q = s.question_set.all()[:1]
    if q:
        q = q[0]
    return render_to_response('surveys/question.html', {'survey': s, 'question': q}, context_instance=RequestContext(request))

def list(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)
    return render_to_response('surveys/list.html', {'survey': s})

def question(request, survey_id, question_id):
    s = get_object_or_404(Survey, pk=survey_id)
    q = s.question_set.get(pk=question_id)

    for question in s.question_set.all():
        if question.id == q.id:
            break
        else:
            q.number += 1

    return render_to_response('surveys/question.html', {'survey': s, 'question': q}, context_instance=RequestContext(request))

def results(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)
    statistics = s.results()
    return render_to_response('surveys/results.html', {'survey': s, 'statistics': statistics})

def vote(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)
    if request.method == 'POST':
        for k, v in request.POST.items():
            if k.startswith("question"):
                sk, pk = k.split('-')
                q = s.question_set.get(pk=pk)
                if q.type == q.TYPE_RADIO:
                    c = q.choice_set.get(pk=v)
                    c.votes += 1
                    c.save()
                elif q.type == q.TYPE_CHECKBOX:
                    for pk in request.POST.getlist(k):
                        c = q.choice_set.get(pk=pk)
                        c.votes += 1
                        c.save()

        if (request.POST.get("nextquestion")):
            return HttpResponseRedirect(reverse('surveys.views.question', args=(s.id, int(request.POST.get("nextquestion")))))

    return HttpResponseRedirect(reverse('surveys.views.results', args=(s.id,)))

def create(request):
    if request.method == "POST":
        form = SurveyCreationForm(request.POST)
        if form.is_valid():
            new_survey = form.save()
            return HttpResponseRedirect(reverse('surveys.views.edit', args=(new_survey.id,)))
    else:
        form = SurveyCreationForm()
    return render_to_response('surveys/create.html', {'form': form,}, context_instance=RequestContext(request))

def edit(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)
    if request.method == "POST":
        for k, v in request.POST.items():
            if k.startswith("surveyTitle"):
                s.title = v
                s.save()
            elif k.startswith("questionName"):
                k, pk = k.split('-')
                q = s.question_set.get(pk=pk)
                q.question = v
                q.save()
            elif k.startswith("questionType"):
                k, pk = k.split('-')
                q = s.question_set.get(pk=pk)
                q.type = int(v)
                q.save()
            elif k.startswith("choice"):
                k, pk = k.split('-')
                c = Choice.objects.get(pk=pk)
                if v:
                    c.choice = v
                    c.save()
                else:
                    c.delete()
            elif k.startswith("newChoice"):
                k, pk = k.split('-')
                if v and v != "Add new choice":
                    q = s.question_set.get(pk=pk)
                    c = Choice()
                    c.question = q
                    c.choice = v
                    c.votes = 0
                    c.save()
            elif k == "newQuestion" and v and v != "Enter a new question":
                q = Question()
                q.survey = s
                q.question = v
                if request.POST["newQuestionType"]:
                    # TODO: sterilize this
                    q.type = int(request.POST["newQuestionType"])
                else:
                    q.type = 1
                q.save()
        return HttpResponseRedirect(reverse('surveys.views.edit', args=(s.id,)))
    return render_to_response('surveys/edit.html', {'survey': s}, context_instance=RequestContext(request))