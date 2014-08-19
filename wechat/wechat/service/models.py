#!/usr/bin/env python
# coding: utf-8
"""
Created On Jul 2, 2014

@author: jwang
"""
from django.conf import settings
from wechat.db import config as config_single, wechatdb

config_single(wechatdb, **settings.WECHATDB)
