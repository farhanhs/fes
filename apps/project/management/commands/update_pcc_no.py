# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os, datetime, decimal, random
from fishuser.models import *
from django.conf import settings
import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate


def TODAY(): return datetime.date.today()

class Command(BaseCommand):
    help = u"放入工程會編號並同步資料"

    def handle(self, *args, **kw):
        projects = [
            [102,u"補助金門縣新湖漁港冷凍庫改善計畫",u"002"],
            [106,u"八斗子觀光漁港魚貨直銷中心公共設施整修工程",u"1285"],
            [101,u"東石鄉塭港養殖漁業生產區頂寮排水改善工程",u"9060"],
            [101,u"台北市萬大路魚類批發市場路面改善計畫",u"10103"],
            [100,u"永興養殖區2號水門第一南北進排水路改善工程",u"10255"],
            [99,u"栗子崙魚塭排水改善工程",u"10289"],
            [100,u"臺東縣伽藍漁港卸魚機整建工程",u"100004"],
            [100,u"苑裡漁港安檢所前及中堤碼頭塌陷修復工程",u"100083"],
            [101,u"烈嶼鄉上林出海口道路整建工程",u"101031"],
            [101,u"通霄漁港觀景台下碼頭及港區道路掏空修復工程",u"101201"],
            [102,u"龍鳳漁港外航道淤砂疏浚工程",u"102339"],
            [102,u"外埔漁港外泊地航道淤砂疏浚工程",u"102340"],
            [102,u"苑裡漁港泊地航道疏浚工程",u"102355"],
            [102,u"通霄漁港簡易浮動碼頭增設工程",u"102414"],
            [103,u"花蓮魚市場重建工程",u"103002"],
            [103,u"苑港漁港景觀橋周邊廣場地坪改善工程",u"103217"],
            [103,u"龍鳳漁港外航道淤砂疏浚工程",u"103306"],
            [103,u"苑裡漁港泊地航道疏浚工程",u"103307"],
            [103,u"外埔漁港外泊地航道淤砂疏浚工程",u"103308"],
            [103,u"通霄漁港泊地航道疏浚工程",u"103309"],
            [103,u"苑港漁港泊地航道疏浚工程",u"103310"],
            [103,u"外埔漁港南堤碼頭階梯改善工程",u"103317"],
            [104,u"104年度苑裡漁港泊地航道疏浚工程(不含設計)(第一年)",u"104234"],
            [105,u"105年度龍鳳漁港淤砂疏浚工程(不含設計)(第二年)",u"104236"],
            [105,u"105年度苑港漁港泊地航道疏浚工程(不含設計)(第二年)",u"104237"],
            [106,u"苗栗魚市場環境衛生改善工程",u"106003"],
            [107,u"107年苑港漁港漁港泊地航道淤砂疏浚工程(不含設計工作)(第二年)",u"106200"],
            [106,u"106年苑港漁港泊地航道淤砂疏浚工程(不含設計工作)(第一年)",u"106200"],
            [107,u"107年通霄漁港泊地航道淤砂疏浚工程(不含設計工作)(第二年)",u"106205"],
            [106,u"106年通霄漁港泊地航道疏浚工程(不含設計工作)(第一年)",u"106205"],
            [107,u"107年苑裡漁港泊地航道淤砂疏浚工程(不含設計工作)(第二年)",u"106206"],
            [106,u"106年苑裡漁港泊地航道淤砂疏浚工程(不含設計工作)(第一年)",u"106206"],
            [100,u"中芸漁港東防波堤延長工程",u"980914"],
            [99,u"水井區海水進水系統工程",u"990929"],
            [99,u"前鎮北、中碼頭地坪整建及港區設施改善工程",u"994017"],
            [100,u"安平直銷中心後續整修工程",u"1001111"],
            [101,u"台西出海道路改善工程",u"1010808"],
            [102,u"姑寮出海道路改善工程(二)",u"1020627"],
            [103,u"芳苑南哨出海尾段出海路改善工程",u"1030321"],
            [103,u"新寶11班哨支線出海道路改善工程",u"1030322"],
            [103,u"福寶出海道路改善工程",u"1030323"],
            [103,u"103年梧棲漁港魚貨直銷中心餐飲區建物整修暨附屬設施改善工程(第一年)(代辦)",u"1031219"],
            [103,u"永新漁港疏浚工程",u"1036013"],
            [103,u"永華養殖生產區-草田溝魚塭排水改善工程",u"1036030"],
            [103,u"中芸漁港疏浚工程",u"1036032"],
            [103,u"彌陀養殖魚塭集中區東西向排水工程",u"1036033"],
            [105,u"埔心魚市場冷凍倉儲興建工程",u"1041109"],
            [104,u"新建冷凍庫設備",u"1041204"],
            [106,u"106年蚵子寮魚貨直銷中心新建工程(不含規劃設計工作)",u"1046011"],
            [105,u"105年蚵子寮魚貨直銷中心新建工程(不含規劃設計工作)(第二年)",u"1046011"],
            [104,u"埔心魚市場地坪改善工程",u"1051212"],
            [105,u"105年度興達漁港加油碼頭修復工程(不含設計監造工作)",u"1056031"],
            [106,u"永華養殖漁業生產區(舊港口段16-9)魚塭土溝改善工程(第二年)",u"1056037"],
            [106,u"永華養殖漁業生產區(復興段369)草田溝排水西支線魚塭土溝改善工程(第二年)",u"1056038"],
            [105,u"永華養殖漁業生產區(復興段369)草田溝排水西支線魚塭土溝改善工程",u"1056038"],
            [106,u"105年彌陀養殖魚塭集中區東西向排水工程(第二年)",u"1056041"],
            [105,u"105年彌陀養殖魚塭集中區東西向排水工程",u"1056041"],
            [107,u"107年中芸漁港東防波堤延長工程(第二期)(第三年)",u"1056055"],
            [106,u"106年中芸漁港東防波堤研長工程(第二期)(第二年)",u"1056055"],
            [106,u"(106)漢寶哨出海道路改善工程",u"1060518"],
            [106,u"106年金寧鄉出海道路新建工程",u"1060603"],
            [106,u"106年梧棲漁港娛樂碼頭木棧平台改善工程(不含設計工作)",u"1060711"],
            [106,u"106年梧棲漁港魚貨直銷中心周遭環境改善工程(不含設計監造)(第一年)(委託代辦)",u"1061206"],
            [106,u"106年中芸漁港疏浚工程(含監造工作)",u"1066017"],
            [106,u"106年度前鎮漁港防舷材汰換工程",u"1066019"],
            [106,u"高雄市永華養殖區共同給水工程",u"1066030"],
            [100,u"淡水第二漁港全國漁民活動中心興建工程(含規劃設計)",u"9811015"],
            [99,u"正濱漁市場及污水處理等相關設施",u"9811130"],
            [99,u"安平漁港整體規劃設計工作",u"9811230"],
            [99,u"八斗子漁港港區疏浚工程",u"9910317"],
            [99,u"「加速辦理地層下陷地區排水環境改善示範計畫」委託專案管理計畫",u"9910323"],
            [99,u"烏石漁港魚市場及直銷中心外觀更新整建暨相關設施改善興建工程委託設計監造工作",u"9910524"],
            [99,u"新店養殖區中路聯絡道路（北段）整建工程",u"9910615"],
            [99,u"八斗子漁港海功號試驗船整修暨景觀改造工程",u"9910824"],
            [100,u"中洲漁港老舊碼頭改善工程",u"10042033"],
            [100,u"中芸漁港疏浚工程",u"10042042"],
            [100,u"永安區草田溝排水整治工程-草田溝主線部分",u"10042053"],
            [100,u"彌陀區養殖漁業生產區第3期供水及排水改善工程-供水部份",u"10042055"],
            [100,u"彌陀區養殖漁業生產區第3期供水及排水改善工程-排水部份",u"10042056"],
            [101,u"蚵子寮漁港疏浚工程",u"10142012"],
            [101,u"彌陀漁港疏浚工程",u"10142013"],
            [101,u"興達港遠洋魚市場污水處理廠興建工程",u"10142017"],
            [101,u"梓官區漁會魚市場重建工程",u"10142026"],
            [101,u"前鎮漁港公務碼頭碰墊更新及設置車阻護欄工程",u"10142034"],
            [101,u"前鎮魚市場污水處理廠新建工程",u"10142045"],
            [101,u"中芸漁港辦公室新建工程",u"10142057"],
            [102,u"102年度促進養殖漁業與環境和諧計畫-高雄市",u"10242021"],
            [100,u"雙春生產區擋土牆排水改善工程",u"99070101"],
            [101,u"青山漁港魚貨拍賣場東棟建築物及將軍漁港東棟拍賣場修繕工程",u"101102301"],
            [105,u"北門保安生產區排水溝堤後續改善工程",u"105021703"],
            [106,u"永興養殖區3號水門第二南北進排水路106年度改善工程",u"1050011653"],
            [100,u"長濱漁港疏浚及設施維護改善工程",u"1.0015E+11"],
            [101,u"復國墩漁港航道及泊地浚挖工程",u"101110110010"],
            [101,u"臺東縣各漁港安檢防舷材及港區告示牌設置工程",u"1.0115E+11"],
            [101,u"綠島漁港漁港設施改善工程",u"1.0115E+11"],
            [101,u"公館漁港防波堤及碼頭修復工程",u"1.0115E+11"],
            [101,u"長濱漁港疏浚工程",u"1.0115E+11"],
            [101,u"開元漁港港區照明改善工程",u"1.0115E+11"],
            [102,u"十大經典魅力漁港環境維護及改善計畫-新港漁港",u"1.0215E+11"],
            [103,u"大武漁港疏浚工程",u"1.0315E+11"],
            [103,u"長濱漁港疏浚工程",u"1.0315E+11"],
            [105,u"105年度臺東縣大武漁港疏浚養灘及環境營造-大武漁港疏浚及侵蝕海岸保護工程",u"105150310158"],
            [105,u"105年度臺東縣漁業觀光環境暨漁業設施振興計畫-新港漁港魚市場環境改善工程",u"105150310316"],
            [105,u"105年度臺東縣漁業觀光環境暨漁業設施振興計畫-臺東縣伽藍(富岡)漁港曳船道整建工程",u"105150310336"],
            [105,u"105年度臺東縣大武漁港疏浚養灘及環境營造-大武漁港港區聯絡景觀疏砂橋新建工程",u"105150310385"],
            [105,u"105年度臺東縣漁業觀光環境暨漁業設施振興計畫-新港漁港深水碼頭闢建工程",u"105150310482"],
            [106,u"106年新港漁港曳船道修繕工程(不含設計監造工作)",u"106150310328"],
            [106,u"106年度新港魚市場衛生安全改善工程",u"106150310586"],
            [100,u"興達漁港碼頭鋪面暨路燈汰換工程",u"000991124-1"],
            [100,u"苑港漁港跨海景觀橋暨週邊景觀改善工程",u"00125a"],
            [101,u"外埔漁港疏濬工程",u"01159a"],
            [101,u"龍鳳漁港北碼頭及南碼頭塌陷修復工程",u"01210a"],
            [100,u"東港鹽埔漁港設置車阻及標線等安全措施工程",u"022-1000826-1"],
            [100,u"屏東縣東港漁港停車場興建工程",u"022-1000831"],
            [100,u"漁福漁港碼頭整修工程",u"022-1000908"],
            [100,u"小琉球及琉球新漁港輪胎防舷材修繕工程",u"022-1001128"],
            [101,u"東港漁港漁會大樓旁碼頭整建工程",u"022-1010614"],
            [100,u"水利村及塭豐漁港疏浚工程",u"022-1011004"],
            [100,u"林邊養殖區海水供水工程",u"022-1011108"],
            [102,u"塭豐養殖漁業生產區橋樑及道路改善工程",u"022-1020925A1"],
            [102,u"番子崙及東海養殖漁業生產區道路排水改善工程",u"022-1021128P1"],
            [103,u"塭豐海水供應系統計量設備工程",u"022-1021202P1"],
            [103,u"下埔頭養殖漁業生產區道路改善工程",u"022-1030707A1"],
            [103,u"番子崙養殖漁業生產區排水護岸工程",u"022-1030707A2"],
            [103,u"塭豐養殖漁業生產區道路加高及AC工程",u"022-1030707A3"],
            [103,u"水利村及塭豐漁港港區及航道清疏工程",u"022-1030811A1"],
            [104,u"櫻花蝦作業碼頭改善(第二年)",u"022-1030910P1"],
            [103,u"大庄養殖漁業生產區海鷗一~二號橋等路面改善工程",u"022-1030918A1"],
            [104,u"東港漁港停車場2、3樓停車場暨景觀天橋興建工程(不含設計監造)(第二年)",u"022-1031203P1"],
            [103,u"東港漁港停車場2、3樓停車場暨景觀天橋興建工程",u"022-1031203P1"],
            [104,u"104年水利村及塭豐漁港港區及航道清疏工程",u"022-1040730P1"],
            [106,u"屏東縣塭豐養殖漁業生產區海水供應系統擴充工程",u"022-1050910"],
            [106,u"106年度水利村及塭豐漁港港區及航道清疏工程(第二年)",u"022-1051024-1"],
            [106,u"106年屏東縣枋寮漁港木棧道改建工程(不含設計監造)",u"022-1060414-1"],
            [106,u"106年塭豐養殖漁業生產區十全路道路加高工程",u"022-1060511-1"],
            [106,u"106年度琉球新漁港西防波堤堤頭修復工程(不含設計監造)(第一年)",u"022-1061115"],
            [106,u"106年水利村及塭豐漁港疏浚工程(第一年)",u"022-1061213-1"],
            [102,u"通霄漁港泊地航道疏浚工程",u"02294a"],
            [100,u"鹽埔漁港北防砂堤後續興建工程",u"022-991206"],
            [99,u"試驗性海水取水方式設置及研究",u"022-991216-2"],
            [102,u"龍鳳漁港增設消波塊工程",u"02318a"],
            [102,u"外埔漁港南北堤修護及港區公共廁所整修工程",u"02329a"],
            [102,u"龍鳳漁港南堤及外埔漁港東堤浮動碼頭增設工程",u"02330a"],
            [105,u"105年通霄漁港泊地航道疏浚工程(不含設計)(第二年)",u"05035a"],
            [107,u"107年外埔漁港淤砂疏浚工程(不含設計工作)(第二年)",u"06139a"],
            [106,u"106年外埔漁港淤砂疏浚工程(不含設計工作)(第一年)",u"06139a"],
            [107,u"107年龍鳳漁港淤砂疏浚工程(不含設計工作)(第二年)",u"06140a"],
            [106,u"106年龍鳳漁港淤砂疏浚工程(不含設計工作)(第一年)",u"06140a"],
            [98,u"羅厝漁港南防波堤及復國墩漁港東消波堤改善工程",u"098110110181_1"],
            [99,u"青山漁港西南航道疏浚工程",u"099G3D0001729"],
            [99,u"北門鄉南興生產區排水改善工程",u"099G3D0002840"],
            [100,u"擴建梧棲漁港小船浮動碼頭工程",u"100-02-23"],
            [100,u"永安漁港鋪面、步道及照明改善工程",u"1000325-AA1"],
            [100,u"梧棲漁港鋪面暨路燈汰換工程",u"100-06-27"],
            [100,u"永安漁港夜間照明改善工程",u"1000719-AA1"],
            [100,u"梧棲漁港安檢所前浮動碼頭改建工程",u"100-08-22"],
            [100,u"竹圍漁港漁具倉庫修復工程",u"1000908-AA1"],
            [100,u"新港南養殖區道路排水整建工程",u"10011-15"],
            [100,u"蚶寮養殖區144線西側進排水路整建工程",u"10011-16"],
            [100,u"青蚶養殖區台17線旁(二)道路排水整建工程",u"10011-17"],
            [100,u"下崙養殖區南6路進排水路整建工程",u"10011-18"],
            [99,u"下湖口養殖區南區排水護岸及道路整建(2)工程",u"1001A10036"],
            [100,u"箔子寮漁港西碼頭西側道路加高整修工程",u"1001A10038"],
            [100,u"箔子寮漁港港區防衝撞車阻及道路整建工程",u"1001A10046"],
            [100,u"箔子寮漁港航道緊急疏浚",u"1001A20025"],
            [100,u"崙尾灣漁港港內疏浚工程",u"1001OAG034"],
            [100,u"新竹漁港基本設施維護改善工程",u"100A159"],
            [100,u"北門漁港航道疏浚工程",u"100AGR0096"],
            [100,u"安平漁港上架場船筏設施工程",u"100AGR0100"],
            [100,u"安平漁港近海泊區疏浚工程",u"100AGR0102"],
            [100,u"永安區戰車壕溝排水整治工程",u"100B006"],
            [100,u"下庄漁港新建漁船維修用曳船道",u"100GA789A2"],
            [100,u"下庄漁港南側碼頭由斜坡式改採直立式工程",u"100GE790A2"],
            [101,u"王功漁港港區內設施改善工程",u"101-0020604-022-1-1"],
            [101,u"永安漁港港口緊急疏浚工程",u"1010531-AA1"],
            [101,u"永安漁港觀光漁市週邊路面改善工程",u"1010531-AA2"],
            [101,u"竹圍漁港航道口緊急疏浚工程",u"1010608-AA2"],
            [101,u"漢寶140班哨出海道路改善工程",u"1010808-2"],
            [101,u"竹圍漁港南岸公共設施改善工程(一)",u"1011001-AA1"],
            [101,u"臺中市松柏及五甲漁港新建護欄工程",u"101-11-26"],
            [101,u"梧棲漁港北側公共廁所整建工程",u"101-12-03"],
            [101,u"下崙養殖區南9路進排水路整建工程",u"1011A10076"],
            [101,u"下崙養殖區羊稠厝堤防2K+305.5進排水路整建工程",u"1011A10077"],
            [101,u"公司寮漁港西堤破損整修工程",u"101404c"],
            [101,u"苑港漁港及苑裡漁港簡易浮動碼頭興建工程",u"101489c"],
            [101,u"梧棲漁港安檢所以西之碼頭沿岸設置護欄",u"101-7-2"],
            [101,u"彌陀區漁會製冰廠整建工程",u"101A02"],
            [101,u"新竹漁港基本設施及公共設施整建工程(含新竹漁港碼頭下陷修復及水溝整建等)",u"101A145"],
            [101,u"八斗子漁港碼頭及道路鋪面整修工程",u"101A225"],
            [101,u"八斗子漁港曳船道整建工程",u"101A226"],
            [101,u"正濱漁港港區加冰設施等設置工程",u"101A268"],
            [101,u"北門漁港共同航道出海口南側導航燈修復工程",u"101AGR0047"],
            [101,u"網寮及白水湖漁港共用航道疏浚工程",u"101GA639A2"],
            [101,u"白水湖漁港碼頭及周邊道路加高工程",u"101GC618A2"],
            [101,u"布袋漁港航道疏浚工程",u"101GJ637A2"],
            [102,u"梧棲漁港碼頭告示牌及看板、西側公廁修繕及碼頭蓋板更新",u"102-1-25"],
            [102,u"大武漁港區域疏浚工程",u"102150310329_1"],
            [102,u"龍鳳漁港港區增設防舷材工程",u"102614c"],
            [102,u"102年度新竹漁港疏浚工程(2)",u"102A079"],
            [102,u"102年度海山漁港疏浚工程",u"102A163"],
            [102,u"外木山漁港外廓防波堤加拋消波塊工程",u"102A170"],
            [103,u"新竹漁港碼頭及週邊鋼構除鏽油漆工程",u"102A187"],
            [102,u"八斗子及正濱漁港輪胎碰墊修復工程",u"102A216"],
            [102,u"八斗子漁港第一泊區部分碼頭鋪面改善工程",u"102A224"],
            [102,u"八斗子海功號油漆暨週邊設施改善工程",u"102A226"],
            [102,u"安平漁港觀光直銷中心站碼頭工程",u"102AGR0051"],
            [102,u"下山漁港泊地疏浚工程",u"102AGR0062"],
            [102,u"青山漁港內港停泊區疏浚工程",u"102AGR0065"],
            [102,u"將軍漁港漁貨拍賣場（中西棟）整修工程",u"102AGR0068"],
            [102,u"北門區雙春生產區臨急水溪排水後續改善工程",u"102AGR0078"],
            [102,u"七股養殖區公共排水設施工程",u"102AGR0078"],
            [102,u"七股區龍山里176線旁養殖漁業進排水路改善工程",u"102AGR0078"],
            [102,u"北門區雙春生產區慈烏山莊排水改善工程",u"102AGR0078"],
            [102,u"北門雙春生產區西側道路旁排水改善工程",u"102AGR0078"],
            [102,u"將軍漁港航道疏浚工程",u"102AGR0080"],
            [102,u"新店養殖區道路改善工程",u"102GA857A2"],
            [102,u"西新店養殖區道路改善工程",u"102GC856A2"],
            [102,u"西好美里養殖區排水改善工程",u"102GE854A2"],
            [103,u"下庄漁港北側碼頭加高工程（二）",u"102GJ595A2"],
            [102,u"下庄漁港北側碼頭加高工程（一）",u"102GJ595A2"],
            [102,u"塭港養殖區道路改善工程",u"102GJ855A2"],
            [102,u"辦理金沙鎮洋山、劉澳及中蘭出海道路整建工程",u"102JS007"],
            [103,u"永興養殖區2號水門進排水改善工程(第五期)",u"103-0020604-034-1-1"],
            [103,u"王功燈塔出海道路設施工程",u"1030317-1"],
            [103,u"十大經典魅力漁港環境維護及改善計畫-深澳漁港",u"1030319A"],
            [103,u"磺港漁港疏浚工程",u"1030403A"],
            [103,u"永安漁港泊地及航道疏浚工程",u"1030502-AA2"],
            [103,u"竹圍漁港泊地及航道疏浚工程",u"1030502-AA3"],
            [103,u"十大經典魅力漁港環境維護及改善計畫-淡水第二漁港",u"1030509C"],
            [103,u"十大經典魅力漁港環境維護及改善計畫-淡水第一漁港",u"1030520D"],
            [103,u"十大經典魅力漁港環境維護及改善計畫-東澳漁港",u"1030604B"],
            [103,u"松柏漁港港區疏浚及港埠設施修繕工程",u"103-06-05"],
            [103,u"永安漁港北岸堤防補強工程",u"1030807-AA2"],
            [103,u"金寧鄉古寧頭北山出海道路整建工程（二期）",u"1030926A"],
            [103,u"下崙養殖區5米路（二）道路排水整建工程",u"1031A10050"],
            [103,u"三條崙漁港內突堤新建工程",u"1031A10059"],
            [104,u"104年台子村漁港港區加高整建工程（第二年）",u"1031A10073"],
            [103,u"台子村漁港港區加高整建工程",u"1031A10073"],
            [104,u"104年雲林縣箔子寮漁港航道改善工程（不含設計監造工作）（第二年）",u"1031A10121"],
            [103,u"103年雲林縣箔子寮漁港航道改善工程（不含設計監造工作）（第一年）",u"1031A10121"],
            [103,u"八斗子漁港西防波堤補拋消波塊工程",u"103A058"],
            [103,u"長潭里漁港外防波堤加拋消波塊工程",u"103A082"],
            [103,u"新竹漁港上架場曳船道及台車修護工程（不含設計監造)",u"103A138"],
            [103,u"青山漁港漁貨拍賣場相關設施改善工程（不含規劃設計）",u"103AGR0027"],
            [103,u"北門區海埔養殖生產區產業道路旁擋土牆加強工程",u"103AGR0054"],
            [103,u"北門區雙春養殖生產區排水溝堤加高工程",u"103AGR0054"],
            [103,u"北門區海埔養殖生產區5號排水路加高工程",u"103AGR0054"],
            [103,u"北門區保安養殖生產區排水溝堤改善工程",u"103AGR0054"],
            [104,u"104年網寮漁港內側護岸工程(不含設計監造工作)(第二年)",u"103GE609A2"],
            [103,u"103年網寮漁港內側護岸工程（不含設計監造工作）（第一年）",u"103GE609A2"],
            [104,u"坡頭漁港疏浚工程（不含設計監造）",u"104001B"],
            [105,u"105年度彰化漁港開發案近程(可開港營運第一階段)計畫(第二年)-彰化漁港北防風林填築及圍堤工程(第一階段)",u"104-0020604-045-1-1"],
            [105,u"105年度崙尾灣漁港清淤工程(第二年)",u"104-0020604-049-1-1"],
            [105,u"104年度崙尾灣漁港清淤工程",u"104-0020604-049-1-1"],
            [105,u"漢寶養殖區十三戶一中排改善工程暨漢寶養殖區十三戶第三排一中排改善工程",u"104-0020604-072-1-1"],
            [104,u"淡水第二漁港浮動碼頭改善工程（不含設計工作）",u"1040521A"],
            [104,u"104漢寶哨出海道路改善工程",u"1040804-3"],
            [104,u"104年度永安漁港公共設施改善工程",u"1040819-AA1"],
            [105,u"新港北養殖區北興街道路排水整建工程",u"1041A10060"],
            [104,u"下崙養殖區南7路進排水路整建工程",u"1041A10061"],
            [104,u"104年度新竹漁港基本設施(港區碼頭)整建工程(不含設計監造)",u"104A048"],
            [104,u"八斗子漁港扒網漁船整網區工程",u"104A081"],
            [104,u"北門漁港航道疏浚工程",u"104AGR0035"],
            [104,u"青山漁港魚市場突堤西面碼頭整建工程",u"104AGR0042"],
            [104,u"東石漁港及其外航道疏浚工程(不含設計監造)",u"104GE151A2"],
            [105,u"金沙鎮西園西江、西園三獅山等出海口道路整建工程",u"104KS0708"],
            [105,u"105年度王功漁港設施修繕工程(不含設計監造)",u"105-0020604-013-1-1"],
            [105,u"漢寶養殖區八洲排水一中排改善工程",u"105-0020604-045-1-1"],
            [105,u"105年深澳漁港西堤改善及疏浚工程(不含設計監造工作)",u"1050401C"],
            [105,u"105年度竹圍漁港泊地及航道疏浚工程",u"1050425-AA1"],
            [105,u"永安漁港航道及泊地疏浚工程",u"1050425-AA2"],
            [106,u"青蚶養殖區青蚶橋南駁坎整建工程(第二年)",u"10509-2"],
            [105,u"青蚶養殖區青蚶橋南駁坎整建工程",u"10509-2"],
            [106,u"下崙養殖區羊稠厝支線道路排水整建工程(二期)(第二年)",u"10509-4"],
            [105,u"下崙養殖區羊稠厝支線道路排水整建工程(二期)",u"10509-4"],
            [103,u"下崙養殖區羊稠厝支線道路排水整建工程",u"10509-4"],
            [106,u"台子養殖區產業道路改善工程(第二年)",u"10509-5"],
            [105,u"台子養殖區產業道路改善工程",u"10509-5"],
            [106,u"新港北養殖區道路排水改善工程(第二年)",u"10509-8"],
            [105,u"新港北養殖區道路排水改善工程",u"10509-8"],
            [106,u"106年度竹圍漁港周邊改善工程(第二年)",u"1051027-AA1"],
            [105,u"105年度竹圍漁港周邊改善工程(第一年)",u"1051027-AA1"],
            [105,u"台子養殖區路面改善工程",u"1051A10070"],
            [102,u"苑港漁港景觀橋亮化工程",u"10553B"],
            [106,u"105年度「提升魚市場衛生品質」-蚵仔寮魚市場HACCP管制點圍籬及地坪整修工程」",u"105A0006"],
            [105,u"105年正濱漁港泊區及八斗子漁港曳船道周邊水域疏浚工程(不含設計監造工作)",u"105A045"],
            [106,u"106年度新竹漁港疏浚工程(第二年)",u"105A185"],
            [105,u"105年度新竹漁港疏浚工作（第一年）",u"105A185"],
            [105,u"105年度新竹漁港疏浚工程",u"105A185"],
            [105,u"105年青山漁港西南航道疏浚工程(不含設計工作)",u"105AGR0077"],
            [106,u"105年度促進養殖漁業與環境和諧計畫等五件工程",u"105AGR0092"],
            [105,u"塭港漁塭養殖區頂寮道路拓寬改善工程",u"105GA280A2"],
            [105,u"塭港漁塭養殖區頂寮道路拓寬改善工程",u"105GA280A2"],
            [105,u"105年布袋漁港護岸及碼頭加高工程（第二年）",u"105GC095A2"],
            [104,u"104年布袋漁港護岸及碼頭加高工程（第一年）",u"105GC095A2"],
            [105,u"105年度東石漁港漁人碼頭路燈增設及路面改善工程",u"105GC475A2"],
            [105,u"西新店養殖區道路拓寬改善工程",u"105GE281A2"],
            [105,u"105年白水湖漁港航道疏浚工程（不含設計監造）",u"105GJ126A2"],
            [105,u"白水湖漁港航道疏浚工程",u"105GJ126A2"],
            [106,u"106年度彰化漁港開發案近程(可開港營運第一階段)計畫(第三年)-近程第一階段防波堤及內港口開闢興建工程",u"106-0020604-009-1-1"],
            [106,u"永興養殖區2號水門進排水改善工程(第七期)",u"106-0020604-018-1-1"],
            [106,u"106年度彰化漁港開發案近程(可開港營運第一階段)計畫(第三年)-近程第一階段漁筏停泊區及浮動碼頭等興建工程",u"106-0020604-055-1-1"],
            [106,u"106年度竹圍漁港南岸積砂改善工程",u"1060223-AA1"],
            [106,u"106年野柳及萬里漁港泊地疏浚工程",u"1060511B"],
            [106,u"106年磺港漁港外泊地碼頭改善工程(第一年)",u"1060512A"],
            [106,u"106年龍鳳漁港拱橋式上架場天車整修工程(不含設計監造工作)",u"106057c"],
            [106,u"106年度竹圍漁港北岸整體景觀改善工程",u"1060616-AA1"],
            [106,u"蚶仔寮養殖區擋土牆及道路改善工程",u"10606-7"],
            [106,u"106年松柏漁港魚貨多功能集貨場暨周邊港埠設施新建工程(第一年)",u"106-08-02"],
            [106,u"106年度永安漁港漁貨直銷中心建築牆面整修及停車場車道改善工程",u"1060815-AA1"],
            [106,u"106年度梧棲漁具整網場整建工程",u"106-09-08"],
            [106,u"全國漁會三重示範魚市場環境衛生及週邊設施改善工程",u"106-10"],
            [106,u"106年箔子寮漁港舊港區凸堤碼頭加高工程",u"1061A10022"],
            [106,u"106年三條崙漁港港區加高整建工程(第三期)(不含設計工作)",u"1061A10042"],
            [106,u"下湖口養殖區擋土牆改善工程",u"1061A10059"],
            [106,u"新港北養殖區排水路加高及水門改善工程",u"1061A10060"],
            [106,u"106年五條港漁港碼頭加高工程(不含設計工作)(第一年)",u"1061A10064"],
            [106,u"106年度三條崙漁港港區加高整建工程(第二期)(不含設計工作)(第一年)",u"1061A10102"],
            [106,u"106年八斗子漁港東外廓防波堤沉箱縫修復及補強工程(不含設計)",u"106A055"],
            [106,u"106年海功號油漆工程",u"106A075"],
            [106,u"106年八斗子漁港港區道路整修工程",u"106A219"],
            [106,u"106年正濱漁港不鏽鋼欄杆整修工程",u"106A220"],
            [106,u"106年度將軍漁港航道疏浚工程(不含設計監造工作)",u"106AGR078"],
            [106,u"106年安平漁港碧海碼頭鋪面及設施更新工程(第一年)",u"106AGR088"],
            [107,u"107年將軍漁港曳船道上架設施修繕工程(不含設計監造)",u"106AGR095"],
            [106,u"「106年度將軍漁港曳船道上架設施修繕工程(不含設計監造工作)(第一年)」計劃",u"106AGR095"],
            [106,u"西新店養殖區道路路面改善工程",u"106GC402A2"],
            [106,u"106年度布袋、塭港及網寮漁港起卸設施新建工程",u"106GC486A2"],
            [106,u"106年度布袋漁港航道疏浚工程",u"106GE400A2"],
            [106,u"106年度下庄漁港上架平台新建工程(不含設計監造工作)",u"106GJ225A2"],
            [105,u"105年度下庄漁港上架平台新建工程",u"106GJ225A2"],
            [103,u"苗栗通霄海水養殖生產區海水供水及公共設施統包工程",u"30053B"],
            [98,u"台西漁港疏浚工程",u"971A20039"],
            [98,u"下湖口養殖區北區防潮堤排水單側護岸整建(2)工程",u"9811009c"],
            [98,u"金湖漁港疏浚工程",u"981A20036"],
            [98,u"台子村漁港泊地疏浚工程",u"981A20037"],
            [100,u"八斗子漁港遊艇停泊碼頭及俱樂部相關設施興建工程委託規劃設計監造工作",u"98t10330b"],
            [98,u"梧棲漁港魚貨直銷中心銷售區整建工程",u"98t20506"],
            [99,u"坡頭漁港泊地疏浚工程",u"99004A"],
            [99,u"嘉義縣好美里及東好美里養殖區供排水系統改善工程",u"9901001-1"],
            [99,u"台子養殖區進排水路整建工程",u"9907-16"],
            [99,u"新港北養殖區進水路加高三期工程",u"9908-7"],
            [99,u"西新店養殖區過路子北支排（上游段）整建工程",u"9910629a"],
            [100,u"竹圍漁港泊地及航道疏浚工程",u"991216-AA1"],
            [99,u"箔子寮漁港港區整建工程",u"991A10057"],
            [99,u"台子村泊區疏浚",u"991A20029"],
            [99,u"箔子寮、三條崙航道清淤開口契約",u"991A20030"],
            [99,u"八斗子遊艇停泊碼頭工程",u"99a0806"],
            [99,u"烏石漁港曳船道遷建工程委託設計監造工作",u"99a0813"],
            [99,u"新竹漁港外泊地及航道疏浚工程",u"99A134"],
            [99,u"海山漁港航道泊地疏浚工程",u"99A136"],
            [99,u"海山漁港整網場遮陽棚新建工程",u"99A141"],
            [99,u"新竹漁港碼頭鋪面暨路燈汰換工程",u"99A215"],
            [99,u"高雄縣永安鄉養殖漁業生產區共同給水第五期工程",u"99B040"],
            [99,u"99年度東石漁人碼頭新建浮動碼頭",u"99GY1093A2"],
            [105,u"105年度南北寮漁港漁具整補場新建工程(第二年)",u"A104005"],
            [103,u"三民養殖漁業生產區排水路整建第二期工程",u"AG103060501"],
            [105,u"105年度花蓮漁港登船碼頭新建工程（不含設計監造）",u"AG10508151"],
            [105,u"105年度花蓮漁港綠美化及入口意象設施改善工程",u"AG10510051"],
            [100,u"大溪魚市場改建工程",u"AGCO099026"],
            [100,u"大塭養殖區供水管線及分配水箱整建工程",u"AGCO099057"],
            [100,u"常興養殖漁業區給排水路整建工程(第一工區)",u"AGCO099058"],
            [100,u"南方澳漁港漁具倉庫興建工程",u"AGCO100052"],
            [100,u"南澳漁港內泊地擴建工程",u"AGCO100061"],
            [101,u"南方澳漁港第三泊區新設LED港燈及路面重新鋪設工程",u"AGCO101019"],
            [101,u"南澳朝陽漁港東側海堤、粉鳥林北側路堤及大溪漁港東防波堤加拋消波塊工程",u"AGCO101036"],
            [102,u"烏石漁港娛樂漁船區棧橋碼頭增設工程及內泊地碼頭增設工程",u"AGCO102002"],
            [102,u"102年宜蘭縣大塭常興養殖漁業生產區海水供水管線整建工程",u"AGCO102026"],
            [102,u"大里、大溪及梗枋等三處漁港航道清淤疏浚工程",u"AGCO102037"],
            [102,u"東澳粉鳥林漁港、南澳漁港航道清淤疏浚工程",u"AGCO102037"],
            [102,u"大溪漁港東防波堤加拋消波塊工程",u"AGCO102054"],
            [103,u"烏石漁港離岸堤導航燈及相關設施改善工程",u"AGCO103016"],
            [103,u"壯圍養殖漁業生產區進排水路整建工程",u"AGCO103018"],
            [104,u"104年大溪漁港觀光魚貨直銷賣場新建工程（第二年）",u"AGCO103025"],
            [103,u"大溪漁港觀光魚貨直銷賣場新建工程（第一年）",u"AGCO103025"],
            [103,u"十大經典魅力漁港環境維護及改善計畫-南澳漁港",u"AGCO103031"],
            [103,u"大溪第二漁港泊區淤積疏浚工程",u"AGCO103039"],
            [103,u"103年-十大經典魅力漁港環境維護及改善計畫-烏石漁港",u"AGCO103040"],
            [104,u"烏石漁港斜坡道工程(不含設計監造)",u"AGCO103047"],
            [103,u"烏石漁港港區路燈更新及結合風力發電系統試驗計畫(二)",u"AGCO103052"],
            [104,u"烏石漁港卸魚碼頭設施工程(不含設計監造)",u"AGCO104014"],
            [104,u"梗枋漁港地基掏空修復補強工程",u"AGCO104025-1"],
            [104,u"烏石漁港胸牆美化工程(不含設計監造)",u"AGCO104035"],
            [104,u"大溪第二漁港泊區、南澳漁港淤積疏浚工程",u"AGCO104042"],
            [104,u"大溪第二漁港泊區、南澳漁港淤積疏浚工程",u"AGCO104042"],
            [104,u"烏石漁港航道疏浚工程",u"AGCO104047"],
            [104,u"宜蘭縣竹安養殖區海水供應管線擴充工程",u"AGCO104063"],
            [104,u"清水二中排改善工程-宜蘭縣(委辦)計畫工程",u"AGCO104064"],
            [105,u"清水排水改善工程",u"AGCO105024"],
            [105,u"105年度大溪漁港排水溝改善工程",u"AGCO105042"],
            [105,u"105年度梗枋漁港東防波堤及大里漁港加拋消波塊工程(不含設計)",u"AGCO105044"],
            [105,u"105年東澳粉鳥林及南澳漁港防波堤加拋消波塊工程",u"AGCO105075"],
            [106,u"清水三中排改善工程",u"AGCO105083"],
            [106,u"宜蘭縣壯圍養殖區二中排水溝整建工程(不合設計監造)",u"AGCO106010"],
            [107,u"107年度南方澳漁港第三泊區碼頭改建工程(不含設計監造)(第二年)",u"AGCO106013"],
            [106,u"106年度南方澳漁港第三泊區碼頭改建工程",u"AGCO106013"],
            [106,u"大塭養殖區王通塭四中排1-19小排水溝整建工程(不含設計監造)",u"AGCO106018"],
            [106,u"106年度梗枋漁港航道及泊地疏浚工程",u"AGCO106024"],
            [106,u"106年度大溪漁港第三期航道及泊地疏浚工程",u"AGCO106024"],
            [106,u"106年度梗枋漁港碼頭面環境改善工程",u"AGCO106025"],
            [106,u"106年烏石漁港航道水域疏浚工程",u"AGCO106041"],
            [106,u"106年度大溪漁港碼頭面環境改善工程",u"AGCO106045"],
            [106,u"106年南方澳漁港第一泊區輪胎碰墊改善工程設計工作",u"AGCO106052"],
            [106,u"106年南方澳漁港第一泊區輪胎碰墊改善工程(不含設計工作)",u"AGCO106052"],
            [100,u"布袋漁港維修用曳船道整建工程",u"B10003-1"],
            [103,u"布袋直銷中心屋頂防水隔熱整修工程（不含規劃設計）",u"B10207-2"],
            [106,u"台南雙春養殖區六中排排水改善工程",u"C0511116"],
            [106,u"臺南雙春養殖區三中排排水改善工程",u"C0610116"],
            [106,u"嘉義縣東好美養殖區東好美一之一中排改善工程",u"C0610218"],
            [106,u"雲林縣新港北養殖區新港北四之五中排改善工程",u"C0610301"],
            [106,u"八斗子漁港卸魚棚興建工程(加冰架及相關設施)",u"C0611205"],
            [101,u"塭港第一漁港蚵殼堆置場加高工程",u"C10103-1"],
            [104,u"嘉義縣轄內漁港航道及牡蠣養殖區共用航道導航燈興建工程",u"C10303-2"],
            [104,u"澎湖縣漁業公共設施建設計畫-花嶼漁港漁具倉庫暨補網場新建工程",u"CW-1050905"],
            [100,u"沙港中漁港北防波堤整建工程",u"CW-1100028"],
            [100,u"紅羅漁港基本設施改善工程",u"CW-1100041"],
            [100,u"外垵漁港碼頭延建工程",u"CW-1100043"],
            [100,u"中西漁港航道疏浚工程",u"CW-1100070"],
            [100,u"大池漁港泊地及航道疏浚工程",u"CW-1100071"],
            [100,u"大倉漁港泊地疏浚工程",u"CW-1100089"],
            [101,u"外垵漁港第五期工程",u"CW-1101034"],
            [103,u"外垵漁港第六期工程（二）",u"CW-1102057"],
            [103,u"小門漁港航道疏浚工程",u"CW-1103076"],
            [103,u"外垵漁港增設防舷材工程",u"CW-1103081"],
            [104,u"內垵北漁港小船泊區整建工程",u"CW-1104065"],
            [104,u"七美漁港基本設施改善工程",u"CW-1104070"],
            [104,u"澎湖縣漁業公共設施建設計畫-小門漁具倉庫及補網場等漁業公共設施改善工程",u"CW-1104077"],
            [104,u"桶盤漁港堤面及側牆改善工程",u"CW-1104078"],
            [105,u"104年度赤崁漁港疏浚及基本設施改善工程",u"CW-1104079"],
            [105,u"105年鳥嶼漁港航道疏浚工程",u"CW-1105012"],
            [106,u"馬公第三漁港製冰冷凍廠新建工程",u"CW-1105045"],
            [106,u"馬公第三漁港製冰冷凍廠新建工程(冷凍空調工程)",u"CW-1105091"],
            [106,u"106年度澎湖縣內垵南漁港外廓堤消波塊拋放工程",u"CW-1106054"],
            [98,u"南北寮漁港航道疏浚",u"CW-198021"],
            [102,u"烏石漁港遊艇碼頭及相關設施興建工程(水域部分)第一次變更設計",u"E0210110"],
            [102,u"烏石漁港魚市場及直銷中心外觀更新整建暨相關設施改善興建工程(第二次變更設計)",u"E0210118"],
            [101,u"烏石漁港魚市場及直銷中心外觀更新整建暨相關設施改善興建工程(變更設計)",u"E0210118"],
            [100,u"八斗子漁港經國廣場整建工程",u"H0010211"],
            [100,u"烏石漁港遊艇碼頭及相關設施興建工程(水域部分)",u"H0010323"],
            [100,u"八斗子漁港遊艇停泊示範區整建工程",u"H0010817"],
            [100,u"烏石漁港魚市場及直銷中心外觀更新整建暨相關設施改善興建工程",u"H0010826b"],
            [100,u"水井養殖區供排水路改善工程",u"H0010914"],
            [100,u"安平漁港遊艇泊區碼頭工程",u"H0011129"],
            [100,u"烏石漁港離岸防波堤北端堤頭加強保護工程",u"H0011206"],
            [101,u"八斗子漁港熱食區外觀改善工程",u"H0111009"],
            [101,u"八斗子全區景觀整建工程",u"H0111115"],
            [101,u"101年度大型鋼鐵人工魚礁工程",u"H0120413"],
            [101,u"梧棲漁港魚貨直銷中心銷售區整建工程",u"H0140301"],
            [99,u"嘉義縣西新店、北華、竿子寮、新店及過路子養殖區供排水系統改善工程（第1期）",u"H9911110"],
            [99,u"嘉義縣西新店、北華、竿子寮、新店及過路子養殖區供排水系統改善工程（第2期）",u"H9911116"],
            [99,u"嘉義縣西新店、北華、芉子寮、新店及過路子養殖區供排水系統改善工程（第3期）",u"H9911117"],
            [99,u"雲林縣下湖口養殖區供排水系統環境改善工程",u"H9911117a"],
            [99,u"烏石漁港南內防波堤興建工程(含規劃設計)",u"H9911117b"],
            [103,u"八斗子漁港卸魚碼頭疏浚工程",u"L0310306"],
            [103,u"烏石漁港遊艇泊區鋪面改善工程",u"L0310370"],
            [103,u"安平漁港遊艇碼頭新設圍籬工程",u"L0310522"],
            [104,u"嘉義縣西新店養殖區二中排改善工程",u"L0410924-3"],
            [104,u"台南雙春養殖區四中排排水改善工程",u"L0411023"],
            [104,u"LNG冷排水養殖試驗場興建工程",u"L0411119"],
            [105,u"嘉義縣北華養殖區二中排改善工程",u"L0411202"],
            [104,u"高雄市永華養殖區三中排排水改善工程",u"L0411210"],
            [105,u"嘉義縣過路子養殖區過路子二中排改善工程",u"L0510712"],
            [105,u"嘉義縣過路子養殖區過路子二中排改善工程",u"L0510712"],
            [106,u"106年羅厝漁港內泊地及航道疏浚工程(不含設計工作)",u"N106110110158"],
            [100,u"石梯漁港疏浚工程",u"SWC100040601"],
            [100,u"石梯漁港堤防波面及環境改善工程",u"SWC100121302"],
            [101,u"石梯漁港整補場工程",u"SWC101070901"],
            [102,u"壽豐養殖區二期排水渠道改善工程",u"SWC102102804"],
            [106,u"106年東港區漁會漁民活動中心綜合大樓修繕計畫",u"TKFISH1060013782"],
            [106,u"東港冷凍魚市場之環境衛生改善計畫",u"TKFISH1060014414"],
            [106,u"106年金湖漁港港區路面加固工程",u"TYFISH09801103"],
            [105,u"105年台子村漁港疏浚工程",u"tyfish1050901"],
            [105,u"105年度台子村漁港漁船油代購轉交簡易儲(加)油設施改善工程",u"tyfish1051001"],
            [100,u"萬里製冰廠興建",u"W100103105"],
            [107,u"107年苑港漁港漁港泊地航道淤砂疏浚工程(不含設計工作)(第二年)",u"106200"],
            [107,u"107年通霄漁港泊地航道淤砂疏浚工程(不含設計工作)(第二年)",u"106205"],
            [107,u"107年苑裡漁港泊地航道淤砂疏浚工程(不含設計工作)(第二年)",u"106206"],
            [107,u"107年中芸漁港東防波堤延長工程(第二期)(第三年)",u"1056055"],
            [107,u"107年外埔漁港淤砂疏浚工程(不含設計工作)(第二年)",u"06139a"],
            [107,u"107年龍鳳漁港淤砂疏浚工程(不含設計工作)(第二年)",u"06140a"],
            [107,u"107年磺港漁港外泊地碼頭改善工程(第二年)",u"1060512A"],
            [107,u"107年將軍漁港曳船道上架設施修繕工程(不含設計監造)",u"106AGR095"],
            [107,u"107年度南方澳漁港第三泊區碼頭改建工程(不含設計監造)(第二年)",u"AGCO106013"],
        ]

        total = len(projects)
        for n, row in enumerate(projects):
            for p in Project.objects.filter(year=row[0], name=row[1], deleter=None):
                p.pcc_no = row[2]
                p.save()
                try:
                    p.sync_pcc_info()
                except: pass
            print u'pcc_no="{pcc_no}"  progress={percent}%'.format(pcc_no=row[2], percent=round(100.0*(n+1)/total, 2))