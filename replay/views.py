# -*- coding: utf8 -*-
from django.template import Template
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
import json
from django.conf import settings
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError, URLError
from ho600_ajax import controller, AJAXForbiddenError
from weblive.models import Place, FishingPort, Monitor, SyncLog, Account, Preset

if 'djangoappengine' not in settings.INSTALLED_APPS:
    memcache = False
else:
    try:
        from google.appengine.api import memcache
    except ImportError:
        memcache = False

from random import randint
from md5 import md5
from sha import sha
from time import time
import httplib
from decimal import Decimal

import os, urllib, logging, datetime, urllib2, re


try: from django.conf.settings import VIDEO_REPOSITORY_URL
except: VIDEO_REPOSITORY_URL = 'http://replay.nchu-cm.com/video/'

CITE_ORDER = {
    u"基隆市": 4,
    u"新北市": 5,
    u"臺北市": 6,
    u"台北市": 6,
    u"桃園縣": 7,
    u"新竹縣": 8,
    u"新竹市": 9,
    u"苗栗縣": 10,
    u"臺中市": 11,
    u"臺中縣": 11,
    u"台中市": 11,
    u"台中縣": 11,
    u"南投縣": 12,
    u"彰化縣": 13,
    u"嘉義縣": 14,
    u"嘉義市": 15,
    u"雲林縣": 16,
    u"臺南市": 17,
    u"台南市": 17,
    u"高雄市": 18,
    u"屏東縣": 19,
    u"臺東縣": 3,
    u"台東縣": 3,
    u"花蓮縣": 2,
    u"宜蘭縣": 1,
    u"澎湖縣": 21,
    u"金門縣": 22,
    u"連江縣": 23,
    u"南海島": 24,
}


class KeySortDict(dict):
    def list_sorted_key_and_value(self):
        keys = self.keys()
        keys.sort(key=lambda x: CITE_ORDER[x] if CITE_ORDER.has_key(x) else x)
        return [(key, self[key]) for key in keys]


def _verify_key_from_fes(allow_id, ask_time_str, verify_key):
    ask_time = datetime.datetime.strptime(ask_time_str, '%Y-%m-%d %H:%M:%S')
    if datetime.datetime.now() > (ask_time + datetime.timedelta(days=1)):
        return False
    elif sha('%s: %s'%(ask_time_str, allow_id)).hexdigest() != verify_key:
        return False
    else:
        return allow_id


def _get_monitor_hash(place_id='0'):
    hash = False
    if memcache:
        hash = memcache.get('monitor_hash')

    if not hash:
        hash = KeySortDict()
        if str(place_id) == '0':
            monitors = Monitor.objects.all().order_by('name')
        else:
            monitors = Monitor.objects.filter(place__fes_id=place_id).order_by('name')
        for monitor in monitors:
            place_name = monitor.port.place.name
            fishingport_name = monitor.port.name
            try:
                hash[place_name].setdefault(fishingport_name, []).append(monitor)
            except KeyError:
                hash[place_name] = KeySortDict([[fishingport_name, [monitor]]])
        if memcache:
            memcache.set('monitor_hash', hash, 3600)
    return hash


def index(R, site_id='1'):
    allow_id = R.GET.get('allow', '')
    allow_id = allow_id if allow_id != '' else R.session.get('allow', '')
    ask_time_str = R.GET.get('now', '')
    ask_time_str = ask_time_str if ask_time_str != '' else R.session.get('ask_time_str', '')
    verify_key = R.GET.get('verify_key', '')
    verify_key = verify_key if verify_key != '' else R.session.get('verify_key', '')

    if allow_id == '' or ask_time_str == '' or verify_key == '':
        return HttpResponseRedirect('http://fes.fa.gov.tw/harbor/replay/')
    result = _verify_key_from_fes(allow_id, ask_time_str, verify_key)
    if result == False:
        return HttpResponseRedirect('http://fes.fa.gov.tw/harbor/replay/')

    hash = _get_monitor_hash(place_id=result)

    templat = get_template(os.path.join('replay', 'index.html'))
    html = templat.render(RequestContext(R, {'site_id': site_id, 'hash': hash}))
    R.session['allow'] = allow_id
    R.session['ask_time_str'] = ask_time_str
    R.session['verify_key'] = verify_key
    return HttpResponse(html)


def video_repository(R, path):
    links = False
    if memcache:
        links = memcache.get(path)

    if not links:
        try:
            content, links = _get_video_repository_links(path)
        except urllib2.HTTPError, e:
            return HttpResponse(str(e))
        except urllib2.URLError, e:
            return HttpResponse(str(e))

        if memcache:
            memcache.set(path, links, 3600)

    return HttpResponse(content+'\n\n\nlinks: \n\n'+'\n'.join(links), mimetype='text/plain')


A_RE = re.compile('<a[^>]*>([0-9][^<]+)</a>', flags=re.I)
def _get_video_repository_links(path, video_url=''):
    u""" apache.conf should be set up like below:

    SetEnvIf Fesweblive-Replay    ^baae99c48f6b36e5cc0147924aa7ab84$    it_is_t01
    <Directory /home/fesweblive/modules/replay>
        Order Deny,Allow
        Allow from env=it_is_t01
        Deny from all
    </Directory>
    """
    if path and path[-1] != '/': path += '/'
    if not video_url: video_url = VIDEO_REPOSITORY_URL
    if video_url[-1] != '/': video_url += '/'

    url = video_url + path
    req = urllib2.Request(url)
    req.add_header('Fesweblive-Replay', 'baae99c48f6b36e5cc0147924aa7ab84')
    response = urllib2.urlopen(req)
    content = response.read()
    links = [video_url+path+a for a in A_RE.findall(content)]

    return content, links


@controller.register
def decide_time_range(R):
    time_str = re.sub('[- ]+', '/', R.POST.get('time_str', '').replace(u'時', ''))
    monitor_id = R.POST.get('monitor_id', '')
    path = '%s/%s/'%(monitor_id, time_str)
    links = False
    if memcache:
        links = memcache.get(path)

    if not links:
        m = Monitor.objects.get(fes_id=monitor_id)
        try:
            content, links = _get_video_repository_links(path, video_url=m.video_url)
        except urllib2.HTTPError, e:
            content, links = '', []
        except urllib2.URLError, e:
            content, links = '', []
        if memcache:
            memcache.set(path, links, 3600)
    return {'status': True, 'links': links}
