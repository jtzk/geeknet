from django.conf.urls import patterns, include, url
from django.contrib import admin
from geeknet.views import about, contact, resulttest

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'surveys.views.index'),
    url(r'^surveys/', include('surveys.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^about/', about, name='about'),
    url(r'^contact/', contact, name='contact'),
    url(r'^test/', resulttest, name='contact'),
    url(r'^admin/', include(admin.site.urls)),
)