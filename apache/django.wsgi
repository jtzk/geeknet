import os, sys  
  
sys.path.append('C:/Documents and Settings/Jarryd/Desktop/geeknet/')  
  
  
os.environ['DJANGO_SETTINGS_MODULE'] = 'geeknet.settings'  
  
  
import django.core.handlers.wsgi  
  
  
application = django.core.handlers.wsgi.WSGIHandler()  