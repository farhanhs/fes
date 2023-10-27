# -*- coding: utf8 -*-
from hashlib import md5
from types import NoneType
from settings import DEBUG
from settings import DOCSERVER
from settings import ROOT
from common.models import VerifyCode
from base64 import b64decode
from urllib import urlencode
import urllib2
from urllib2 import Request
from urllib2 import HTTPError
import datetime
import os
import shutil
from django.http import HttpResponse

def TODAY(): return datetime.date.today()


class WorkingDate:
    """ 每一種「工期計算方式」會對應一種一周開工/停工型式。key 0 表星期一，key 6 表星期日，
        value 1 表「計工期」，也就是要工作。

        工作日的計算方法如下：

        首先看它是那一種「工期計算方式」，這樣就會決定星期幾時要開工還是停工。

        接下來，檢查 holiday list 是否有設定，有則「停工」;
        再接下來檢查 force_work list 是否有設定，有則「開工」;
        而後檢查 day_off 是否有設定，有則「停工」;
        最後檢查 day_on 是否有設定，有則「開工」。

        holiday, force_work 乃 cim 系統針對人事行政局所作的設定。
        而 day_off, day_on 則是該工程主辦自行設定的。

        另外，只有「限期完工(日曆天每日施工)」是不檢查 holiday 及 force_work 的。
    """
    WEEKINDAYTYPE = {
        u'日曆天(包含六日)':       {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1},
        u'工作天':                {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1},
        u'限期完工(日曆天每日施工)':{0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1},
        u'日曆天(僅周日不計)':     {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0},
        u'日曆天(不含六日)':       {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 0, 6: 0},
    }

    def __init__(self, type_name=u'日曆天(包含六日)', start_date=TODAY(),
        holiday=[], force_work=[], day_off=[], day_on=[]):
        """ type_name, start_date 是必須存在的輸入值。

        使用範例：
        >>> w = WorkingDate()
        >>> w.rByEnddate(TODAY())
        [TODAY()]
        """
        self.type_name = type_name
        self.week_in_daytype = self.WEEKINDAYTYPE[type_name]
        self.start_date = start_date
        self.holiday = holiday
        self.force_work = force_work
        self.day_off = day_off
        self.day_on = day_on
        self.go = 1 # 往後走，日期的計算是愈來愈新

    def rByRange(self, range):
        """ 當 range = 10 時，則是 start_date 加上之後的 9 天為 working date 。
        """
        if range < 0: self.go = -1   # 往前走，日期的計算是愈來愈舊
        elif range >= 0: self.go = 1 # 往後走，日期的計算是愈來愈新
        range = abs(range)
        dates = []
        for d in self.check():
            if len(dates) >= range: break
            dates.append(d)
        return dates

    def rByEnddate(self, end_date):
        """ end_date 有算在 working date ，除非 end_date 本身被 day_off, holiday
            排除了。
        """
        if end_date < self.start_date: self.go = -1   # 往前走，日期的計算是愈來愈舊
        elif end_date >= self.start_date: self.go = 1 # 往後走，日期的計算是愈來愈新
        dates = []
        for d in self.check():
            if self.go > 0 and d > end_date: break
            elif self.go < 0 and d < end_date: break
            dates.append(d)
        return dates

    def rByRangeAndEnddate(self, range=0, end_date=TODAY()):
        """ 同時考慮工期及完工日期，以兩者的較大值為截止日。
        """
        range -= 1
        dates = []
        end_date_type = ''
        range_type = ''
        for d in self.check():
            if d > end_date: end_date_type = 'enough'
            if len(dates) > range: range_type = 'enough'
            if end_date_type and range_type: break
            dates.append(d)
        return dates

    def check(self):
        """ 檢查某日的 weekday 是因「工期計算方式」而不計工期，
            最後依序檢查 holiday, force_work, day_off, day_on 是否已有設定。

            本函式較特別的一點是使用 yield 作回傳機制。此機制同 xrange 函式，
            會有一種惰性。如：

            >>> for i in xrange(3): print(i)
            >>>
            0
            1
            2

            而我們使用 check 函式時，則是：

            >>> for d in self.check():
            >>>     if d < datetime.date(2009, 1, 4): print(d)
            >>>     else: break
            >>>
            datetime.date(2009, 1, 1)
            datetime.date(2009, 1, 2)
            datetime.date(2009, 1, 3)
        """
        date = self.start_date - datetime.timedelta(days=self.go)
        while 1:
            date += datetime.timedelta(days=self.go)
            weekday = date.weekday()
            type = self.week_in_daytype[weekday]

            if u'限期完工(日曆天每日施工)' != self.type_name and date in self.holiday: type = False
            if u'限期完工(日曆天每日施工)' != self.type_name and date in self.force_work: type = True
            if date in self.day_off: type = False
            if date in self.day_on: type = True

            if type: yield(date)
            else: pass

def findSublevel(self, sublevel_string='sublevel_set', order_by='pk'):
    sublevels = []
    for s in getattr(self, sublevel_string).all().order_by(order_by).order_by('sort'):
        sublevels.append(s)
        sublevels.extend(findSublevel(s, sublevel_string))
    return sublevels

def updateFirstWordByUpper(s):
    return s[0].upper() + s[1:].lower()

def readDateRange(start, end):
    range = []
    date = start
    while date <= end:
        range.append(date)
        date += datetime.timedelta(1)
    return range

def verifyOK(verifycode_id, usercode):
    try:
        verifycode = VerifyCode.objects.get(id=verifycode_id)
        if verifycode.key == usercode and verifycode.isdone == False:
            status = True
        else:
            status = False
        verifycode.isdone = True
        verifycode.save()
        return status
    except VerifyCode.DoesNotExist:
        return False

def md5password(password):
    password = unicode(password)
    return md5('%s%s+%s' % (password[0], password[-1], password)).hexdigest()

def readDATA(R):
    if DEBUG: return R.GET
    else: return R.POST

def mkdirByP(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdirByP(head)
        #print "mkdirByP %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

def mkdirWithP(newdir):
    mkdirByP(newdir)

from math import ceil
def makePageList(now_page, all_numbers, numperpage=10):
    all_pages = ceil(all_numbers/numperpage) + 1
    now_page, all_pages = int(now_page), int(all_pages)
    if now_page == 1: previous_page = False
    else: previous_page = now_page - 1

    if now_page == all_pages or all_pages == 0: next_page = False
    else: next_page = now_page + 1

    if all_pages <= numperpage or now_page <= (numperpage - 1):
        max_pages = all_pages >= numperpage and numperpage or all_pages
        page_list = range(1, max_pages+1)
    else:
        page_list = [p for p in range(1, all_pages+1)
        if p >= now_page - numperpage and p <= (now_page + numperpage - 1)]

    return {'previous_page': previous_page, 'page_list': page_list, 'all_pages': all_pages,
    'next_page': next_page, 'now_page': now_page}
#def makePageList(now_page, all_pages):
#    now_page, all_pages = int(now_page), int(all_pages)
#    if now_page == 1: previous_page = False
#    else: previous_page = now_page - 1
#
#    if now_page == all_pages or all_pages == 0: next_page = False
#    else: next_page = now_page + 1
#
#    if all_pages <= 10 or now_page <= 9:
#        max_pages = all_pages >= 10 and 10 or all_pages
#        page_list = range(1, max_pages+1)
#    else:
#        page_list = [p for p in range(1, all_pages+1) if p >= now_page - 10 and p <= now_page + 9]
#
#    return {'previous_page': previous_page, 'page_list': page_list, 'all_pages': all_pages,
#    'next_page': next_page, 'now_page': now_page}

def toDate(date_str):
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except:
        try:
            date = datetime.datetime.strptime(date_str, '%Y/%m/%d')
        except:
            date = ''
    return date

def nocache_response(response, max_age=0):
    response['Cache-Control'] = 'no-cache, must-revalidate, max-age=%s' % max_age
    response['Pragma'] = 'no-cache'
    return response

def getObject_find_sub_level(Model, id, setname, diff='', orderby='', level=0):
    try:
        if orderby == '':
            subs = getattr(Model.objects.get(id=id), setname).all()
        else:
            subs = getattr(Model.objects.get(id=id), setname).all().order_by(orderby)
        #TODO 排序出來的結果不會變，真奇怪。我怎麼當初沒寫是那份資料排序有問題呀! 現在要怎麼測試
    except:
        return
    ids = subid = []
    for sub in subs:
        ids.extend([(level, sub)])
        if diff == '':
            subid = find_sub_level(Model, sub.id, setname, level=level+1, orderby=orderby)
        else:
            subid = find_sub_level(Model, getattr(sub, diff).id, setname,
                level=level+1, orderby=orderby)
        if subid != [] and type(subid) != NoneType: ids.extend(subid)
    return ids

def find_sub_level(Model, id, setname, diff='', orderby='', level=0):
    try:
        if orderby == '':
            subs = getattr(Model.objects.get(id=id), setname).all()
        else:
            subs = getattr(Model.objects.get(id=id), setname).all().order_by(orderby)
        #TODO 排序出來的結果不會變，真奇怪。我怎麼當初沒寫是那份資料排序有問題呀! 現在要怎麼測試
    except:
        return
    ids = subid = []
    for sub in subs:
        ids.extend([(level, sub.id)])
        if diff == '':
            subid = find_sub_level(Model, sub.id, setname, level=level+1, orderby=orderby)
        else:
            subid = find_sub_level(Model, getattr(sub, diff).id, setname,
                level=level+1, orderby=orderby)
        if subid != [] and type(subid) != NoneType: ids.extend(subid)
    return ids

def getObject_find_sub(Model, id, setname, diff='', orderby=''):
    try:
        if orderby == '':
            subs = getattr(Model.objects.get(id=id), setname).all()
        else:
            subs = getattr(Model.objects.get(id=id), setname).all().order_by(orderby)
    except:
        return
    ids = subid = []
    for sub in subs:
        ids.extend([sub])
        if diff == '':
            subid = find_sub(Model, sub.id, setname, orderby=orderby)
        else:
            subid = find_sub(Model, getattr(sub, diff).id, setname, orderby=orderby)
        if subid != [] and type(subid) != NoneType: ids.extend(subid)
    return ids

def find_sub(Model, id, setname, diff='', orderby=''):
    try:
        if orderby == '':
            subs = getattr(Model.objects.get(id=id), setname).all()
        else:
            subs = getattr(Model.objects.get(id=id), setname).all().order_by(orderby)
    except:
        return
    ids = subid = []
    for sub in subs:
        ids.extend([sub.id])
        if diff == '':
            subid = find_sub(Model, sub.id, setname, orderby=orderby)
        else:
            subid = find_sub(Model, getattr(sub, diff).id, setname, orderby=orderby)
        if subid != [] and type(subid) != NoneType: ids.extend(subid)
    return ids

def to_money(money):
    money = str(money)
    s = ''
    d = []
    try:
        (money, postfix) = money.split('.')
        postfix = '.' + postfix
    except:
        postfix = ''

    if len(str(money)) <= 3:
        return str(money)
    else:
        for (i, w) in enumerate(reversed(str(money))):
            s = w + s
            if i % 3 == 2:
                d.insert(0, s)
                s = ''
        if s != '': d.insert(0, s)
        return ','.join(d) + postfix

def authurl(list, randkey):
    return md5(''.join([str(i) for i in list])+randkey).hexdigest()[9:19].replace('8', 'X')

def calsize(num):
    if not num: num = 0
    if num < 1024: return str(num) + ' B'
    k = int(num) / 1024
    if k <=1024: return str(k) + ' KB'
    m = k / 1024
    if m <= 1024: return str(m) + ' MB'
    g = m / 1024
    return str(g) + ' GB'

from django.db.models import ImageField, FileField, signals
from django.dispatch import dispatcher
from django.conf import settings
import glob

# Helpers
from imaging import fit,fit_crop
from fs import change_basename

def auto_rename(file_path, new_name):
    """
    Renames a file, keeping the extension.

    Parameters:
        - file_path: the file path relative to MEDIA_ROOT
        - new_name: the new basename of the file (no extension)

    Returns the new file path on success or the original file_path on error.
    """

    # Return if no file given
    if file_path == '':
        return ''
    #

    # Get the new name
    new_path = change_basename(file_path, new_name)

    # Changed?
    if new_path != file_path:
        # Try to rename
        try:
            shutil.move(os.path.join(settings.ROOT, file_path), os.path.join(settings.ROOT, new_path))
        except IOError:
            # Error? Restore original name
            new_path = file_path
        #
    #

    # Return the new path
    return new_path
# def auto_rename

def auto_resize(file_path, max_width=None, max_height=None, crop=False):
    """
    Resize an image to fit an area.
    Useful to avoid storing large files.

    If set to crop, will resize to the closest size and then crop.

    At least one of the max_width or max_height parameters must be set.
    """

    # Return if no file given or no maximum size passed
    if (not file_path) or ((not max_width) and (not max_height)):
        return
    #

    # Get the complete path using MEDIA_ROOT
    real_path = os.path.join(settings.ROOT, file_path)

    if (crop):
        fit_crop(real_path, max_width, max_height)
    else:
        fit(real_path, max_width, max_height)
    #
# def auto_resize

def init_path(self, **kwargs):
    """
    Create a flag if there's an 'upload_to' parameter.
    If not found, fill with a dummy value.
    The flag will be used to create an automatic value on "post_init" signal.
    """

    # Flag to auto-fill the path if it is empty
    self.fill_path = ('upload_to' not in kwargs)

    if self.fill_path:
        # Dummy value to bypass attribute requirement
        kwargs['upload_to'] = '_'
    #

    return kwargs
# def init_path

def set_field_path(self, instance = None):
    """
    Set up the "upload_to" for AutoFileField and AutoImageField or "path" for AutoFilePathField.
    Set a path based on the field hierarchy (app/model/field).
    """

    # Use the automatic path?
    if self.fill_path:
        setattr(self, 'upload_to', os.path.join(instance._meta.app_label, instance.__class__.__name__, self.name).lower())
    #
# def set_field_path

class AutoFileField(FileField):
    """
    File field with:
    * automatic primary key based renaming
    * automatic upload_to (if not set)
    """

    def __init__(self, verbose=None, **kwargs):
        # Adjust the upload_to parameter
        kwargs = init_path(self, **kwargs)

        super(AutoFileField, self).__init__(verbose, **kwargs)
    # def __init__

    def _post_init(self, instance=None):
        set_field_path(self, instance)
    # def _post_init

    def _save(self, instance=None):
        if instance == None:
            return
        filename = auto_rename(getattr(instance, self.attname), '%s' % instance._get_pk_val())
        setattr(instance, self.attname, filename)
    # def _save

    def contribute_to_class(self, cls, name):
        super(AutoFileField, self).contribute_to_class(cls, name)
        dispatcher.connect(self._post_init, signals.post_init, sender=cls)
        dispatcher.connect(self._save, signals.pre_save, sender=cls)
    # def contribute_to_class

    def get_internal_type(self):
        return 'FileField'
    # def get_internal_type
# class AutoFileField

class AutoImageField(ImageField):
    """
    Image field with:
    * automatic primary key based renaming
    * automatic upload_to (if not set)
    * optional resizing to a maximum width and/or height
    """

    def __init__(self, verbose=None, max_width=None, max_height=None, crop=False, **kwargs):
        # Adjust the upload_to parameter
        kwargs = init_path(self, **kwargs)

        # Image resizing properties
        self.max_width, self.max_height, self.crop = max_width, max_height, crop

        # Set fields for width and height
        self.width_field, self.height_field = 'width', 'height'

        super(AutoImageField, self).__init__(verbose, **kwargs)
    # def __init__

    def save_file(self, new_data, new_object, original_object, change, rel, save=True):
        # Original method
        super(AutoImageField, self).save_file(new_data, new_object, original_object, change, rel, save)

        # Get upload info
        upload_field_name = self.get_manipulator_field_names('')[0]
        field = new_data.get(upload_field_name, False)

        # File uploaded?
        if field:
            # Resize image
            auto_resize(getattr(new_object, self.attname), max_width=self.max_width, max_height=self.max_height, crop=self.crop)
        #
    # def save_file

    def delete_file(self, instance):
        """
        Deletes left-overs from thumbnail or crop template filters
        """

        super(AutoImageField, self).delete_file(instance)

        if getattr(instance, self.attname):
            # Get full path
            file_name = getattr(getattr(instance, self.name), 'name')
            # Get base dir, basename and extension
            basedir = os.path.dirname(file_name)
            base, ext = os.path.splitext(os.path.basename(file_name))

            # Delete left-overs from filters
            for file in glob.glob(os.path.join(basedir, base + '_*' + ext)):
                os.remove(os.path.join(basedir, file))
            #
        #
    # def delete_file

    def _post_init(self, instance=None):
        set_field_path(self, instance)
    # def _post_init

    def _save(self, instance=None):
        if instance == None:
            return
        filename = auto_rename(getattr(instance, self.attname), '%s' % instance._get_pk_val())
        setattr(instance, self.attname, filename)
    # def _save

    def contribute_to_class(self, cls, name):
        super(AutoImageField, self).contribute_to_class(cls, name)
        dispatcher.connect(self._post_init, signals.post_init, sender=cls)
        dispatcher.connect(self._save, signals.pre_save, sender=cls)
    # def contribute_to_class

    def get_internal_type(self):
        return 'ImageField'
    # def get_internal_type
# class AutoImageField


class NameIsNotImportant:
    pass


def makeFileByWordExcel(template_name='' , result='', docserver=DOCSERVER):
    if docserver != 'THE_SAME_PLATFORM':
        url = 'http://%s/%s/' % (docserver, template_name)
        req = Request(url)
        post_data = urlencode([('data', result)])
        try:
            from settings import DOC_PROXY as PROXY
        except ImportError:
            PROXY = ''

        if ('127.0.0.1' in docserver or 'localhost' in docserver):
            proxy_handler = urllib2.ProxyHandler({})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)
        elif PROXY:
            proxy = ':'.join([str(i) for i in PROXY])	
            passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passmgr.add_password(None, proxy, '', '')
            authinfo = urllib2.ProxyBasicAuthHandler(passmgr)
            proxy_support = urllib2.ProxyHandler({"http" : proxy})
            opener = urllib2.build_opener(proxy_support, authinfo)
            urllib2.install_opener(opener)

        try:
            fd = opener.open(req, post_data)
        except HTTPError, e:
            response = HttpResponse()
            response['status_code'] = 500
            response.write(e.read().replace('<title>', '<title>DOCSERVER Return: '))
            return response
        content = b64decode(fd.read())
        fd.close()
    else:
        try:
            from wordexcel.views import exportMSFile
        except ImportError:
            raise ImportError('We need wordexcel module in Windows')
        NameIsNotImportant.THE_SAME_PLATFORM = result
        filename = exportMSFile(NameIsNotImportant, template_name)
        f = open(filename, 'rb')
        content = f.read()
        f.close()
        shutil.rmtree(os.path.dirname(os.path.dirname(filename)))

    return content
