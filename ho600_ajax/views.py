""" AjaxMappingController is a ajax view function controller.

    Please see the anAjaxExample function to get the concept,
    every ajax view function has four conditions in an ajax request,
    the anAjaxExample shows all for you.
"""
try:
    from google.appengine.api.datastore_types import Email
    from google.appengine.api.datastore_types import Text
    from google.appengine.api.datastore_types import PhoneNumber
    from google.appengine.api.datastore_types import Link
except ImportError:
    Email = Text = PhoneNumber = Link = None

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.http import HttpResponseServerError
from django.template import RequestContext
from django.template.loader import get_template
from django.views.debug import ExceptionReporter
from django.utils.safestring import SafeUnicode
import json

try:
    from ho600_bugrecord.models import BugPage
except ImportError:
    BugPage = None

try: from djangoappengine.utils import on_production_server
except ImportError: on_production_server = False
except: on_production_server = False

import sys, os, logging, types, datetime



class WalkStructure:
    def __init__(self, s, list_f=lambda x,y: y if 1 else y,
        hash_f=lambda x,y: y if x >=0 else y, to_json=False):
        self._s = s
        self._list_f = list_f if not to_json else self.toJSON
        self._hash_f = hash_f if not to_json else self.toJSON
        self.walk(s)

    def rNewS(self):
        return self._s

    def toJSON(self, k, v):
        type_v = type(v)
        if type_v in [types.UnicodeType, Text, Email, PhoneNumber, Link, SafeUnicode]:
            return str(v.encode('utf8'))
        elif type_v == datetime.datetime:
            return v.strftime('%Y-%m-%d %H:%M:%S')
        elif type_v == datetime.date:
            return v.strftime('%Y-%m-%d')
        else:
            return v

    def walk(self, s):
        if type(s) == types.DictionaryType:
            for k, v in s.items():
                v = self._hash_f(k, v)
                s[k] = v
                self.walk(v)

        elif type(s) == types.ListType:
            for i, v in enumerate(s):
                v = self._list_f(i, v)
                s[i] = v
                self.walk(v)
        return s



class AJAXForbiddenError(Exception):
    pass



class AjaxMappingController(object):
    def __init__(self):
        self._map_dict = {}


    def register(self, fn):
        """ When http server imports scripts have
            "@controller.register" wrapper function likes
            "apps/dailyreport/views.py", this register function will shot.
        """
        func_mapping = self._map_dict.setdefault(fn.__module__, {})
        if fn.func_name in func_mapping:
            raise Exception('%s was existed' % fn.func_name)
        else:
            func_mapping[fn.func_name] = {'function': fn, '__doc__': fn.__doc__}

        return self.callback


    def callback(self, R):
        R.DATA = DATA = R.POST if R.method == 'POST' else R.GET

        module, fn_name = DATA.get("module", None), DATA.get("submit", DATA.get('_submit', None))
        no_submit = False
        try:
            fn = self._map_dict[module][fn_name]['function']
        except KeyError:
            try:
                dev_null = __import__(module)
                fn = self._map_dict[module][fn_name]['function']
            except ImportError:
                no_submit = True
            except KeyError:
                no_submit = True
            except TypeError:
                no_submit = True

        if no_submit:
            message = "ajax function error. module=%s, submit=%s"%(module, fn_name)
            return HttpResponseForbidden(message, content_type='text/plain')

        if not R.user.is_authenticated():
            if R.is_ajax():
                return HttpResponse(json.dumps({"__redirect__": R.META.get('HTTP_REFERER', '/')}),
                                                content_type='application/json')
            else:
                return HttpResponseRedirect(R.META.get('PATH_INFO', '/'))

        try:
            response = fn(R)

        except AJAXForbiddenError,e:
            message = "\n".join(e.args)
            return HttpResponseForbidden(message, content_type='text/plain')

        except:
            code = "No Ho600's Bug Record"
            if BugPage:
                reporter = ExceptionReporter(R, *sys.exc_info())
                #phase I, record bug page html
                bp = BugPage(html=reporter.get_traceback_html())
                bp.save()
                #phase II, record request's detail
                bp.saveWithRequest(request=R)
                #phase III, search the same bug kind
                bp.kind = bp.findBugKind()
                bp.save()

                code = bp.code
                logging.error('bug page code: %s' % bp.code)

            return HttpResponseServerError(code, content_type='text/plain')

        else:
            if type(response) in [HttpResponse, HttpResponseRedirect]:
                return response
            elif type(response) == types.DictType:
                response["__status__"] = True
                ws = WalkStructure(response, to_json=True)
                return HttpResponse(json.dumps(ws.rNewS()))
            else:
                return HttpResponseForbidden(u'format of return data is not defined, it should be a dictionary!',
                    content_type='text/plain')


    def helper(self, R, module=''):
        """ Show all ajax view functions that was wrapped by "@controller.register"

            But it only shows ajax view functions after the script are imported.

            If you want to see the cProject of apps.project.views,
            please run some url in your browser to import apps.project.views first.
        """
        if on_production_server:
            return HttpResponseForbidden('Could not show helper, We are not in DEBUG', content_type='text/plain')

        d = {}
        if module:
            v = self._map_dict.get(module, {})
            v_ks = v.keys()
            v_ks.sort()
            d[module] = [{'submit_name': v_k, 'DOC': v[v_k]['__doc__']} for v_k in v_ks]
        else:
            for k, v in self._map_dict.items():
                v_ks = v.keys()
                v_ks.sort()
                d[k] = [{'submit_name': v_k, 'DOC': v[v_k]['__doc__']} for v_k in v_ks]

        t = get_template(os.path.join('ajax', 'ajax_helper.html'))
        html = t.render(RequestContext(R, {'modules': d}))
        return HttpResponse(html)



controller = AjaxMappingController()


@controller.register
def anAjaxExample(R):
    '''
*** An example of AJAX view function ***

    Example:

        *** Click ***: `Type with good
        </__ajax__/?module=ho600_ajax.views&submit=anAjaxExample&type=good>`_

            Get 200 status: '{"__status__": true, "message": "Good", "Good": "message"}'

        *** Click ***: `Type with error
        </__ajax__/?module=ho600_ajax.views&submit=anAjaxExample&type=error>`_

            Get 403 status which defined in your view function: AJAXForbiddenError("ajax runtime error on anAjaxExample")

        *** Click ***: `Type with not_dictionary
        </__ajax__/?module=ho600_ajax.views&submit=anAjaxExample&type=not_dictionary>`_

            Get 403 status which defined in ajax.controller.AjaxMappingController: 'format of return data is not defined, it should be a dictionary!'

        *** Click ***: `Type with nothing
        </__ajax__/?module=ho600_ajax.views&submit=anAjaxExample>`_

            Get 500 status which is undefined anywhere: THE BUG PAGE
'''
    if R.DATA.get('type', '') == 'good':
        return {'message': 'Good', 'Good': 'message'}
    elif R.DATA.get('type', '') == 'error':
        raise AJAXForbiddenError("What Error you designed!!!")
    elif R.DATA.get('type', '') == 'not_dictionary':
        return 'OK'
    else:
        a = 1 / 0 #INFO Error happens


callback = controller.callback
helper = controller.helper
