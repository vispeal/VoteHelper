#!/usr/bin/python
from weibonews.utils.daemon import Daemon
import sys
from geventrun import runwsgi
import logging

_LOG_FILE = '/var/app/weibonews/log/wechat/error.log'

class wechatdaemon(Daemon):
    '''
    Subclass or daemon to run specific service
    '''
    def run(self):
        try:
            runwsgi()
        except TypeError, err:
            logger = initlog(_LOG_FILE)
            logger.exception('RunWsgi failed with exception : %s' % err)
        except Exception, err:
            logger = initlog(_LOG_FILE)
            logger.exception('RunWsgi failed with exception : %s' % err)

def initlog(logfile):
    '''
    Setup logger to log start daemon error
    '''
    logger = logging.getLogger('')
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger


def main():
    '''
    Control service
    '''
    daemon = wechatdaemon('/var/run/weibonews-wechat.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

if __name__ == "__main__":
    main()
