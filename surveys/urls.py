from django.conf.urls import patterns, url

urlpatterns = patterns('surveys.views',
    url(r'^$', 'index'),
    url(r'^(?P<survey_id>\d+)/$', 'detail', {'slug': 'default'}),
    url(r'^list/(?P<survey_id>\d+)/$', 'list'),
    url(r'^(?P<survey_id>\d+)/question/(?P<question_id>\d+)/$', 'question'),
    url(r'^(?P<survey_id>\d+)/results/$', 'results'),
    url(r'^(?P<survey_id>\d+)/vote/$', 'vote'),
    url(r'^create/$', 'create'),
    url(r'^(?P<survey_id>\d+)/participate/$', 'participate'),
    url(r'^(?P<survey_id>\d+)/edit/$', 'edit'),
    url(r'^(?P<survey_id>\d+)/(?P<slug>[-\w]+)/$', 'detail'),
)
