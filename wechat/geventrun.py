from gevent import monkey
monkey.patch_all()
from gevent.wsgi import WSGIServer
import sys
import os
import traceback
from django.core.handlers.wsgi import WSGIHandler
#from django.core.management import call_command
from django.core.signals import got_request_exception

def exception_printer(sender, **kwargs):
    traceback.print_exc()

def runwsgi():
    sys.path.append('/var/app/weibonews/enabled/wechat/')
    sys.path.append('/var/app/weibonews/enabled/wechat/wechat')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'wechat.settings'
    got_request_exception.connect(exception_printer)
    WSGIServer(('', 8088), WSGIHandler()).serve_forever()

if __name__ == "__main__":
    runwsgi()

