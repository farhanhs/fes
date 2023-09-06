from django import template
from django.utils.translation import gettext_lazy as _
import re
from random import random
register = template.Library()
from settings import DEBUG
try:
    from settings import GOOGLE_TRACKER_CODE
except:
    GOOGLE_TRACKER_CODE = None

@register.simple_tag
def get_or_post():
    if DEBUG: return 'GET'
    else: return 'POST'
    
@register.simple_tag
def get_or_post_div():
    if DEBUG: return '<div id="get_or_post" style="display: none">GET</div>'
    else: return '<div id="get_or_post" style="display: none">POST</div>'

@register.simple_tag
def insert_google_analytics():
    if DEBUG: return ""
    elif GOOGLE_TRACKER_CODE: return "<script type=\"text/javascript\">\r\nvar gaJsHost = ((\"https:\" == document.location.protocol) ? \"https://ssl.\" : \"http://www.\");\r\ndocument.write(unescape(\"%3Cscript src='\" + gaJsHost + \"google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E\"));\r\n</script>\r\n<script type=\"text/javascript\">\r\ntry {\r\nvar pageTracker = _gat._getTracker(\"" + GOOGLE_TRACKER_CODE + "\");pageTracker._trackPageview();} catch(err) {}\r\n</script>"
    else: return ""

@register.filter
def minus(first, second):
    return first - second

def randomdecimal():
    return str(random())
register.simple_tag(randomdecimal)

class ExprNode(template.Node):
    def __init__(self, expr_string, var_name):
        self.expr_string = expr_string
        self.var_name = var_name
    
    def render(self, context):
        try:
            clist = list(context)
            clist.reverse()
            d = {}
            d['_'] = _
            for c in clist:
                d.update(c)
            if self.var_name:
                context[self.var_name] = eval(self.expr_string, d)
                return ''
            else:
                return str(eval(self.expr_string, d))
        except:
            raise
    
class CatchNode(template.Node):
    def __init__(self, nodelist, var_name):
        self.nodelist = nodelist
        self.var_name = var_name
        
    def render(self, context):
        output = self.nodelist.render(context)
        context[self.var_name] = output
        return ''

r_expr = re.compile(r'(.*?)\s+as\s+(\w+)', re.DOTALL)    
def do_expr(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents[0]
    m = r_expr.search(arg)
    if m:
        expr_string, var_name = m.groups()
    else:
        if not arg:
            raise template.TemplateSyntaxError, "%r tag at least require one argument" % tag_name
            
        expr_string, var_name = arg, None
    return ExprNode(expr_string, var_name)
do_expr = register.tag('expr', do_expr)

def do_catch(parser, token):
    """
    Catch the content and save it to var_name

    Example::

        {% catch as var_name %} ... {% endcatch %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents[0]
    m = re.search(r'as\s+(\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, '%r tag should define as "%r as var_name"' % (tag_name, tag_name)
    var_name = m.groups()[0]
    nodelist = parser.parse(('endcatch',))
    parser.delete_first_token()
    return CatchNode(nodelist, var_name)
do_catch = register.tag('catch', do_catch)

from django.template.loader import get_template
from django.conf import settings

import tokenize
import StringIO

class CallNode(template.Node):
   def __init__(self, template_name, *args, **kwargs):
       self.template_name = template_name
       self.args = args
       self.kwargs = kwargs

   def render(self, context):
       try:
           template_name = self.template_name.resolve(context)
           t = get_template(template_name)
           d = {}
           args = d['args'] = []
           kwargs = d['kwargs'] = {}
           for i in self.args:
               args.append(i.resolve(context))
           for key, value in self.kwargs.items():
               kwargs[key] = d[key] = value.resolve(context)

           context.update(d)
           result = t.render(context)
           context.pop()
           return result
       except:
           if settings.TEMPLATE_DEBUG:
              raise
           return ''

def do_call(parser, token):
   """
   Loads a template and renders it with the current context.

   Example::

       {% call "foo/some_include" %}
       {% call "foo/some_include" with arg1 arg2 ... argn %}
   """
   bits = token.contents.split()
   if 'with' in bits: #has 'with' key
       pos = bits.index('with')
       argslist = bits[pos+1:]
       bits = bits[:pos]
   else:
       argslist = []
   if len(bits) != 2:
       raise template.TemplateSyntaxError, "%r tag takes one argument: the name of the template to be included" % bits[0]
   path = parser.compile_filter(bits[1])
   if argslist:
       args = []
       kwargs = {}
       for i in argslist:
           if '=' in i:
               a, b = i.split('=', 1)
               a = a.strip()
               b = b.strip()
               buf = StringIO.StringIO(a)
               keys = list(tokenize.generate_tokens(buf.readline))
               if keys[0][0] == tokenize.NAME:
                   kwargs[a] = parser.compile_filter(b)
               else:
                   raise template.TemplateSyntaxError, "Argument syntax wrong: should be key=value"
           else:
               args.append(parser.compile_filter(i))
   return CallNode(path, *args, **kwargs)

register.tag('call', do_call)

class PyIfNode(template.Node):
    def __init__(self, nodeslist):
        self.nodeslist = nodeslist

    def __repr__(self):
        return "<PyIf node>"

    def render(self, context):
        for e, nodes in self.nodeslist:
            clist = list(context)
            clist.reverse()
            d = {}
            d['_'] = _
            for c in clist:
                d.update(c)
            v = eval(e, d)
            if v:
                return nodes.render(context)
        return ''

def do_pyif(parser, token):
    nodeslist = []
    while 1:
        v = token.contents.split(None, 1)
        if v[0] == 'endif':
            break
        if v[0] in ('pyif', 'elif'):
            if len(v) < 2:
                raise template.TemplateSyntaxError, "'pyif' statement requires at least one argument"
        if len(v) == 2:
            tagname, arg = v
        else:
            tagname, arg = v[0], 'True'
        nodes = parser.parse(('else', 'endif', 'elif'))
        nodeslist.append((arg, nodes))
        token = parser.next_token()
#    parser.delete_first_token()
    return PyIfNode(nodeslist)
do_pyif = register.tag("pyif", do_pyif)


# pycall
# you can use it to invoke a method of a module
r_identifers = re.compile(r'[\w.]+')
class PyCallNode(template.Node):
    def __init__(self, expr_string, var_name):
        self.expr_string = expr_string
        self.var_name = var_name

    def __repr__(self):
        return "<PyCall node>"

    def render(self, context):
        clist = list(context)
        clist.reverse()
        d = {}
        d['_'] = _
        d['context'] = context
        for c in clist:
            d.update(c)
        m = r_identifers.match(self.expr_string)
        if m:
            module, func = m.group().rsplit('.', 1)
            funcstring = self.expr_string[len(module) + 1:]
            mod = __import__(module, {}, {}, [''])
            d[func] = getattr(mod, func)
        else:
            raise template.TemplateSyntaxError, "The arguments of %r tag should be module.function(...)" % 'pycall'
            
        if self.var_name:
            context[self.var_name] = eval(funcstring, d)
            return ''
        else:
            return str(eval(funcstring, d))

def do_pycall(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires arguments" % token.contents[0]
    
    m = re.search(r'(.*?)\s+as\s+(\w+)', arg)
    if m:
        expr_string, var_name = m.groups()
    else:
        if not arg:
            raise template.TemplateSyntaxError, "The arguments of %r tag should be module.function(...)" % tag_name
            
        expr_string, var_name = arg, None
            
    return PyCallNode(expr_string, var_name)
do_pycall = register.tag("pycall", do_pycall)


from django import template
from django.conf import settings
import os

# Adjust your paths to 'imaging' and 'fs'
from common.imaging import fit,fit_crop
from common.fs import add_to_basename

def parse_args(args = ''):
    """
    Parse filter arguments in the format:
        keyword_1=value_1,keyword_2=value_2
    
    Returns a keyword list
    """
    kwargs = {}
    
    if args:
        for arg in args.split(','):
            kw, val = arg.split('=', 1)
            kwargs[kw.lower()] = val
        # for
    #
    
    return kwargs
# def parse_args

def resize(url, args = '', crop = False):
    """
    On-the-fly thumbnail or crop creation
    """
    
    kwargs = parse_args(args)
    call_kwargs = {}

    if ('width' not in kwargs) and ('height' not in kwargs):
        return url
    #
    
    if crop:
        # Mark as a cropped image
        extra = '_c_'
    else:
        # Mark as a thumbnailed image
        extra = '_t_'
    #
    
    # Setup width and/or height
    if 'width' in kwargs:
        extra += 'w' + kwargs['width']
        call_kwargs['max_width'] = kwargs['width']
    #
    if 'height' in kwargs:
        extra += 'h' + kwargs['height']
        call_kwargs['max_height'] = kwargs['height']
    #
    
    # Remove MEDIA_URL
#    url = url.replace(settings.MEDIA_URL, '')
    
    new_url = add_to_basename(url, extra)
    call_kwargs['save_as'] = os.path.join(settings.ROOT, new_url)

    if not os.path.exists(call_kwargs['save_as']):
        try:
            if crop:
                # Make the cropping
                ok = fit_crop(os.path.join(settings.ROOT, url), **call_kwargs)
            else:
                  # Create the thumbnail
                try:
                    ok = fit(os.path.join(settings.ROOT, url), **call_kwargs)
                except KeyError:
                    ok = False
        except IOError:
            ok = True
            if kwargs.has_key('error'):
                new_url = kwargs['error']
            else:
                new_url = 'media/images/error.png'

    else:
      ok = True
    #
        
    # Something wrong with the image processing?
    if not ok:
        # Silently restore the original url
        new_url = url
    #
    
    # Add MEDIA_URL back to the URL and return
    return new_url
    
# def resize

def thumb(url, args=''):
    """
    On-the-fly thumbnail creation
    
    Usage:
        {{ url|thumb:"width=10,height=20" }}
        {{ url|thumb:"width=10" }}
        {{ url|thumb:"height=20" }}
    """
    
    return resize(url, args)
#

def crop(url, args=''):
    """
    On-the-fly image cropping
    
    Usage:
        {{ url|crop:"width=10,height=20" }}
        {{ url|crop:"width=10" }}
        {{ url|crop:"height=20" }}
    """
    
    return resize(url, args, crop=True)
#
register.filter('thumb', thumb)
register.filter('crop', crop)

@register.filter
def cutzero(value, args=''):
   value = str(value)
   if '.' not in value: return value
   else: return re.sub('\.$', '', re.sub('0+$', '', value))
