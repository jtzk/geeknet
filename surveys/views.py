import datetime, dateutil.parser
from django.utils import timezone
from django.shortcuts import render_to_response, get_object_or_404
from surveys.models import Survey, Choice, Question, Surveyee
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db.models import Count, Q
from surveys.forms import SurveyCreationForm, SearchForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from surveys.search import IssueSearch

def index(request):

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            searchResults = search(form.cleaned_data , request)
            if searchResults:
                return render_to_response('surveys/index.html', {'survey_list': searchResults, 'view_id': 10, 'form':form}, RequestContext(request))
            else:
                return render_to_response('surveys/index.html', {'survey_list': None, 'view_id': 10, 'form':form}, RequestContext(request))


    else:
        form = SearchForm

    view_id = 0

    if request.GET.get('view') != None:
        if request.GET.get('view').isdigit():
            view_id = int(request.GET.get('view'))

    latest_survey_list = Survey.objects.all().filter(status=Survey.STATUS_PUBLISHED).filter(endtime__gt=timezone.now()).order_by('-starttime')[:5]
    popular_survey_list = Survey.objects.filter(status=Survey.STATUS_PUBLISHED).filter(endtime__gt=timezone.now()).annotate(surveyParticipants=Count('surveyee')).order_by('-surveyParticipants').filter(surveyParticipants__gte=1)[:5]
    all_survey_list = Survey.objects.filter(status=Survey.STATUS_PUBLISHED).filter(endtime__gt=timezone.now()).order_by('id')
    active_survey_list = Survey.objects.filter(status=Survey.STATUS_ACTIVE).order_by('id')
    deleted_survey_list = Survey.objects.filter(status=Survey.STATUS_INACTIVE)
    recently_ended_survey_list = Survey.objects.filter(Q(status=Survey.STATUS_ENDED) | Q(endtime__lte=timezone.now())).order_by('-endtime').exclude(status=Survey.STATUS_INACTIVE)[:5]

    if request.user.is_staff:
        if view_id == 5:
            return render_to_response('surveys/index.html', {'survey_list': active_survey_list, 'view_id': view_id, 'form':form}, RequestContext(request))
        elif view_id == 6:
            return render_to_response('surveys/index.html', {'survey_list': deleted_survey_list, 'view_id': view_id, 'form':form}, RequestContext(request))

    if view_id == 2:
        return render_to_response('surveys/index.html', {'survey_list': popular_survey_list, 'view_id': view_id, 'form':form}, RequestContext(request))
    elif view_id == 3:
        return render_to_response('surveys/index.html', {'survey_list': all_survey_list, 'view_id': view_id, 'form':form}, RequestContext(request))
    elif view_id == 4:
        return render_to_response('surveys/index.html', {'survey_list': recently_ended_survey_list, 'view_id': view_id, 'form':form}, RequestContext(request))
    else:
        return render_to_response('surveys/index.html', {'survey_list': latest_survey_list, 'view_id': 1 , 'form':form}, RequestContext(request))


def detail(request, survey_id, slug):
    s = get_object_or_404(Survey, pk=survey_id)
    if request.method == "POST":
        if "participate" in request.POST:
            # get id of first question in survey

            q = s.question_set.all()[:1]
            if q:
                q = q[0]

            # Create surveyee
            # registered user surveyee
            if request.user.is_authenticated():
                surveyee = s.surveyee_set.create(question=q, user=request.user, ip=get_client_ip(request))

            # anonymous surveyee
            else:
                surveyee = s.surveyee_set.create(question=q, user=User.objects.get(pk=0), ip=get_client_ip(request))

            # store to session
            if "surveys" not in request.session:
                request.session["surveys"] = {}
            request.session["surveys"][s.id] = surveyee.id
            request.session.modified = True

            return HttpResponseRedirect(reverse('surveys.views.question', args=(s.id, q.id,)))
    if slug == "default":
        return HttpResponseRedirect(reverse('surveys.views.detail', args=(s.id, s.slug)))
    if s.endtime is not None:
        if s.status != s.STATUS_ENDED and s.endtime <= timezone.now():
            s.status = s.STATUS_ENDED
            s.save()
    if "surveys" in request.session:
        if s.id in request.session["surveys"]:
            try:
                surveyee = s.surveyee_set.get(pk=request.session["surveys"][s.id], endtime=None)
            except Surveyee.DoesNotExist:
                del request.session["surveys"][s.id]
                return render_to_response('surveys/detail.html', {'survey': s,}, context_instance=RequestContext(request))

            nextquestion = surveyee.question

            return render_to_response('surveys/detail.html', {'survey': s, 'nextquestion': nextquestion}, context_instance=RequestContext(request))
    return render_to_response('surveys/detail.html', {'survey': s,}, context_instance=RequestContext(request))

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def list(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)

    if request.method == "POST":
        if "participate" in request.POST:
            # get id of first question in survey
            q = s.question_set.all()[:1]
            if q:
                q = q[0]

            # Create surveyee
            # registered user surveyee
            if request.user.is_authenticated():
                surveyee = s.surveyee_set.create(question=q, user=request.user, ip=get_client_ip(request))

            # anonymous surveyee
            else:
                surveyee = s.surveyee_set.create(question=q, user=User.objects.get(pk=0), ip=get_client_ip(request))

            # store to session
            if "surveys" not in request.session:
                request.session["surveys"] = {}
            request.session["surveys"][s.id] = surveyee.id
            request.session.modified = True

            return HttpResponseRedirect(reverse('surveys.views.question', args=(s.id, q.id,)))

    return render_to_response('surveys/list.html', {'survey': s }, RequestContext(request))

def question(request, survey_id, question_id):
    s = get_object_or_404(Survey, pk=survey_id)
    if "surveys" in request.session:
        if s.id in request.session["surveys"]:

            q = s.question_set.get(pk=question_id)

            try:
                surveyee = s.surveyee_set.get(pk=request.session["surveys"][s.id], endtime=None)
            except Surveyee.DoesNotExist:
                return HttpResponseRedirect(reverse('surveys.views.detail', args=(s.id, s.slug)))

            surveyee.question = q
            surveyee.save()

            for question in s.question_set.all():
                if question.id == q.id:
                    break
                else:
                    q.number += 1

            progress = 100 * q.number / s.numQuestions

            return render_to_response('surveys/question.html', {'survey': s, 'question': q , 'progress': progress}, context_instance=RequestContext(request))

    return HttpResponseRedirect(reverse('surveys.views.detail', args=(s.id, s.slug)))

def results(request, survey_id):

    view_id = 0;
    show_ip = 0;

    if request.GET.get('view') != None:
        if request.GET.get('view').isdigit():
            view_id = int(request.GET.get('view'))

    if request.GET.get('ip') != None:
        if request.GET.get('ip').isdigit():
            show_ip = int(request.GET.get('ip'))

    s = get_object_or_404(Survey, pk=survey_id)
    if not s.status == s.STATUS_ACTIVE and not s.status == s.STATUS_INACTIVE:
        if request.user.is_staff or s.resultDisplay == s.RESULTS_PUBLIC or (s.resultDisplay == s.RESULTS_USER and request.user.is_authenticated()) or (s.resultDisplay == s.RESULTS_PRIVATE and request.user == s.owner):
            statistics = s.results()
            return render_to_response('surveys/results/results.html', {'survey': s, 'statistics': statistics, 'view_id': view_id, 'show_ip': show_ip}, RequestContext(request))
        else:
            return render_to_response('surveys/results/error.html', {'survey': s,})

    return HttpResponseRedirect(reverse('surveys.views.index'))

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
                elif q.type == q.TYPE_TEXTBOX or q.type == q.TYPE_TEXTAREA:
                    a = q.answer_set.create(question=q, value=v)
                    a.save()

        if request.POST.get('nextquestion'):
            return HttpResponseRedirect(reverse('surveys.views.question', args=(s.id, int(request.POST.get("nextquestion")))))

    if request.session.get("surveys"):
        if request.session["surveys"].get(s.id):
            surveyee = s.surveyee_set.get(pk=request.session["surveys"].get(s.id))
            surveyee.end()
            if request.session["surveys"][s.id]:
                del request.session["surveys"][s.id]

    return HttpResponseRedirect(reverse('surveys.views.results', args=(s.id,)))

@login_required
def create(request):
    if request.user.is_authenticated() and request.method == "POST":
        form = SurveyCreationForm(request.POST)
        if form.is_valid():
            new_survey = form.save(commit=False)
            new_survey.owner = request.user
            new_survey.save()
            return HttpResponseRedirect(reverse('surveys.views.edit', args=(new_survey.id,)))
    else:
        form = SurveyCreationForm()
    return render_to_response('surveys/create.html', {'form': form,}, context_instance=RequestContext(request))

@login_required
def edit(request, survey_id):
    s = get_object_or_404(Survey, pk=survey_id)
    # only admins and survey owner can view this page
    if request.user.is_staff or (request.user.is_authenticated() and s.owner == request.user):
        if request.method == "POST":
            # editing is only allowed when survey status is 'ACTIVE'
            if s.status == s.STATUS_ACTIVE:
                errors = {}
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
                        if v and v != "Add new choice":
                            c.choice = v
                            c.save()
                        else:
                            c.delete()
                    elif k.startswith("newChoice"):
                        k, pk = k.split('-')
                        if v and v != "Add new choice" and v != "":
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
                            q.type = int(request.POST["newQuestionType"])
                        else:
                            q.type = 1
                        q.save()
                if 'publish' in request.POST:
                    if s.question_set.all().count() == 0:
                        errors['publishError'] = "You cannot publish an empty survey. Create some questions first."
                        return render_to_response('surveys/edit/edit.html', {'survey': s, 'today':datetime.datetime.now(), 'tomorrow': datetime.datetime.now() + datetime.timedelta(days=1), 'errors': errors}, context_instance=RequestContext(request))
                    if 'resultDisplay' in request.POST and 'endtime' in request.POST:
                        if not s.publish(resultDisplay=request.POST["resultDisplay"], endtime=dateutil.parser.parse(request.POST["endtime"], dayfirst=True)):
                            return HttpResponseRedirect(reverse('surveys.views.edit', args=(s.id,)))
            # actions for published surveys
            elif s.status == s.STATUS_PUBLISHED:
                if "end" in request.POST:
                    ACTION_CONFIRM = 0
                    ACTION_END = 1
                    if "confirm" in request.POST:
                        s.end()
                        return render_to_response('surveys/edit/end.html', {'survey': s, 'action': ACTION_END}, context_instance=RequestContext(request))
                    if "negative" in request.POST:
                        return HttpResponseRedirect(reverse('surveys.views.edit', args=(s.id,)))
                    else:
                        return render_to_response('surveys/edit/end.html', {'survey': s, 'action': ACTION_CONFIRM}, context_instance=RequestContext(request))
                if "unpublish" in request.POST:
                    if request.user.is_staff:
                        s.status = s.STATUS_ACTIVE
                        s.save()
            elif s.status == s.STATUS_INACTIVE:
                if "undelete" in request.POST:
                    if request.user.is_staff:
                        s.status = s.STATUS_ACTIVE
                        s.save()
            if not s.status == s.STATUS_INACTIVE:
                if "delete" in request.POST:
                    if request.user.is_staff:
                        s.status = s.STATUS_INACTIVE
                        s.save()

            if "ban" in request.POST:
                if request.user.is_staff:
                    s.owner.is_active = False
                    s.owner.save()

            elif "unban" in request.POST:
                if request.user.is_staff:
                    s.owner.is_active = True
                    s.owner.save()


            return HttpResponseRedirect(reverse('surveys.views.edit', args=(s.id,)))
        return render_to_response('surveys/edit/edit.html', {'survey': s, 'today':datetime.datetime.now(), 'tomorrow': datetime.datetime.now() + datetime.timedelta(days=1)}, context_instance=RequestContext(request))
    else:
        return render_to_response('surveys/edit/error.html', {'survey': s,})

def search(search_data, request):
    q = Q()
    searchResults = None
    searcher = IssueSearch(search_data)

    for key in search_data.iterkeys():
        dispatch = getattr(searcher, 'search_%s' % key)
        q = dispatch(q)
        print q

    if q and len(q):
        if request.user.is_staff:
            searchResults = Survey.objects.filter(q).select_related().order_by('-title')
        else:
            searchResults = Survey.objects.filter(q).select_related().exclude(status=Survey.STATUS_INACTIVE).exclude(status=Survey.STATUS_ACTIVE).order_by('-title')

        print searchResults
    else:
        searchResults = []
    return searchResults