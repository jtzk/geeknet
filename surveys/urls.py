from django.conf.urls import patterns, url

urlpatterns = patterns('surveys.views',
    url(r'^$', 'index'),
    url(r'^(?P<survey_id>\d+)/$', 'detail'),
    url(r'^(?P<survey_id>\d+)/question/(?P<question_id>\d+)/$', 'question'),
    url(r'^(?P<survey_id>\d+)/results/$', 'results'),
    url(r'^(?P<survey_id>\d+)/vote/$', 'vote'),
)
