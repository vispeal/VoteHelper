PROJECT_NAME = 'weibo-news'
VERSION_CONTROL = "dolphindeploy.git"
APP_DIR = '/var/app/weibonews'
# The Project Role Alias table.
ROLE_ALIAS = {
    'nginx-web' : 'NGINX Web',
    'wechat': 'Wechat',
}
# The project app table
ROLE_APPS_TABLE = {
    'NGINX Web' : ['nginx_web'],
    'Wechat': ['weibonews', 'wechat'],
}
# Extra extension to search
EXTRA_EXT_PATTERN = (
    '.conf',
    '.cfg',
    '.xml',
    '.csv',
    '.nginx',
    '.sh',
    '.properties',
)
# Extra file name to search
EXTRA_CONF_NAME_PATTERN = (
    'version',
    'settings.py',
)

BUILD_HANDLER_CONFIG = (
    'dolphindeploy.handlers.ConfigurationFileHandler',
)
