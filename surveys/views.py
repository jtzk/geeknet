from django.shortcuts import render_to_response, get_object_or_404
from surveys.models import Survey
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext

def index(request):
    latest_survey_list = Survey.objects.all().order_by('-pub_date')[:5]
    return render_to_response('surveys/index.html', {'latest_survey_list': latest_survey_list})

def detail(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)
    return render_to_response('surveys/detail.html', {'survey': s}, context_instance=RequestContext(request))

def list(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)
    return render_to_response('surveys/list.html', {'survey': s})

def question(request, survey_id, question_id):
    s = get_object_or_404(Survey, pk=survey_id)
    q = s.question_set.get(pk=question_id)

    prev = s.question_set.order_by('-id').filter(id__lt=question_id)[0:1]
    if prev.count():
        q.prev = prev[0]
    else:
        q.prev = 0

    next = s.question_set.filter(id__gt=question_id)[0:1]
    if next.count():
        q.next = next[0]
    else:
        q.next = 0

    return render_to_response('surveys/question.html', {'survey': s, 'question': q}, context_instance=RequestContext(request))

def results(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)
    return render_to_response('surveys/results.html', {'survey': s})

def vote(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)

    if request.method == 'POST':
        for k, v in request.POST.items():
            if k.startswith("question"):
                k, pk = k.split('-')
                q = s.question_set.get(pk=pk)
                c = q.choice_set.get(pk=v)
                c.votes += 1
                c.save()

    return HttpResponseRedirect(reverse('surveys.views.results', args=(s.id,)))