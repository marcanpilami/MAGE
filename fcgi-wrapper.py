#!c:/python25/python.exe
# -*- coding: utf-8 -*-

debug = False

##########################
## Python imports
import sys, os
try:
  import fastcgi
except:
  print u'Il faut installer le wrapper FCGI'
  sys.exit(1)


##########################
## Setup Django envt
sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0])) + "\\..")
os.environ['DJANGO_SETTINGS_MODULE'] = "MAGE.settings"
os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
from django.core.handlers.wsgi import WSGIHandler


##########################
## Debug FCGI log
if debug:
    f=open('C:\FCGI.log', 'w')
    f.write('debut script\n\n')
    f.flush()


##########################
## Appli
def myapp(environ, start_response):
    if debug:
        f.write('script 2\n\n')
        f.flush()
    
    #start_response('200 OK', [('Content-Type', 'text/html; charset=UTF-8'), ('Pragma', 'no-cache')])
    handler = WSGIHandler()
    
    if debug:
        f.write('script 3\n\n')
        f.flush()
    #return ['<html><head><title>TEST FCGI</title></head><body><h1>TEST OK 3 !</h1></body></html>\n\n']
    return handler(environ, start_response)


##########################
## Main
if __name__ == '__main__':    
    s = fastcgi.ThreadedWSGIServer(myapp, workers=1)
    s.serve_forever()

if debug:
    f.write('fin script\n')
    f.close()