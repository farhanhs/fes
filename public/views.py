#-*- coding: utf8 -*-
from os.path import join
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from tastypie.http import HttpBadRequest

from project.models import Project
from gallery.models import Case


def public_list(R):
    '''
    公開工程列表。
    '''
    public_case = Case.objects.filter(parent__is_public=True).values('parent__year').distinct()
    years = [i['parent__year'] for i in public_case]
    years.sort()

    template = get_template(join('public', 'public_list.html'))
    html = template.render(RequestContext(R, {'years': years}))
    return HttpResponse(html)


def public_photo(R, project_id):
    '''
    相片系統公開頁面。
    會檢查工程是否公開並顯示該工程之公開相片。
    '''
    try: project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return HttpBadRequest(u'無對應工程。')

    if not project.is_public:
        return HttpBadRequest(u'工程未公開。')

    try: case = project.photo_case
    except Case.DoesNotExist:
        project.save()
        case = project.photo_case

    template = get_template(join('public', 'public_photo.html'))
    html = template.render(RequestContext(R, {'project': project, 'case': case}))
    return HttpResponse(html)