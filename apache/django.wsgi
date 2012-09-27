import os, sys  
  
sys.path.append('C:/Documents and Settings/Jarryd/Desktop/djangoTest/testproject/')  
  
  
os.environ['DJANGO_SETTINGS_MODULE'] = 'testproject.settings'  
  
  
import django.core.handlers.wsgi  
  
  
application = django.core.handlers.wsgi.WSGIHandler()  