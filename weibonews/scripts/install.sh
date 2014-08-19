#!/bin/bash
#
# This scripts is used for installing project.
# This scripts is required for all projects.
#
#
# Author : chzhong 
#


SCRIPT_DIR=`dirname $0`

if [ "$1" = "checkdeps" ] ; then

    if [ -f "${SCRIPT_DIR}/install_deps.sh" ]; then
        ${SCRIPT_DIR}/install_deps.sh
    fi
fi 

python setup.py -q build

PTH_FILE='weibonews.pth'
if [ "$2" = "lib" ] ; then
    sudo python setup.py -q install
else
    pwd > ${PTH_FILE}
    sudo python scripts/install.py
fi
