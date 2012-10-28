from django.shortcuts import render_to_response
from django.template import RequestContext

def about(request):
    return render_to_response('about.html' , RequestContext(request))

def contact(request):
    return render_to_response('contact.html' , RequestContext(request))
