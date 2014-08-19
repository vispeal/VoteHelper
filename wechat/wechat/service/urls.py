from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('wechat.service.views',
    # GET Method
    url(r'^handler$', 'operation.handler'),
    url(r'^vote/history\.json$', 'operation.vote_history'),
    # POST Method
    url(r'^vote/start$', 'operation.start_vote'),
)
