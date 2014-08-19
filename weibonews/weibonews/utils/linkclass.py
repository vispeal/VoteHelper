'''
Created on Jul 30, 2013

@author: fli
'''
from weibonews.utils.downloader import download
from urllib2 import urlparse

_SHORT_SERVICE = {
    't.cn' : True,
    'nnq.tv': True,
    'v.uyan.cc': True,
    's.uyan.cc': True,
    'ywb.so': True,
    'uyc.cc': True,
    'wap.tbssdpk.com': True,
    'ua.yesweibo.com': True,
    '955.cc': True,
    'v.burl.cc': True,
    'burl.cc': True,
    'url.winnew.net': True,
}

SITE_TYPE = {
    'ads' : -3,
    'ecom' : -2,
    'junk' : -1,
    'news' : 0,
    'vedio' : 1,
    'music' : 2,
    'forum' : 3,
    'social' : 4,
    'picture' : 5,
    'app' : 6,
}

_BLACK_SITE_LIST = {
    'weiligongshe.com' : -3,
    '59zan.com' : -3,
    'buchou.com' : -3,
    'taobao.com' : -2,
    'tmall.com' : -2,
    'jd.com' : -2,
    'jumei.com' : -2,
    'emop.cn' : -2,
    'j.cn': -2,
    'meilishuo' : -2,
    'haitaozhekou.com' : -2,
    'taoppp.com' : -2,
    'jetsousa.com' : -2,
    'czfxh.com' : -2,
    'kiees.com' : -2,
    'dealam.com' : -2,
    'haitaozj.com' : -2,
    'itugo.com' : -2,
    '55haitao.com' : -2,
    'egou.com' : -2,
    'haitaomen.com' : -2,
    'mogujie.com' : -2,
    'youtube.com' : 1,
    'youku.com' : 1,
    'iqiyi.com' : 1,
    'tudou.com' : 1,
    'tv.sohu.com' : 1,
    'video.sina.com.cn' : 1,
    'v.qq.com' : 1,
    'v.ifeng.com' : 1,
    '56.com' : 1,
    'ku6.com' : 1,
    'letv.com' : 1,
    'yinyuetai.com' : 2,
    'changba.com' : 2,
    'tianya.cn' : 3,
    'mop.com' : 3,
    'zhihu.com' : 3,
    'weibo.com' : 4,
    'weibo.cn' : 4,
    'peopleurl.cn': 4,
    'papa.me' : 4,
    'url.cn' : 4, #tencent weibo
    'immomo.com' : 4,
    'gifshow.com' : 4,
    'instagram.com' : 5,
    'tuding001.com' : 5,
    'voguemate.com' : 5,
    'sinaapp.com' : 6,
    'danhuaer.com' : 6,
    'tugewang.com': 5,
    'meilishuo.com' : -2,
    'suning.com': -2,
    'mafengwo.cn': 4,
    'tuan800.com': -2,
    'quban.tyhk.org.cn': -3,
    'amazon.com': -2,
    'amazon.cn': -2,
    'www.oneline.cc': -1,
    'mryhd.com': -2,
    'dealmoon.com': -2,
    'douban.com': 4,
    '21usdeal.com': -2,
    'taoban.com': -2,
    '87050.com': -1,
    'weiph.cn': -2,
    'tsdxb.com': -2,
    'pan.baidu.com': -1,
    'istyle.163.com': 5,
    'abjmt.com': -2,
    'haitaomama.cn': -2,
    'mostyle.me': 5,
    'tieba.baidu.com': 3,
    'hrwdw.com': -1,
    'jiepang.com': -2,
    'jie.pn': -2,
    'baomihua.com': -2,
    'qumaisha.com': -2,
    'jayxun.com': -1,
    'jayzou.com': -1,
    '51fanli.com': -2,
    'mogujie.cn': -2,
    'shui5.cn': -1,
    'qzone.qq.com': 4,
    'meidebi.com': -2,
    'alipay.com': -1,
    'dianping.com': -2,
    'hers.net.cn': 3,
    'hers.com.cn': 3,
    'wap.mrjfzx.com': -2,
    'm.163.com': 6,
    'shopdealus.com': -2,
    '9iyouhui.com': -2,
    'tv.cntv.cn': 1,
    'shhbm.com': -2,
    'quban.idc-xf.com': -1,
    'kidulty.com': -1,
    'damai.cn': 2,
    'koreaxing.com': -2,
    'bilibili.tv': 1,
    '19lou.com': 3,
    'pptv.com': 1,
    'phfgh.com': -2,
    'mtyhd.com': -2,
    'bookchina.com': -1,
    '5sing.com': 2,
    'itunes.apple.com': 6,
    'cmt2013.com': -2,
    'yoho.cn': -2,
    'yhzzd.com': -2,
    'weico.com': 5,
    'juetuzhi.net': 5,
    'slide.news.sina.com.cn': 5,
    'imgo.tv': 1,
    'yixia.com': 1,
    'ixchao.com': -2,
    'quban.51sfs.com': -1,
    'twitter.com': 4,
    'qb.9udoc.com': -1,
    'quban.9udoc.com': -1,
    'meituan.com': -2,
    'ozdazhe.com': -2,
    'xuanxuanfanli.com': -2,
    '7k7k.com': -1,
}

def classify_link(link):
    ''' classify link according to its domain
    '''
    if link is None:
        return link, SITE_TYPE['junk']
    original_url = link
    url = urlparse.urlparse(link)
    max_try_count = 10
    try_count = 0
    while url.netloc in _SHORT_SERVICE:
        if try_count >= max_try_count:
            # if multiple redirect, return as news
            return link, SITE_TYPE['news']
        #get original link of short link
        original_url = _get_original_link(original_url)
        url = urlparse.urlparse(original_url)
        try_count += 1
    domain_token = url.netloc.split('.')
    length = len(domain_token) - 2
    while length >= 0:
        domain = '.'.join(domain_token[length:])
        if domain in _BLACK_SITE_LIST:
            return original_url, _BLACK_SITE_LIST[domain]
        length -= 1
    #treat unclassified link as news link
    return original_url, SITE_TYPE['news']

def _get_original_link(link):
    resp = download(link, follow_redirect=False)
    if resp is None:
        return link
    return resp.original_url or link

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print "python linkclass link"
        sys.exit()
    print classify_link(sys.argv[1])
