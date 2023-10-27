#!/usr/bin/env python
# -*- coding:utf8 -*-

import datetime
import httplib, urllib, re
from xxxhandler import XXXHandler, assign_parser

FAM_HOST = 'http://fes.fa.gov.tw/'

PROJECT_PARSER = [
        {'key': u'計畫代碼',
        'seek': [u'計畫代碼', u'class=sline>'],
        'until': u'</span>'},

        {'key': u'計畫編號',
        'seek': [u'計畫編號', u'class=sline>'],
        'until': u'</span>'},

        {'key': u'計畫名稱',
        'seek': [u'計畫名稱', u'class=sline>'],
        'until': u'</span>'},

        {'key': u'執行單位',
        'seek': [u'執行單位', u'class=sline>'],
        'until': u'</span>'},

        {'key': u'研提日期',
        'seek': [u'研提日期', u'class=sline>'],
        'until': u'</span>'},

        {'key': u'核定日期',
        'seek': [u'核定日期', u'class=sline>'],
        'until': u'</span>'},

        {'key': u'核定金額',
        'seek': [u'核定金額', u'class=sline>'],
        'until': u'</span>'},

        {'key': u'撥付資料',
         'seek': [u'序號', u'合計'],
         'seek_sub': u'center',
         'sub': [{'key': u'撥付日期',
                 'seek': [u'<td', u'center\">'],
                 'until': u'</td>'},
                 {'key': u'經常門',
                 'seek': [u'<td', u'<td', u'right\">'],
                 'until': u'</td>'},
                 {'key': u'資本門',
                 'seek': [u'<td', u'right\">'],
                 'until': u'</td>'},
                 {'key': u'合計',
                 'seek': [u'<td', u'right\">'],
                 'until': u'</td>'}
                 ],
         'terminate': u'right'}
    ]

class FishMoney(XXXHandler):
    def __init__(self, host, port = 80, **kw):
        #kw["url_prefix"] = FAM_HOST
        super(FishMoney, self).__init__(host, **kw)

    def refine_date(self, data):
        try:
            r_year = re.search("[0-9]+", data)
            data = data[r_year.end():]
            
            r_month = re.search("[0-9]+", data)
            data = data[r_month.end():]
            
            r_day = re.search("[0-9]+", data)
            return datetime.datetime(int(r_year.group()) + 1911, int(r_month.group()), int(r_day.group()))
        except:
            return None
    
    def login(self, un="AM", pwd="am"):
        response = self.getPage("POST",
                                "/amd_2/svrp/mainpage_1.asp?prosta=2",
                                {"initxx":"1", "openam93":"Y", "userid":un, "passwd":pwd})
        response.read()
        self.header["Cookie"] = response.getheader('set-cookie')
        
        return True
        
    def get_project(self, project_code):
        k1 = k2 = k3 = ""
        project_code = project_code.split("-")
        if(len(project_code)>0): k1 = project_code[0]
        if(len(project_code)>1): k2 = project_code[1]
        if(len(project_code)>2): k3 = project_code[2]
         
        print ">> " + "/amd_2/svrp/program04s4.asp?" + (urllib.urlencode({"id":0,"tform":"program04s1F","k1":k1,"k2":k2,"k3":k3,"k99":"548"}))
        response = self.getPage("GET",
                                "/amd_2/svrp/program04s4.asp?" + (urllib.urlencode({"id":0,"tform":"program04s1F","k1":k1,"k2":k2,"k3":k3,"k99":"548"})))
        
        doc = self.parseDocument(response.read().decode("big5"), PROJECT_PARSER)
        doc[u'研提日期'] = self.refine_date(doc[u'研提日期'])
        doc[u'核定日期'] = self.refine_date(doc[u'核定日期'])
        doc[u'核定金額'] = float(self.refine(doc[u'核定金額'], "[0-9\,\.]+", "0").replace(",",""))
        for pay in doc[u'撥付資料']:
            pay[u'經常門'] = float(self.refine(pay[u'經常門'], "[0-9\,\.]+", "0").replace(",",""))
            pay[u'資本門'] = float(self.refine(pay[u'資本門'], "[0-9\,\.]+", "0").replace(",",""))
            pay[u'合計'] = float(self.refine(pay[u'合計'], "[0-9\,\.]+", "0").replace(",",""))
            pay[u'撥付日期'] = self.refine_date(pay[u'撥付日期'])
        return doc
