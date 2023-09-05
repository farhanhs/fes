# -*- coding: utf-8 -*-
import sys
print sys.path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.conf import settings


from supervise.models import ErrorContent



class Command(BaseCommand):
    help = 'Create the permissions for project, dailyreport modules'


    def handle(self, *args, **kw):
        errors = [
            {"no": "4.01.01", "point": [u'-1',u'-2'], "introduction": u"契約內□未編列品管費用，或□品管人員訂有專職及人數等規定者，未以人月量化編列，或□以百分比法編列之比率不符規定，或□未編列廠商材料設備之檢驗或系統功能運轉測試費用，或□未編列監造單位材料設備之抽驗費用，或□未編列環境保護相關經費，或□未規劃臨時照明及臨時給排水設施，或□未編列安全衛生經費"},
            {"no": "4.02.03.04", "point": [u'±2',u'±4'], "introduction": u"有無抽查施工作業及抽驗材料設備，並填具抽查(驗)紀錄表，或□製作材料設備檢（試）驗管制總表管控，或□對檢（試）驗報告判讀認可，或□確認檢（試）驗報告內容正確性，或□落實執行"},
            {"no": "4.02.03.08", "point": [u'±1',u'±2'], "introduction": u"有無依契約規定填報監造報表，或□有無落實記載，或□使用規定格式報表"},
            {"no": "4.03.02.03", "point": [u'-1',u'-2'], "introduction": u"□未訂定各分項工程施工要領，或□未符合需求"},
            {"no": "4.03.02.04", "point": [u'-1',u'-2'], "introduction": u"□未訂定各分項工程品質管理標準，或□未符合需求"},
            {"no": "4.03.02.06", "point": [u'-1',u'-2'], "introduction": u"工程標的含運轉類機電設備者，□未依單機測試、系統運轉、整體功能試運轉等分別訂定檢驗程序及標準，或□無試運轉及測試計畫書"},
            {"no": "4.03.02.12", "point": [u'-1',u'-2'], "introduction": u"□未訂定材料設備送審管制總表、材料設備檢（試）驗管制總表、自主檢查表等相關表單，或□未符合需求"},
            {"no": "4.03.05", "point": [u'-3',u'-5'], "introduction": u"□對材料檢(試)驗未落實執行，或□對檢（試）驗報告未予判讀，或□檢（試）驗報告內容誤植；或□未製作材料設備送審管制總表、材料設備檢（試）驗管制總表，或□未符合工程需求"},
            {"no": "4.03.08", "point": [u'-2',u'-4'], "introduction": u"新臺幣2,000萬元以上工程或契約明訂者，品管人員□新設或異動時未提報登錄表，或□設置人數不符規定，或□品管人員未專職（不得兼職其他職務），或□逾期未回訓"},
            {"no": "5.07.04.26", "point": [u'-1',u'-2'], "introduction": u"□發電機油箱未依規定設置防油堤、集油坑及接地，或□透氣管未配至戶外，或□未設置不銹鋼濾網，或□連接發電機之各種管路未使用軟管"},
            {"no": "5.07.04.28", "point": [u'-1',u'-2'], "introduction": u"□高低壓配電盤、分電箱、電氣設備防塵防水IP等級不合規範，或□未設置銘牌，或□電氣設備、管路施工中未防護"},
            {"no": "5.07.05.07", "point": [u'-1',u'-2'], "introduction": u"□管路吊架不穩固，或□固定架間距未依規定施作，或□螺栓、法蘭、墊片等，未依規定設置，或□不同金屬互相接觸未適當隔絕"},
            {"no": "5.09.13", "point": [u'-1',u'-2'], "introduction": u"未依契約規定設置臨時用電(含照明)或臨時給排水設施"},
            {"no": "5.14.06.07", "point": [u'-1',u'-2'], "introduction": u"使勞工於局限空間從事作業前，未先確認該局限空間內有無可能引起勞工缺氧、中毒、感電、塌陷、被夾、被捲及火災、爆炸等危害，並據以訂定危害防止計畫"},
            {"no": "5.14.06.08", "point": [u'-1',u'-2'], "introduction": u"使勞工於局限空間從事作業時，□未建立勞工進入許可作業，或□未對勞工之進出確認、點名登記作成紀錄"},
            {"no": "5.14.06.09", "point": [u'-2',u'-4'], "introduction": u"使勞工從事局限空間作業，當作業區域超出監視人員目視範圍時，□未使勞工佩戴安全帶及可偵測人員活動情形之裝置；或□未置備可以動力或機械輔助吊升之緊急救援設備"},
            {"no": "6.01.10", "point": [u'-1',u'-2'], "introduction": u"施工進度未依項目分別計算再加權統，不符 合現場實際施工進度"},
            {"no": "6.01.11", "point": [u'-1',u'-2'], "introduction": u"主辦機關、監造單位或廠商之工程進度不一致"},
            {"no": "6.01.12", "point": [u'-1',u'-2'], "introduction": u"施工預定進度表 （或網圖） ，未明確標示要徑不易掌控作業進度"},
            {"no": "6.01.99", "point": [u'-1',u'-2'], "introduction": u"其他施工進度問題 其他施工進度問題"},
        ]

        for e in errors:
            try:
                ec = ErrorContent.objects.get(no=e["no"])
            except:
                ec = ErrorContent(no=e["no"])
            ec.introduction = e["introduction"]
            ec.save()

