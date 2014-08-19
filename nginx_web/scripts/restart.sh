#!/bin/bash
#
# This scripts is used to restart the application.
# This scripts is required for all projects.
#
#
# Author : chzhong 
#

if [ -f "/var/run/nginx.pid" ]; then
	sudo service nginx reload
else
	sudo service nginx start
fi

