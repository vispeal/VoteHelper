#!/usr/bin/env python
# coding: utf-8
"""
Created On Nov 13, 2013
@Author : Jun Wang
Email: jwang@bainainfo.com
"""
import os
import time
from ConfigParser import InterpolationMissingOptionError
from weibonews.utils.config import MultiLocaleConfigParser
from logging.config import dictConfig
from weibonews.db.utils import parse_conn_string


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {}
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

os.environ["TZ"] = TIME_ZONE
time.tzset()

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5q%#w%g-iy(#skb6y=z1gj63d61u990swg=@u=yoyy68uk+=(o'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'wechat.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    # 'django.contrib.auth',
    # 'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.sites',
    # 'django.contrib.messages',
    # 'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
#    'cronjob',
#    'data_manager',
    #'django_mongodb_engine',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(process)d [%(filename)s:%(lineno)d] %(funcName)s %(message)s'
        },
        'detail': {
            'format': '%(asctime)s %(levelname)s %(module)s %(message)s'
        },
        'message_only': {
            'format': '%(asctime)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file':{
            'level':'DEBUG',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'filename': '/tmp/admin.log',
            'when': 'D',
            'backupCount' : 30
        },
        'perf':{
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'formatter': 'message_only',
            'filename':'/tmp/perf.log',
            'maxBytes': 30 * 1024 * 1024, # 30MB
            'backupCount' : 30
        },
        'err':{
            'level':'ERROR',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'filename':'/tmp/error.log',
            'when': 'D',
            'backupCount' : 7
        },
    },
    'loggers': {
        'weibonews.wechat': {
            'handlers': ['file', 'err'],
            'level': 'DEBUG',
        },
        'weibonews.db': {
            'handlers': ['file', 'err'],
            'level': 'DEBUG',
        },
        'weibonews.perf': {
            'handlers': ['perf'],
            'level': 'DEBUG',
        },
    },
}


WECHATDB = None

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

def _load_config():
    """
    config db, image and dispatch etc.
    """
    global WECHATDB
    section = 'wechat'
    config_parser = MultiLocaleConfigParser()
    config_parser.read([os.path.join(SITE_ROOT, "/var/app/weibonews/enabled/wechat/wechat.cfg")])

    WECHATDB = parse_conn_string(config_parser.get(section, 'wechatdb'))
    log_dir = config_parser.get(section, 'logs_dir', 'logs')
    LOGGING['handlers']['file']['filename'] = os.path.join(log_dir, 'wechat.log')
    LOGGING['handlers']['perf']['filename'] = os.path.join(log_dir, 'perf.log')
    LOGGING['handlers']['err']['filename'] = os.path.join(log_dir, 'error.log')
    dictConfig(LOGGING)


try:
    _load_config()
except InterpolationMissingOptionError as err:
    print err
