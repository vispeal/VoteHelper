#!/usr/bin/env python
# coding: utf-8
"""
Created On Nov 29, 2013

@Author : Jun Wang
"""
import os
import logging
import subprocess

_LOGGER = logging.getLogger('weibonews.wechat')

def upload_by_scp(hosts, user, key_file, local, remote):
    '''
    scp file to remote host
    '''
    remote_dir = os.path.dirname(remote)
    servers = ['%s@%s' % (user, ip) for ip in hosts]
    for server in servers:
        scp_file = 'scp -i %s %s %s:%s' % (key_file, local, server, remote)
        _LOGGER.info(scp_file)
        result = subprocess.call(scp_file, shell=True)
        if result != 0:
            mkdir = 'ssh -i %s %s "mkdir -p %s"' % (key_file, server, remote_dir)
            dir_result = subprocess.call(mkdir, shell=True)
            if dir_result != 0:
                _LOGGER.error(dir_result)
                return False
            result = subprocess.call(scp_file, shell=True)
        _LOGGER.info('%s result: %s' % (scp_file, result))
        if result != 0:
            return False
    return True
