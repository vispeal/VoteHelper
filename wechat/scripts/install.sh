#!/bin/bash
#
# This scripts is used to install the application.
# This scripts is required for all projects.
#
#
# Author : chzhong 
#

python setup.py -q build

SCRIPT_DIR=`dirname $0`
PARENT=weibonews
PROJECT=wechat

if [ "$1" = "checkdeps" ] ; then

    if [ -f "${SCRIPT_DIR}/install_deps.sh" ]; then
        ${SCRIPT_DIR}/install_deps.sh
    fi
fi

if [ -f "${SCRIPT_DIR}/setup_conf.sh" ]; then
    ${SCRIPT_DIR}/setup_conf.sh
fi

PTH_FILE="${PARENT}-${PROJECT}.pth"
if [ "$2" = "lib" ] ; then
    sudo python setup.py -q install
else
    pwd > ${PTH_FILE}
    sudo python scripts/install.py
fi

echo Installing service...
[ -z `grep "^$PARENT:" /etc/passwd` ] && sudo useradd -r $PARENT -M -N

chmod -R a+rw /var/app/$PARENT/data/$PROJECT
chmod -R a+rw /var/app/$PARENT/log/$PROJECT
chown $PARENT:nogroup /var/app/$PARENT/data/$PROJECT
chown $PARENT:nogroup /var/app/$PARENT/log/$PROJECT
mkdir -p -m a+rw /var/app/$PARENT/data/$PROJECT/log

ln -sf /var/app/$PARENT/enabled/$PROJECT/scripts/project-init.sh /etc/init.d/$PARENT-$PROJECT
update-rc.d $PARENT-$PROJECT defaults
