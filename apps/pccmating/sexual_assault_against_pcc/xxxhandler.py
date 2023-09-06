#!/usr/bin/env python
# -*- coding:utf8 -*-

import httplib, urllib, re

POST_HEADER = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain" }

def assign_parser(parser):
    def packager(fn):
        def wrapper(*args, **kw):
            kw["parser"] = parser
            return fn(*args, **kw)
        return wrapper
    return packager
    

class XXXHandler(object):
    class NotExistProjectAccountError(Exception):
        pass


    
    class NoProjectAccountDataError(Exception):
        pass



    def __init__(self, host, port = 80, **kw):
        self.header = {}
        self.debug = kw.has_key("debug") and kw["debug"] or False
        self.url_prefix = kw.has_key("url_prefix") and kw["url_prefix"] or ""
        self.connection = httplib.HTTPConnection(host, port)
    
    def getPage(self, method, path, data={}, ttl = 5):
        try:
            if(method=="POST"):
                self.connection.request(method, "%s%s"%(self.url_prefix, path), urllib.urlencode(data), dict(self.header, **POST_HEADER))
            else:
                self.connection.request(method, "%s%s"%(self.url_prefix, path), None, dict(self.header))

            return self.connection.getresponse()
            
        except Exception as e:
            if(ttl>0): self.getPage(method, path, data, ttl = ttl-1)
            raise
        
    def refine(self, data, regrep, default):
        try:
            r = re.search(regrep, data)
            if(r): return r.group()
            else: return default
        except:
            return default
    
    def parseDocument(self, _doc, document_parser, deep=False, indent = 0):
        whole_doc, doc, ldoc = _doc.lower(), _doc, _doc.lower()
        document = {}
        for n, parser in enumerate(document_parser):
            bad_seek = False
            # print n, parser
            for s in parser['seek']:
                try:
                    r = re.search(s, ldoc)
                    doc, ldoc = doc[r.end():], ldoc[r.end():]
                except AttributeError:
                    if(parser.has_key('allow_skip') and parser['allow_skip']):
                        bad_seek = True
                    else:
                        whole_doc = whole_doc.replace('\n', '').replace('\r', '')
                        if re.search(u'查無資料!!.*本計畫無撥款明細資料。', whole_doc):  
                            raise self.NotExistProjectAccountError(u'編碼錯誤，查無資料!')
                        elif u'本計畫無撥款明細資料' in whole_doc:
                            raise self.NoProjectAccountDataError(u'本計畫無撥款明細資料!')
                        if(self.debug):
                            print(u"正在嘗試移動指標時發生錯誤。key=%s, seek for=%s, \r\nDocument left:%s"%(parser['key'], s, doc))
                            return document
                        else:
                            raise Exception(u"正在嘗試移動指標時發生錯誤。key=%s, seek for=%s, \r\nDocument left:%s"%(parser['key'], s, doc))
            if(bad_seek): continue
            try:
                if(parser.get('sub', None)):
                    document[parser['key']] = []

                    terminate = False
                    if(self.debug): print("%*s: ["%(indent, parser['key']))

                    while(not terminate):
                        #DEBUG
                        if(self.debug): print("%*s"%(indent, "{"))
                        
                        s_re = re.search(parser['seek_sub'], ldoc)
                        t_re = re.search(parser['terminate'], ldoc)

                        if(s_re and s_re.start() < t_re.start()):
                            doc, ldoc = doc[s_re.end():], ldoc[s_re.end():]
                            sub_document, doc, ldoc = self.parseDocument(doc, parser['sub'], deep=True, indent=(indent + 5))
                            document[parser['key']].append(sub_document)
                        else:
                            terminate = True
                        
                        #DEBUG
                        if(self.debug): print("%*s"%(indent, "},"))
                        
                    #DEBUG
                    if(self.debug): print("%*s"%(indent, "]"))
                else:
                    r_end = re.search(parser['until'], ldoc)
                    document[parser['key']] = doc[0:r_end.start()]
                    if(self.debug): print("%*s: %s"%(indent, parser['key'], document[parser['key']]))

                    doc, ldoc = doc[r_end.end():], ldoc[r_end.end():]
            except AttributeError:
                if(self.debug): 
                    print(u"正在嘗試移動指標時發生錯誤。key=%s, seek for=%s, \r\nDocument left:%s"%(parser['key'], s, doc))
                    return document
                else:
                    raise Exception(u"正在嘗試移動指標時發生錯誤。key=%s, seek for=%s, \r\nDocument left:%s"%(parser['key'], s, doc))

        if(deep):
            return document, doc, ldoc
        else:
            return document
