# -*- coding: utf8 -*-
if __name__ == '__main__':
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../fes'))
    import settings
    from django.core.management import setup_environ
    setup_environ(settings)

from common.models import DifferentTypeError

from django.test import TestCase
from common.lib import WorkingDate
from common import urls
from common import lib
from common import models
from common import views
import datetime
import django

def TODAY(): return datetime.date.today()


class DjangoVersion_1_1_TestCase(TestCase):
    def testVersionLimit(self):
        version = django.VERSION
        if 1 <= version[0]: major_version = True
        else: major_version = False
        if 1 <= version[1]: minor_version = True
        else: minor_version = False

        self.assertTrue(major_version, u'主要版本應大於 1 ')
        self.assertTrue(minor_version, u'次要版本應大於 1 ')


class ProjectExpandoModelTestCase(TestCase):
    from common.models import PStoreModel
    from common.models import ProjectExpandoModel
    def testExtraFields(self):
        p = ProjectExpandoModel(no='1', name='xxx')
        p.save()
        setattr(p, '_f_yyy', datetime.date(2001, 1, 1))
        p.save()
        p = ProjectExpandoModel.objects.get(no='1')

        self.assertEqual(getattr(p, '_f_yyy'), datetime.date(2001, 1, 1), u'p.yyy != datetime.date(2001, 1, 1)')

        p = ProjectExpandoModel(no='2', name='xxx')
        setattr(p, '_f_yyy', datetime.date(2001, 1, 1))
        p.save()
        p = ProjectExpandoModel.objects.get(no='2')

        self.assertEqual(getattr(p, '_f_yyy'), datetime.date(2001, 1, 1), u'p.yyy != datetime.date(2001, 1, 1)')

    def testTheSameType(self):
        p = ProjectExpandoModel(no='1', name='xxx')
        setattr(p, '_f_yyy', datetime.date(2001, 1, 1))
        p.save()
        setattr(p, '_f_yyy', 30)
        try:
            p.save()
        except DifferentTypeError:
            self.assertTrue(True)
        else:
            self.assertTrue(False, u'應禁止新值與舊值的型別不同')


class WorkingDateTestCase(TestCase):
    def testIgentleCase(self):
        """ * 新賀： 工作天
        """
        self.fail("TODO: 新賀未寫")

    def testUiyyeuCase(self):
        """ * 承曜： 日曆天(包含六日)
        """
        self.fail("TODO: 承曜未寫")

    def testDoraCase(self):
        """ * dora： 日曆天(僅周日不計)
        """
        self.fail("TODO: Dora 未寫")

    def testNildamuluiCase(self):
        """ * 祺磊：
            工期計算方式：日曆天(不含六日)，以完工日期計。
            開工日期：2009-09-8
            完工日期：2009-10-12
        """
        start_date = datetime.date(2009, 9, 2)
        end_date = datetime.date(2009, 9, 30)
        holiday = [
            datetime.date(2009, 9, 15),datetime.date(2009, 9, 28)
        ]
        force_work = [
            datetime.date(2009, 9, 12), datetime.date(2009, 9, 15)
        ]
        day_off = [
            datetime.date(2009, 9, 11),
            datetime.date(2009, 9, 18),
            datetime.date(2009, 9, 21),
        ]
        day_on = [
            datetime.date(2009, 9, 21),
            datetime.date(2009, 9, 26),
        ]
        w = WorkingDate(type_name=u'日曆天(不含六日)',
            start_date=start_date, holiday=holiday, force_work=force_work,
            day_off=day_off, day_on=day_on)

        corrent_answer = [
            datetime.date(2009, 9, 2),
            datetime.date(2009, 9, 3),
            datetime.date(2009, 9, 4),
            datetime.date(2009, 9, 7),
            datetime.date(2009, 9, 8),
            datetime.date(2009, 9, 9),
            datetime.date(2009, 9, 10),
            datetime.date(2009, 9, 12),
            datetime.date(2009, 9, 14),
            datetime.date(2009, 9, 15),
            datetime.date(2009, 9, 16),
            datetime.date(2009, 9, 17),
            datetime.date(2009, 9, 21),
            datetime.date(2009, 9, 22),
            datetime.date(2009, 9, 23),
            datetime.date(2009, 9, 24),
            datetime.date(2009, 9, 25),
            datetime.date(2009, 9, 26),
            datetime.date(2009, 9, 29),
            datetime.date(2009, 9, 30)

        ]

        self.assertEqual(corrent_answer, w.rByEnddate(end_date),
            u"在日曆天(不含六日)、開工日期是 %s 、完工日期為 %s 等條件下，計算失敗"
                % (start_date, end_date));

    def testCerberusCase(self):
        """ * 楊焄： 限期完工(日曆天每日施工)
        """
        self.fail("TODO: 楊焄未寫")

    def testGoBackReadByRange(self):
        """ 預設工期計算方式是「日曆天(包含六日)」, 預設開工日期是今天。

            檢查今天之前的 9 天，其工作日有那些!
        """
        w = WorkingDate()
        dates = [TODAY()]
        date = TODAY()
        for d in range(9):
            date += datetime.timedelta(days=-1)
            dates.append(date)
        self.assertEqual(dates, w.rByRange(-10),
            u"在日曆天(包含六日)、開始日期是 %s 、工期往前算 10 天等條件下，計算失敗" % TODAY());

    def testDefaultReadByRange(self):
        """ 預設工期計算方式是「日曆天(包含六日)」, 預設開工日期是今天。

            檢查工期是 10 天時，其工作日有那些!
        """
        w = WorkingDate()
        dates = [TODAY()]
        date = TODAY()
        for d in range(9):
            date += datetime.timedelta(1)
            dates.append(date)

        self.assertEqual(dates, w.rByRange(10),
            u"在日曆天(包含六日)、開工日期是 %s 、工期 10 天等條件下，計算失敗" % TODAY());

    def testGoBackReadByEnddate(self):
        """ 預設工期計算方式是「日曆天(包含六日)」, 預設開始日期是今天。

            檢查結束日期是今天的 365 天前，其工作日有那些!
        """
        w = WorkingDate()
        dates = []
        end_date = TODAY() + datetime.timedelta(days=-365)
        date = TODAY()
        while 1:
            if date < end_date: break
            dates.append(date)
            date += datetime.timedelta(days=-1)

        self.assertEqual(dates, w.rByEnddate(end_date),
            u"在日曆天(包含六日)、開工日期是 %s 、完工日期為 %s等條件下，計算失敗"
                % (TODAY(), end_date));

    def testDefaultReadByEnddate(self):
        """ 預設工期計算方式是「日曆天(包含六日)」, 預設開工日期是今天。

            檢查完工日期是今天的 365 天後，其工作日有那些!
        """
        w = WorkingDate()
        dates = []
        end_date = TODAY() + datetime.timedelta(days=365)
        date = TODAY()
        while 1:
            if date > end_date: break
            dates.append(date)
            date += datetime.timedelta(1)

        self.assertEqual(dates, w.rByEnddate(end_date),
            u"在日曆天(包含六日)、開工日期是 %s 、完工日期為 %s等條件下，計算失敗"
                % (TODAY(), end_date));

    def testCustomReadByEnddate(self):
        """ 工期計算方式是「日曆天(不含六日)」，開工日期是 2009-08-30 ，
            完工日期是 2009-10-04 。
        """
        start_date = datetime.date(2009, 8, 30)
        end_date = datetime.date(2009, 10, 4)
        holiday = [
            datetime.date(2009, 9, 15), datetime.date(2009, 9, 16)
        ]
        force_work = [datetime.date(2009, 9, 15)]
        day_off = [
            datetime.date(2009, 9, 20),
            datetime.date(2009, 9, 21),
            datetime.date(2009, 9, 22),
            datetime.date(2009, 9, 23),
            datetime.date(2009, 9, 24),
            datetime.date(2009, 9, 28),
        ]
        day_on = [
            datetime.date(2009, 9, 24),
            datetime.date(2009, 9, 25),
            datetime.date(2009, 9, 27),
            datetime.date(2009, 9, 28),
        ]
        w = WorkingDate(type_name=u'日曆天(不含六日)',
            start_date=start_date, holiday=holiday, force_work=force_work,
            day_off=day_off, day_on=day_on)

        corrent_answer = [
            datetime.date(2009, 8, 31),
            datetime.date(2009, 9, 1),
            datetime.date(2009, 9, 2),
            datetime.date(2009, 9, 3),
            datetime.date(2009, 9, 4),
            datetime.date(2009, 9, 7),
            datetime.date(2009, 9, 8),
            datetime.date(2009, 9, 9),
            datetime.date(2009, 9, 10),
            datetime.date(2009, 9, 11),
            datetime.date(2009, 9, 14),
            datetime.date(2009, 9, 15),
            datetime.date(2009, 9, 17),
            datetime.date(2009, 9, 18),
            datetime.date(2009, 9, 24),
            datetime.date(2009, 9, 25),
            datetime.date(2009, 9, 27),
            datetime.date(2009, 9, 28),
            datetime.date(2009, 9, 29),
            datetime.date(2009, 9, 30),
            datetime.date(2009, 10, 1),
            datetime.date(2009, 10, 2)
        ]

        self.assertEqual(corrent_answer, w.rByEnddate(end_date),
            u"在日曆天(不含六日)、開工日期是 %s 、完工日期為 %s 等條件下，計算失敗"
                % (start_date, end_date));


if __name__ == '__main__':
    from common.models import ForCompareExpandoModel
    from common.models import PStoreModel
    from common.models import ProjectExpandoModel
    import time

    t0 = time.time()

    #em = ProjectExpandoModel.objects.get(id=8)
    #em = ProjectExpandoModel(no='xxx', name='yyy')
    #em.note1 = 1
    #for i in xrange(2, 201):
        #setattr(em, 'note%d'%i, i)
    #em.save()
    #print em.EXTRA_FIELDS
    # 使用 core2duo 的機器數據
        # ** 使用自己的 value 打包方式 **
        #從 0 到 200 的欄位設定須花 20 秒
        #若是已經新增 200 個欄位，只是作 update 的話，大約 10 秒
        #單純抓出 200 個欄位的值，只須 0.2 秒

        # ** 使用 cPickle 的 value 打包方式 **
        #從 0 到 200 的欄位設定須花 17 秒
        #若是已經新增 200 個欄位，只是作 update 的話，大約 9.7 秒
        #單純抓出 200 個欄位的值，只須 0.2 秒

    # 使用 ibmgrace 的機器數據
        # ** 使用 cPickle 的 value 打包方式 **
        #從 0 到 200 的欄位設定須花 1.8 秒
        #若是已經新增 200 個欄位，只是作 update 的話，大約 1.2 秒
        #單純抓出 200 個欄位的值，只須 0.219 秒

# ===========================================================

    f = ForCompareExpandoModel.objects.get(id=2)
    #f = ForCompareExpandoModel()
    #f.note1 = 1
    #for i in xrange(2, 201):
    #    setattr(f, 'note%d'%i, i)
    #f.save()
    for i in f._meta.fields:
        x = getattr(f, i.name)

    # 使用 core2duo 的機器數據
        # 新增一筆紀錄，只有 0.12 秒 ，差了 200 倍，應該就是 insert 次數的差別。
        # 更新一筆紀錄，居然要 0.27 秒 ，反而比 insert 慢?
        # 抓取一筆紀錄，要 0.21 秒

    # 使用 ibmgrace 的機器數據
        # 新增一筆紀錄，只有 0.029 秒 ，差了 200 倍，應該就是 insert 次數的差別。
        # 更新一筆紀錄，居然要 0.217 秒 ，反而比 insert 慢?
        # 抓取一筆紀錄，要 0.204 秒
    print time.time() - t0
