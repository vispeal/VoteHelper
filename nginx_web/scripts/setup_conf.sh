#!/bin/bash
#
# This scripts is used to setup the configuration for the application.
#
#
# Author : chzhong 
#

CONFIG_FILE=dzone.nginx
IAC_FILE=iac.nginx
GLOBAL_FILE=nginx.conf
LOG_ROTATE_FILE=track.logrotate
BASE_CONFIG=/etc/nginx/
ENABLE_CONFIG=/etc/nginx/sites-enabled
LOG_ROTATE_DIR=/etc/logrotate.d/
REMOVE_CONFIG=( ${ENABLE_CONFIG}/default )

cp -lf ${CONFIG_FILE} ${ENABLE_CONFIG}/dzone

if [ -f "${GLOBAL_FILE}" ] ; then
    cp -f ${GLOBAL_FILE} ${BASE_CONFIG}/
fi

for remove_conf in ${REMOVE_CONFIG[@]};do
    if [ -f "${remove_conf}" ] ; then
        rm "${remove_conf}"
    fi
done
