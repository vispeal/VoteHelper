#!/bin/bash
#
# Webzine gevent Web Server init script
# 
### BEGIN INIT INFO
# Provides:          webzine-web
# Required-Start:    $remote_fs $remote_fs $network $syslog
# Required-Stop:     $remote_fs $remote_fs $network $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start Webzine gevent Web Server at boot time
# Description:       Wenzine gevent Web Server provides web server backend.
### END INIT INFO

PARENT=weibonews
PROJECT=wechat
DESC="Wechat Service"
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/var/app/$PARENT/enabled/$PROJECT
NAME=$PARENT-$PROJECT
PID_FILE=/var/run/$NAME.pid
DAEMON=/usr/local/bin/gevent

if [ -f /etc/default/$PROJECT ]; then
	. /etc/default/$PROJECT
fi

function stop_service()
{
	if [ -f "${PID_FILE}" ]; then
        pushd /var/app/$PARENT/enabled/$PROJECT/
        python run.py stop
        popd
        echo "${DESC}(pid ${PID}) stopped itself."
    fi
	if [ -f "${PID_FILE}" ]; then
        export PID=`cat ${PID_FILE}`
        rm "${PID_FILE}"
        kill -INT ${PID}
        echo "${DESC}(pid ${PID}) stopped."
    else
        echo "${PROJECT} stop/waiting."
	fi
}

function start_service()
{
    pushd /var/app/$PARENT/enabled/$PROJECT/
    python run.py start
    popd
}

function restart_service()
{
    pushd /var/app/$PARENT/enabled/$PROJECT/
    python run.py restart
    popd
}

set -e

. /lib/lsb/init-functions

case "$1" in
	start)
		echo "Starting $DESC..."
		start_service
		echo "Done."
		;;
	stop)
		echo "Stopping $DESC..."
		stop_service
		echo "Done."
		;;

	restart)
		echo "Restarting $DESC..."
		stop_service
		start_service
		echo "Done."
		;;
	status)
		status_of_proc -p /var/run/$NAME.pid "$DAEMON" gevent && exit 0 || exit $?
		;;
	*)
		echo "Usage: $NAME {start|stop|restart|status}" >&2
		exit 1
		;;
esac

exit 0

