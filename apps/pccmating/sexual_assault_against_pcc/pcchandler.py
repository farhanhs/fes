#!/usr/bin/env python
# -*- coding:utf8 -*-
import datetime
import httplib, urllib, re
from xxxhandler import XXXHandler, assign_parser

from parser_parameter import PCC_HOST_PREFIX #工程會網址
from parser_parameter import URL_INFORMATION #登入及資料頁面路徑
from parser_parameter import DOCUMENT_PARSER_REFERENCE #工程基本資料 及 進度資料 parser key word

class SexualAssaultAgainstPCC(XXXHandler):
    def __init__(self, host, port = 80, **kw):
        kw["url_prefix"] = PCC_HOST_PREFIX
        super(SexualAssaultAgainstPCC, self).__init__(host, port, **kw)
        
    def refine_pccdate(self, data):
        try:
            r_year = re.search("[0-9]+", data)
            data = data[r_year.end():]
            
            r_month = re.search("[0-9]+", data)
            data = data[r_month.end():]

            r_day = re.search("[0-9]+", data)

            return datetime.datetime(int(r_year.group()) + 1911, int(r_month.group()), int(r_day.group()))
        except:
            return None
    
    def login(self, un, pwd): # un=username, pwd=password
        #先去 "/pccms/owa/cmdmang.userin" 取得頁面上的iwebdat
        try:
            response = self.getPage("POST", URL_INFORMATION["start_login_page"], {})
            doc = response.read().decode("big5", "replace")
            ldoc = doc.lower()
            seek = re.search('<input type="hidden" name="iwebdat" value="', ldoc).span()[1]
            temp_doc = doc[seek:]
            seek = re.search('">', temp_doc).start()
            self.iwebdat = temp_doc[0:seek]
        except:
            return [{'connect_error': True, 'connect_msg': u'get login iwebdat 錯誤'}, False]

        try:
            #進行登入 "/pccms/owa/cmdmang.chkpas" 需要帳號un  密碼pwd  icnt   iwebdat
            response = self.getPage("POST", URL_INFORMATION["login_page"], {"icnt":"1",
                                                                             "iwebnam": un,
                                                                             "iwebpas": pwd,
                                                                             "iwebdat": self.iwebdat})
            doc = response.read().decode("big5", "replace")
            ldoc = doc.lower()

            # GET USER ID  => userid
            seek = re.search("<input type=hidden name=iwebnam value=", ldoc).span()[1]
            temp_doc = doc[seek:]
            seek = re.search(">", temp_doc).start()
            self.userid = temp_doc[0:seek]
        
            # GET USER IDENTIFY CODE => usercode
            seek = re.search("<input type=hidden name=iwebcod value=", ldoc).span()[1]
            temp_doc = doc[seek:]
            seek = re.search(">", temp_doc).start()
            self.usercode = temp_doc[0:seek]
        except:
            return [{'connect_error': True, 'connect_msg': u'get login usercode 錯誤'}, False]

        try:
            # GET USER IDENTIFY CODE => usercode2
            response = self.getPage("POST", URL_INFORMATION["search_page"], {"iwebcod":self.usercode,
                                                                            "iuid": self.userid})
            doc = response.read().decode("big5", "replace")
            ldoc = doc.lower()
            seek = re.search('<input type="hidden" name="iwebcod" value="', ldoc).span()[1]
            temp_doc = doc[seek:]
            seek = re.search('">', temp_doc).start()
            self.usercode2 = temp_doc[0:seek]
        except:
            return [{'connect_error': True, 'connect_msg': u'get login usercode2 錯誤'}, False]
        return [self.userid, self.usercode]
    
    @assign_parser(DOCUMENT_PARSER_REFERENCE["project_document"])
    def getProjectBasicInformation(self, project_id, parser):
        # get iwebcod
        response = self.getPage("POST", URL_INFORMATION["search_page"], {"iwebcod":self.usercode,
                                                                        "iuid": self.userid})
        # return {'connect_error': True, 'connect_msg': u'get iwebcod 錯誤'}
        try:
            swap_doc = response.read().decode("big5", "replace")
            lswap_doc = swap_doc.lower()
            seek = re.search(u'<input type="hidden" name="iwebcod" value="', lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            seek = re.search(u'"', lswap_doc).start()
            self.iwebcod = swap_doc[:seek]
        except:
            return {'connect_error': True, 'connect_msg': u'get iwebcod 錯誤'}

        try:
            # get iwkut
            response = self.getPage("POST", URL_INFORMATION["search_uid"], {"iwebcod":self.iwebcod,
                                                                            "iuid": self.userid,
                                                                            "iprjno": project_id})
            swap_doc = swap_doc2 = response.read().decode("big5", "replace")
            lswap_doc = lswap_doc2 = swap_doc.lower()
        except:
            return {'connect_error': True, 'connect_msg': u'get iwkut 錯誤'}

        try:
            #直接取得連結
            seek = re.search(u'執行單位', lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            seek = re.search(u'<a href=', lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            seek = re.search(u'>', lswap_doc).start()
            swap_doc, lswap_doc = swap_doc[:seek], lswap_doc[:seek]
            response = self.getPage("POST", swap_doc, {})
        except:
            return {'connect_error': True, 'connect_msg': u'get url 錯誤'}
        # response = self.getPage("POST", URL_INFORMATION["query_project"], {"iwebcod":self.usercode,
        #                                                                     "iuid": self.userid,
        #                                                                     "iwkut": self.iwkut,
        #                                                                     "iprjno": project_id})
        try:
            swap_doc = response.read().decode("big5", "replace")
            doc = self.parseDocument(swap_doc, parser)
        except:
            return {'connect_error': True, 'connect_msg': u'parser Basic Info 錯誤'}
        return doc

    @assign_parser(DOCUMENT_PARSER_REFERENCE["project_document"])
    def getAllFisheryProjectInList(self, parser):
        projects_list = []

        for page in xrange(0, 901, 100):
            response = self.getPage("POST", URL_INFORMATION["fishey_project_list"], {"iwebcod":self.usercode,
                                                                                     "iuid": self.userid,
                                                                                     "iwkut": self.usercode,
                                                                                     "ishowb": page,
                                                                                     })
            swap_doc = response.read().decode("big5", "replace")
            lswap_doc = swap_doc.lower()
            seek = re.search(u"經費來源單位： 行政院農業部漁業署", lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            seek = re.search(u"差異</th>", lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            seek = re.search(u"</tr>", lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            seek = re.search(u"</table>", lswap_doc).start()
            if seek == 1:
                break
            swap_doc, lswap_doc = swap_doc[:seek], lswap_doc[:seek]
            
            
            tr_list = []
            while lswap_doc:
                seek_start = re.search(u"<tr>", lswap_doc).start()
                seek_end = re.search(u"</tr>", lswap_doc).end()
                tr_list.append(swap_doc[seek_start:seek_end+1])
                swap_doc, lswap_doc = swap_doc[seek_end+1:], lswap_doc[seek_end+1:]

            for n, tr in enumerate(tr_list):
                row = tr.split('</TD>')
                info = {}
                info[u"執行機關"] = row[1].split(u'>')[1]
                info[u"編號"] = row[2].split(u'>')[1]
                info[u"標案名稱"] = row[3].split(u'>')[2].replace('</A', '')
                row[4] = row[4].replace('<font size=-1 color=olive>', '').replace('</font>', '')
                try:
                    d = row[4].split(u'>')[1]
                    info[u"預定公告日期"] = datetime.datetime(int(d[:3]) + 1911, int(d[3:5]), int(d[5:]))
                except:
                    info[u"預定公告日期"] = None
                try:
                    d = row[5].split(u'>')[1]
                    info[u"實際決標日期"] = datetime.datetime(int(d[:3]) + 1911, int(d[3:5]), int(d[5:]))
                except:
                    info[u"實際決標日期"] = None
                info[u"發包預算"] = float(row[6].split(u'>')[1].replace(' ', '').replace(',', '')) * 1000
                info[u"決標金額"] = float(row[7].split(u'>')[1].replace(' ', '').replace(',', '')) * 1000
                if len(row) == 13:
                    info[u"進度年"] = row[8].split(u'>')[1][:3]
                    info[u"進度月"] = row[8].split(u'>')[1][4:]
                    info[u"預定進度"] = row[9].split(u'>')[1].replace('%', '').replace(' ', '')
                    info[u"實際進度"] = row[10].split(u'>')[1].replace('%', '').replace(' ', '')
                else:           
                    info[u"進度年"] = None
                    info[u"進度月"] = None
                    info[u"預定進度"] = None
                    info[u"實際進度"] = None
                projects_list.append(info)
        return projects_list
    

    @assign_parser(DOCUMENT_PARSER_REFERENCE["supervise_information"])
    def getSuperviseBasicInformation(self, url, date, parser):
        swap_doc = self.getPage("GET", url).read().decode("big5", "replace")
        seek = re.search(u"其他意見", swap_doc).end()
        swap_doc = swap_doc[seek:]
        seek = re.search(u"</TABLE>", swap_doc).start()
        swap_doc = swap_doc[:seek]
        date = str(date).split('-')
        pcc_date = '>%s.%s.%s' % (str(int(date[0]) - 1911), date[1], date[2])

        if not re.search(pcc_date, swap_doc):
            return None
        swap_doc = swap_doc.split('<TR>')
        for tr in swap_doc:
            if re.search(pcc_date, tr):
                seek = re.search(u'<A HREF=', tr).end()
                tr = tr[seek:]
                seek = re.search(' title', tr).start()
                tr = tr[:seek]
                supervise_url = tr
                break
        swap_doc = self.getPage("GET", supervise_url).read().decode("big5", "replace")

        doc = self.parseDocument(swap_doc, parser)

        doc['place'] = doc['place_location'][:3].replace(u'台', u'臺')
        doc['location'] = doc['place_location'][3:]
        doc['project_manage_unit'] = doc['project_manage_unit'].replace(u'\n', '')
        doc['project'] = doc['project'].replace(u'\n', '')
        doc['project_organizer_agencies'] = doc['project_organizer_agencies'].replace(u'\n', '')
        doc['designer'] = doc['designer'].replace(u'\n', '')
        doc['inspector'] = doc['inspector'].replace(u'\n', '')
        doc['construct'] = doc['construct'].replace(u'\n', '')
        doc['budget_price'] = float(self.refine(doc["budget_price"], "[0-9\,\.]+", "0").replace(",",""))

        contract_price = doc["contract_price"]
        seek = re.search(u"元", contract_price).end()

        doc['contract_price'] = float(self.refine(contract_price[:seek+1], "[0-9\,\.]+", "0").replace(",",""))
        if u'變更' in contract_price:
            seek = re.search(u"變更", contract_price).end()
            contract_price = contract_price[seek:]
            seek = re.search(u"<", contract_price).end()
            doc["contract_price_change"] = float(self.refine(contract_price[:seek+1], "[0-9\,\.]+", "0").replace(",",""))
        else:
            doc["contract_price_change"] = None
            
        doc['scheduled_progress'] = float(self.refine(doc["scheduled_progress"], "[0-9\,\.]+", "0").replace(",",""))
        doc['actual_progress'] = float(self.refine(doc["actual_progress"], "[0-9\,\.]+", "0").replace(",",""))
        doc['scheduled_money'] = float(self.refine(doc["scheduled_money"], "[0-9\,\.]+", "0").replace(",",""))
        doc['actual_money'] = float(self.refine(doc["actual_money"], "[0-9\,\.]+", "0").replace(",",""))
        doc["progress_date"] = self.refine_pccdate(doc["progress_date"] + u'15日') if u'日' not in doc["progress_date"] else self.refine_pccdate(doc["progress_date"])
        doc["date"] = self.refine_pccdate(doc["date"])
        doc["start_date"] = self.refine_pccdate(doc["start_date"])

        expected_completion_date = doc["expected_completion_date"]
        seek = re.search(u"日", expected_completion_date).end()
        doc["expected_completion_date"] = self.refine_pccdate(expected_completion_date[:seek+1])
        if u'變更' in expected_completion_date:
            seek = re.search(u"變更後至", expected_completion_date).end()
            expected_completion_date = expected_completion_date[seek:]
            seek = re.search(u"日", expected_completion_date).end()
            doc["expected_completion_date_change"] = self.refine_pccdate(expected_completion_date[:seek+1])
        else:
            doc["expected_completion_date_change"] = None

        doc["outguide"] = doc["outguide"].replace(u'(無)', '').replace(u' ', '').replace(u'\n', '').split('、')
        doc["inguide"] = doc["inguide"].replace(u'(無)', '').replace(u' ', '').replace(u'\n', '').split('、')
        doc["captain"] = doc["captain"].replace(u'(無)', '').replace(u' ', '').replace(u'\n', '').split('、')
        doc["worker"] = doc["worker"].replace(u'(無)', '').replace(u' ', '').replace(u'\n', '').split('、')
        try: 
            doc['score'] = float(doc['score'])
        except:
            doc['score'] = 0
        doc["info"] = doc["info"].replace('<br>', '\n').replace('<BR>', '\n')
        doc["progress_info"] = doc["progress_info"].replace('<br>', '\n').replace('<BR>', '\n')
        doc["merit"] = doc["merit"].replace('<br>', '\n').replace('<BR>', '\n')
        doc["advise"] = doc["advise"].replace('建議：<br>', '').replace('<br>', '\n').replace('<BR>', '\n')
        doc["other_advise"] = doc["other_advise"].replace('<br>', '\n').replace('<BR>', '\n').replace('<font color=gray>', '').replace('</font>', '')
        doc["test"] = doc["test"].replace('<br>', '\n').replace('<BR>', '\n').replace('<font color=gray>', '').replace('</font>', '')
        if u'承攬廠商' in doc['deductions']:
            seek = re.search(u'承攬廠商', doc['deductions']).end()
            point = doc['deductions'][seek:]
            seek = re.search(u'扣', point).end()
            point = point[seek:]
            seek = re.search(u'點', point).start()
            point = point[:seek]
            doc['construct_deduction'] = point
        if u'監造廠商' in doc['deductions']:
            seek = re.search(u'監造廠商', doc['deductions']).end()
            point = doc['deductions'][seek:]
            seek = re.search(u'扣', point).end()
            point = point[seek:]
            seek = re.search(u'點', point).start()
            point = point[:seek]
            doc['inspector_deduction'] = point
        return doc

    def getSuperviseErrorInformation(self, url, date):
        swap_doc = self.getPage("GET", url).read().decode("big5", "replace")
        seek = re.search(u"其他意見", swap_doc).end()
        swap_doc = swap_doc[seek:]
        seek = re.search(u"</TABLE>", swap_doc).start()
        swap_doc = swap_doc[:seek]
        date = str(date).split('-')
        pcc_date = '>%s.%s.%s' % (str(int(date[0]) - 1911), date[1], date[2])
        if not re.search(pcc_date, swap_doc):
            return None
        swap_doc = swap_doc.split('<TR>')

        for tr in swap_doc:
            if re.search(pcc_date, tr):
                seek = re.search(u'<A HREF=', tr).end()
                tr = tr[seek:]
                seek = re.search('>', tr).start()
                tr = tr[:seek]
                supervise_url = tr
                break

        swap_doc = self.getPage("GET", supervise_url).read().decode("big5", "replace")
        seek = re.search(u"缺失扣點填報請參考：", swap_doc).end()
        swap_doc = swap_doc[seek:]
        seek = re.search(u"記點對象", swap_doc).end()
        swap_doc = swap_doc[seek:]
        seek = re.search(u"</TABLE>", swap_doc).start()
        swap_doc = swap_doc[:seek]
        errors = []
        while re.search(u"<a HREF=", swap_doc):
            temp = []
            seek = re.search(u"<a HREF=", swap_doc).end()
            swap_doc = swap_doc[seek:]
            seek = re.search(u">", swap_doc).end()
            swap_doc = swap_doc[seek:]
            seek = re.search(u"</a>", swap_doc).start()
            temp.append(swap_doc[:seek])
            swap_doc = swap_doc[seek:]

            seek = re.search(u"#ffffc7>", swap_doc).end()
            swap_doc = swap_doc[seek:]
            seek = re.search(u"</TD>", swap_doc).start()
            temp.append(swap_doc[:seek])
            swap_doc = swap_doc[seek:]

            seek = re.search(u"#ffffc7", swap_doc).end()
            swap_doc = swap_doc[seek:]
            seek = re.search(u">", swap_doc).end()
            swap_doc = swap_doc[seek:]
            seek = re.search(u"</TD>", swap_doc).start()
            temp.append(swap_doc[:seek])
            swap_doc = swap_doc[seek:]

            seek = re.search(u"#ffffc7", swap_doc).end()
            swap_doc = swap_doc[seek:]
            seek = re.search(u">", swap_doc).end()
            swap_doc = swap_doc[seek:]
            seek = re.search(u"</TD>", swap_doc).start()
            temp.append(swap_doc[:seek].replace('<font color=red>', '').replace('</font>', ''))
            swap_doc = swap_doc[seek:]
            errors.append(temp)
        return errors

    @assign_parser(DOCUMENT_PARSER_REFERENCE["project_information"])
    def getProjectFullInformation(self, url, parser):
        doc = self.parseDocument(self.getPage("GET", url).read().decode("big5", "replace"), parser)

        doc["host_department_code"] = doc["host_department_code"].replace("\n", "")
        doc["total_budget"] = float(self.refine(doc["total_budget"], "[0-9\,\.]+", "0").replace(",",""))*1000
        doc["contract_budget"] = float(self.refine(doc["contract_budget"], "[0-9\,\.]+", "0").replace(",",""))*1000
        doc["constructor"] = doc["constructor"].replace("\n", "")
        doc["s_design_complete_date"] = self.refine_pccdate(doc["s_design_complete_date"])
        doc["r_design_complete_date"] = self.refine_pccdate(doc["r_design_complete_date"])
        doc["s_public_date"] = self.refine_pccdate(doc["s_public_date"])
        doc["r_public_date"] = self.refine_pccdate(doc["r_public_date"])
        doc["s_decide_tenders_date"] = self.refine_pccdate(doc["s_decide_tenders_date"])
        doc["r_decide_tenders_date"] = self.refine_pccdate(doc["r_decide_tenders_date"])
        doc["s_public_date"] = self.refine_pccdate(doc["s_public_date"])
        doc["r_public_date"] = self.refine_pccdate(doc["r_public_date"])
        doc["s_base_price"] = float(self.refine(doc["s_base_price"], "[0-9\,\.]+", "0").replace(",",""))*1000
        doc["r_base_price"] = float(self.refine(doc["r_base_price"], "[0-9\,\.]+", "0").replace(",",""))*1000
        doc["decide_tenders_price"] = float(self.refine(doc["decide_tenders_price"], "[0-9\,\.]+", "0").replace(",",""))*1000
        if(doc.has_key("decide_tenders_price2")): doc["decide_tenders_price2"] = float(self.refine(doc["decide_tenders_price2"], "[0-9\,\.]+", "0").replace(",",""))*1000
        doc["s_start_date"] = self.refine_pccdate(doc["s_start_date"])
        doc["r_start_date"] = self.refine_pccdate(doc["r_start_date"])
        doc["s_end_date"] = self.refine_pccdate(doc["s_end_date"])
        if(doc.has_key("s_end_date2")): doc["s_end_date2"] = self.refine_pccdate(doc["s_end_date2"])
        doc["r_end_date"] = self.refine_pccdate(doc["r_end_date"])
        if(doc.has_key("r_checked_and_accepted_date")): doc["r_checked_and_accepted_date"] = self.refine_pccdate(doc["r_checked_and_accepted_date"])
        doc["s_last_pay_date"] = self.refine_pccdate(doc["s_last_pay_date"])
        doc["r_last_pay_date"] = self.refine_pccdate(doc["r_last_pay_date"])
        doc["balancing_price"] = float(self.refine(doc["balancing_price"], "[0-9\,\.]+", "0").replace(",",""))*1000
        doc["last_pay_price"] = float(self.refine(doc["last_pay_price"], "[0-9\,\.]+", "0").replace(",",""))*1000
        
        return doc
    
    @assign_parser(DOCUMENT_PARSER_REFERENCE["project_progess"])
    def getProjectBudgetInformation(self, url, parser):
        doc = self.parseDocument(self.getPage("GET", url).read().decode("big5", "replace"), parser)
        doc["money_of_predict_progress"] = float(self.refine(doc["money_of_predict_progress"], "[0-9\,\.]+", "0").replace(",",""))*1000
        doc["percentage_of_predict_progress"] = float(self.refine(doc["percentage_of_predict_progress"], "[0-9\,\.]+", "0").replace(",",""))/100
        doc["money_of_real_progress"] = float(self.refine(doc["money_of_real_progress"], "[0-9\,\.]+", "0").replace(",",""))*1000
        doc["month"] = int(self.refine(doc["month"], "[0-9\,]+", "0").replace(",",""))
        doc["year"] = int(self.refine(doc["year"], "[0-9\,]+", "0").replace(",",""))
        doc["percentage_of_real_progress"] = float(self.refine(doc["percentage_of_real_progress"], "[0-9\,\.]+", "0").replace(",",""))/100
        doc["totale_money_paid"] = float(self.refine(doc["totale_money_paid"], "[0-9\,\.]+", "0").replace(",",""))*1000
        return doc
        
        
    
    












    @assign_parser(DOCUMENT_PARSER_REFERENCE["project_document"])
    def getAllProject(self, parser):
        #取得這個頁面http://cmdweb.pcc.gov.tw/pccms/owa/prjquer.lsprj?iwebcod=395250000G&iwkut=395250000&ibdgt1d=0&ibdgt1u=999999999&iuid=1P2721243K26242A282G        
        
        projects_list = []

        for page in xrange(0, 1901, 100):
            response = self.getPage("POST", URL_INFORMATION["project_list"], {"iwebcod":self.usercode2,
                                                                                     "iuid": self.userid,
                                                                                     "iwkut": self.usercode2,
                                                                                     "ishowb": page,
                                                                                     })
            swap_doc = response.read().decode("big5", "replace")
            #取得開始
            lswap_doc = swap_doc.lower()
            seek = re.search(u"執行單位： 行政院農業部漁業署", lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            seek = re.search(u"完工日期</th>", lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            seek = re.search(u"</tr>", lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            #取得結尾
            seek = re.search(u"</table>", lswap_doc).start()
            if seek == 1:
                break
            swap_doc, lswap_doc = swap_doc[:seek], lswap_doc[:seek]
            
            
            tr_list = []
            while lswap_doc:
                seek_start = re.search(u"<tr>", lswap_doc).start()
                seek_end = re.search(u"</tr>", lswap_doc).end()
                tr_list.append(swap_doc[seek_start:seek_end+1])
                swap_doc, lswap_doc = swap_doc[seek_end+1:], lswap_doc[seek_end+1:]

            for n, tr in enumerate(tr_list):
                row = tr.split('</TD>')
                info = {}
                info[u"編號"] = row[1].split(u'>')[1]
                info[u"執行機關"] = row[2].split(u'>')[1]
                info[u"標案名稱"] = row[3].split(u'>')[2].replace('</A', '')
                row[4] = row[4].replace('<font size=-1 color=olive>', '').replace('</font>', '')
                try:
                    d = row[4].split(u'>')[1]
                    info[u"預定公告日期"] = datetime.datetime(int(d[:3]) + 1911, int(d[3:5]), int(d[5:]))
                except:
                    info[u"預定公告日期"] = None
                try:
                    d = row[5].split(u'>')[1]
                    info[u"實際決標日期"] = datetime.datetime(int(d[:3]) + 1911, int(d[3:5]), int(d[5:]))
                except:
                    info[u"實際決標日期"] = None
                info[u"發包預算"] = float(row[6].split(u'>')[1].replace(' ', '').replace(',', '')) * 1000
                try:
                    info[u"決標金額"] = float(row[7].split(u'>')[1].replace(' ', '').replace(',', '')) * 1000
                except: info[u"決標金額"] = None
                if len(row) == 13:
                    info[u"進度年"] = row[8].split(u'>')[1][:3]
                    info[u"進度月"] = row[8].split(u'>')[1][4:]
                    info[u"預定進度"] = row[9].split(u'>')[1].replace('%', '').replace(' ', '')
                    info[u"實際進度"] = row[10].split(u'>')[1].replace('%', '').replace(' ', '')
                else:           
                    info[u"進度年"] = None
                    info[u"進度月"] = None
                    info[u"預定進度"] = None
                    info[u"實際進度"] = None
                projects_list.append(info)
        return projects_list
    
    @assign_parser(DOCUMENT_PARSER_REFERENCE["project_document"])
    def getAllOldProject(self, parser):
        #取得這個頁面http://cmdweb.pcc.gov.tw/pccms/owa/prjquer.lsprja?iwebcod=395250000G&iwkut=395250000&iuid=1P2721243K26242A282G
        projects_list = []

        for page in xrange(0, 1901, 100):
            response = self.getPage("POST", URL_INFORMATION["old_project_list"], {"iwebcod":self.usercode2,
                                                                                     "iuid": self.userid,
                                                                                     "iwkut": self.usercode2,
                                                                                     "ishowb": page,
                                                                                     })
            swap_doc = response.read().decode("big5", "replace")
            #取得開始
            lswap_doc = swap_doc.lower()
            seek = re.search(u"執行單位： 行政院農業部漁業署", lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            seek = re.search(u"差異</th>", lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            seek = re.search(u"</tr>", lswap_doc).end()
            swap_doc, lswap_doc = swap_doc[seek:], lswap_doc[seek:]
            #取得結尾
            seek = re.search(u"</table>", lswap_doc).start()
            if seek == 1:
                break
            swap_doc, lswap_doc = swap_doc[:seek], lswap_doc[:seek]
            
            
            tr_list = []
            while lswap_doc:
                seek_start = re.search(u"<tr>", lswap_doc).start()
                seek_end = re.search(u"</tr>", lswap_doc).end()
                tr_list.append(swap_doc[seek_start:seek_end+1])
                swap_doc, lswap_doc = swap_doc[seek_end+1:], lswap_doc[seek_end+1:]

            for n, tr in enumerate(tr_list):
                row = tr.split('</TD>')
                if len(row) == 4: continue
                info = {}
                info[u"編號"] = row[1].split(u'>')[1]
                info[u"執行機關"] = row[2].split(u'>')[1]
                info[u"標案名稱"] = row[3].split(u'>')[2].replace('</A', '')
                info[u"預定公告日期"] = None
                info[u"實際決標日期"] = None
                info[u"發包預算"] = None
                try:
                    info[u"決標金額"] = float(row[4].split(u'>')[1].replace(' ', '').replace(',', '')) * 1000
                except: info[u"決標金額"] = None
                try:
                    d = row[5].split(u'>')[1]
                    info[u"實際決標日期"] = datetime.datetime(int(d[:3]) + 1911, int(d[3:5]), int(d[5:]))
                except:
                    info[u"實際決標日期"] = None
                if len(row) == 11:
                    info[u"進度年"] = row[6].split(u'>')[1][:3]
                    info[u"進度月"] = row[6].split(u'>')[1][4:]
                    info[u"預定進度"] = row[7].split(u'>')[1].replace('%', '').replace(' ', '')
                    info[u"實際進度"] = row[8].split(u'>')[1].replace('%', '').replace(' ', '')
                else:           
                    info[u"進度年"] = None
                    info[u"進度月"] = None
                    info[u"預定進度"] = None
                    info[u"實際進度"] = None
                projects_list.append(info)
        return projects_list

    def syncPccAuditingDate(self, url):
        swap_doc = self.getPage("GET", url).read().decode("big5", "replace")
        seek = re.search(u"其他意見", swap_doc).end()
        swap_doc = swap_doc[seek:]
        seek = re.search(u"</TABLE>", swap_doc).start()
        swap_doc = swap_doc[:seek]
        auditing_dates = []
        
        swap_doc = swap_doc.split('<TR>')
        for tr in swap_doc:
            if re.search('<A', tr):
                seek = re.search(u'<A HREF=', tr).end()
                tr = tr[seek:]
                seek = re.search(u'>', tr).end()
                tr = tr[seek:]
                seek = re.search('<', tr).start()
                date = tr[:seek].split('.')
                seek = re.search(u'<TD', tr).end()
                tr = tr[seek:]
                seek = re.search(u'>', tr).end()
                tr = tr[seek:]
                seek = re.search(u'<', tr).start()
                auditing_group = tr[:seek]
                auditing_dates.append(['%s-%s-%s' % (int(date[0])+1911, date[1], date[2]), auditing_group])
        return auditing_dates

    @assign_parser(DOCUMENT_PARSER_REFERENCE["auditing_information"])
    def syncPccAuditingInformation(self, url, date, parser):
        swap_doc = self.getPage("GET", url).read().decode("big5", "replace")
        seek = re.search(u"其他意見", swap_doc).end()
        swap_doc = swap_doc[seek:]
        seek = re.search(u"</TABLE>", swap_doc).start()
        swap_doc = swap_doc[:seek]
        date = str(date).split('-')
        pcc_date = '>%s.%s.%s' % (str(int(date[0]) - 1911), date[1], date[2])
        if not re.search(pcc_date, swap_doc):
            return None
        swap_doc = swap_doc.split('<TR>')
        for tr in swap_doc:
            if re.search(pcc_date, tr):
                seek = re.search(u'<A HREF=', tr).end()
                tr = tr[seek:]
                seek = re.search(' title', tr).start()
                tr = tr[:seek]
                supervise_url = tr
                break
        swap_doc = self.getPage("GET", supervise_url).read().decode("big5", "replace")
        doc = self.parseDocument(swap_doc, parser)

        doc["plan"] = doc["plan"].replace('<font size=-1>', '').replace('</font>', '')
        doc["date"] = self.refine_pccdate(doc["date"])
        doc['place'] = doc['location'][:3].replace(u'台', u'臺')
        doc['location'] = doc['location'][3:].replace(u'台', u'臺')
        doc['project_name'] = doc['project_name'].replace(u'\n', '')
        doc['manage_unit'] = doc['manage_unit'].replace(u'\n', '')
        doc['unit'] = doc['unit'].replace(u'\n', '')
        doc['project_manage_unit'] = doc['project_manage_unit'].replace(u'\n', '')
        doc['designer'] = doc['designer'].replace(u'\n', '')
        doc['inspector'] = doc['inspector'].replace(u'\n', '')
        doc['construct'] = doc['construct'].replace(u'\n', '')
        doc['budget_price'] = float(self.refine(doc["budget_price"], "[0-9\,\.]+", "0").replace(",",""))

        contract_price = doc["contract_price"]
        seek = re.search(u"元", contract_price).end()

        doc['contract_price'] = float(self.refine(contract_price[:seek+1], "[0-9\,\.]+", "0").replace(",",""))
        if u'變更' in contract_price:
            seek = re.search(u"變更", contract_price).end()
            contract_price = contract_price[seek:]
            seek = re.search(u"<", contract_price).end()
            doc["contract_price_change"] = float(self.refine(contract_price[:seek+1], "[0-9\,\.]+", "0").replace(",",""))
        else:
            doc["contract_price_change"] = None
        
        doc["progress"] = doc['progress'].replace(u'<br>', '\n').replace('<BR>', '\n')
        
        doc["start_date"] = self.refine_pccdate(doc["start_date"])

        expected_completion_date = doc["expected_completion_date"]
        seek = re.search(u"日", expected_completion_date).end()
        doc["expected_completion_date"] = self.refine_pccdate(expected_completion_date[:seek+1])
        if u'變更' in expected_completion_date:
            seek = re.search(u"變更後至", expected_completion_date).end()
            expected_completion_date = expected_completion_date[seek:]
            seek = re.search(u"日", expected_completion_date).end()
            doc["expected_completion_date_change"] = self.refine_pccdate(expected_completion_date[:seek+1])
        else:
            doc["expected_completion_date_change"] = None

        doc["supervisors_outside"] = doc["supervisors_outside"].replace(u'(無)', '').replace(u' ', '').replace(u'\n', '')
        doc["supervisors_inside"] = doc["supervisors_inside"].replace(u'(無)', '').replace(u' ', '').replace(u'\n', '')
        doc["captain"] = doc["captain"].replace(u'(無)', '').replace(u' ', '').replace(u'\n', '')
        doc["workers"] = doc["workers"].replace(u'(無)', '').replace(u' ', '').replace(u'\n', '')
        try: 
            doc['score'] = float(doc['score'])
        except:
            doc['score'] = 0
        doc["info"] = doc["info"].replace('<br>', '\n').replace('<BR>', '\n')
        doc["merit"] = doc["merit"].replace('<br>', '\n').replace('<BR>', '\n')
        doc["quality_indicators"] = doc["quality_indicators"].replace('<br>', '\n').replace('<BR>', '\n')
        doc["advise"] = doc["advise"].replace('<br>', '\n').replace('<BR>', '\n')
        doc["other_advise"] = doc["other_advise"].replace('<br>', '\n').replace('<BR>', '\n').replace('<font color=gray>', '').replace('</font>', '')
        doc["test"] = doc["test"].replace('<br>', '\n').replace('<BR>', '\n').replace('<font color=gray>', '').replace('</font>', '')
        if u'承攬廠商' in doc['deductions']:
            seek = re.search(u'承攬廠商', doc['deductions']).end()
            point = doc['deductions'][seek:]
            seek = re.search(u'扣', point).end()
            point = point[seek:]
            seek = re.search(u'點', point).start()
            point = point[:seek]
            doc['deduction_c_point'] = point
        else:
            doc['deduction_c_point'] = 0
        if u'監造廠商' in doc['deductions']:
            seek = re.search(u'監造廠商', doc['deductions']).end()
            point = doc['deductions'][seek:]
            seek = re.search(u'扣', point).end()
            point = point[seek:]
            seek = re.search(u'點', point).start()
            point = point[:seek]
            doc['deduction_i_point'] = point
        else:
            doc['deduction_i_point'] = 0
        return doc