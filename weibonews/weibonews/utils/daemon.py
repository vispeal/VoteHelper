'''
    ***
    Modified generic daemon class
    ***

    Author:     http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
                www.boxedice.com

    License:     http://creativecommons.org/licenses/by-sa/3.0/

    Changes:    23rd Jan 2009 (David Mytton <david@boxedice.com>)
                - Replaced hard coded '/dev/null in __init__ with os.devnull
                - Added OS check to conditionally remove code that doesn't work on OS X
                - Added output to console on completion
                - Tidied up formatting
                11th Mar 2009 (David Mytton <david@boxedice.com>)
                - Fixed problem with daemon exiting on Python 2.4 (before SystemExit was part of the Exception base)
                13th Aug 2010 (David Mytton <david@boxedice.com>
                - Fixed unhandled exception if PID file is empty
'''

# Core modules
import atexit
import os
import sys
import time

from signal import SIGTERM

class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.mp_mode = False

    def daemonize(self):
        """
        Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError, err:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (err.errno, err.strerror))
            sys.exit(1)

        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent
                sys.exit(0)
        except OSError, err:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (err.errno, err.strerror))
            sys.exit(1)

        if sys.platform != 'darwin': # This block breaks on OS X and linux
            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            stdi = file(self.stdin, 'r')
            stdo = file(self.stdout, 'a+')
            stde = file(self.stderr, 'a+', 0)
            os.dup2(stdi.fileno(), sys.stdin.fileno())
            os.dup2(stdo.fileno(), sys.stdout.fileno())
            os.dup2(stde.fileno(), sys.stderr.fileno())

        print "Started"

        # Write pidfile
        if not self.mp_mode:
            atexit.register(self.delpid) # Make sure pid file is removed if we quit
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def delpid(self):
        '''
        Delete pid file
        '''
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """

        print "Starting..."

        # Check for a pidfile to see if the daemon already runs
        try:
            pid_file = file(self.pidfile,'r')
            pid = int(pid_file.read().strip())
            pid_file.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None

        if pid:
            message = "pidfile %s already exists. Is it already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """

        print "Stopping..."

        self.release()

        # Get the pid from the pidfile
        try:
            pid_file = file(self.pidfile,'r')
            pid = int(pid_file.read().strip())
            pid_file.close()
        except IOError:
            pid = None
        except ValueError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Not running?\n"
            sys.stderr.write(message % self.pidfile)

            # Just to be sure. A ValueError might occur if the PID file is empty but does actually exist
            self.delpid()

            return # Not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

        print "Stopped"

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
        pass

    def release(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by stop() or restart().
        """
        pass

def daemon_main(daemon_type, pid_file, argv):
    '''
    Control daemon service
    '''
    daemon = daemon_type(pid_file)
    if len(argv) == 2:
        if 'start' == argv[1]:
            daemon.start()
        elif 'stop' == argv[1]:
            daemon.stop()
        elif 'restart' == argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % argv[0]
        sys.exit(2)
