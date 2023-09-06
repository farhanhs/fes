#-*- coding: utf8 -*-
from django.db import IntegrityError
from django.core.exceptions import ValidationError
# from django.conf.urls import defaults as urls
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.utils.cache import patch_cache_control
from django.views.debug import ExceptionReporter
from django.template.loader import get_template
from django.template import Context, RequestContext

from django.conf.urls import *

from tastypie import fields
from tastypie import http
from tastypie.http import HttpBadRequest
from tastypie.exceptions import BadRequest, ApiFieldError
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.paginator import Paginator
from tastypie.authentication import Authentication, SessionAuthentication, ApiKeyAuthentication, MultiAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from guardian.shortcuts import assign, get_objects_for_user, get_perms
import logging, traceback, sys, os, random, json, re, datetime

from general.models import Place, Unit
# from fishuser.resource import UserResource
# from fishuser.resource import PlanResource
# from fishuser.resource import OptionResource as Fishuser_OptionResource
# from fishuser.resource import ProjectResource as Fishuser_ProjectResource
from harbor.models import Option
from harbor.models import Observatory, FishingPort, PortFisheryOutput, FishingPortBoat, MainProject, Project
from harbor.models import Waves, Tide, FishingPortPhoto, AverageRainfall, AverageTemperature, AveragePressure
from harbor.models import City, FisheryOutput, FishType, FisheryType, AquaculturePublic, AquaculturePublicWork, PortInstallationRecord
from harbor.models import TempFile, DataShare, Aquaculture
from harbor.models import Reef, ReefLocation, ReefPut, ReefPutNum, ReefProject, ReefData

from monitor.models import Option as Monitor_Option
from monitor.models import Monitor, Account

from django.conf import settings
CAN_VIEW_BUG_PAGE_IPS = settings.CAN_VIEW_BUG_PAGE_IPS
NUMPERPAGE = settings.NUMPERPAGE
ROOT = settings.ROOT
API_LIMIT_PER_PAGE = settings.API_LIMIT_PER_PAGE

__enable__ = [
                'OptionResource',
                'ObservatoryResource',
                'FishingPortResource',
                'CityResource',
                'PortInstallationRecordResource',
                'AquacultureResource',
                'ProjectResource',
                'WavesResource',
                'TideResource',
                'FishingPortBoatResource',
                'FishingPortPhotoResource',
                'MainProjectResource',
                'AverageTemperatureResource',
                'AverageRainfallResource',
                'AveragePressureResource',
                'AquaculturePublicResource',
                'AquaculturePublicWorkResource',
                'PortFisheryOutputResource',
                'FisheryOutputResource',
                'TempFileResource',
                'Monitor_OptionResource',
                'MonitorResource',
                'AccountResource',
                'ReefResource',
                'ReefLocationResource',
                'ReefPutResource',
                'ReefPutNumResource',
                'ReefProjectResource',
                'ReefDataResource'
                ]

class RESTForbidden(Exception):
    pass



class SillyAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if settings.DEBUG: logging.info('SillyAuthentication: %s' % request.user.is_authenticated())
        return request.user.is_authenticated()



class PlaceResource(ModelResource):
    parent = fields.ForeignKey('self', 'parent', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Place.objects.all()
        resource_name = 'place'
        ordering = ["zipcode"]
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            "id": ("exact", ),
            "uplevel": ("exact", "isnull"),
        }



class UnitResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place', null=True)
    uplevel = fields.ForeignKey('self', 'uplevel', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Unit.objects.all()
        always_return_data = True
        resource_name = 'unit'
        ordering = ["name"]
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            "id": ("exact", ),
            "uplevel": ("exact", "isnull"),
        }


    def dehydrate_no(self, bundle):
        if bundle.obj:
            bundle.data['listname_place'] = bundle.obj.place.name if bundle.obj.place else ''

        return bundle.data['no']


        
class OptionResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Option.objects.all()
        resource_name = 'option'
        ordering = ["swarm"]
        allowed_methods = ['get', 'post', 'put']



class ObservatoryResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Observatory.objects.all()
        resource_name = 'observatory'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class FishingPortResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place')
    type = fields.ForeignKey(OptionResource, 'type')
    observatory = fields.ForeignKey(ObservatoryResource, 'observatory', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = FishingPort.objects.all()
        resource_name = 'fishingport'
        ordering = ["type", 'place', 'id']
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "place": ("exact", ),
        }

    def dehydrate_id(self, bundle):
        if bundle.obj:
            bundle.data['place__name'] = bundle.obj.place.name if bundle.obj.place else ''
            bundle.data['place__id'] = bundle.obj.place.id if bundle.obj.place else ''
            bundle.data['type__value'] = bundle.obj.type.value if bundle.obj.type else ''
            bundle.data['type__id'] = bundle.obj.type.id if bundle.obj.type else ''
            bundle.data['observatory__name'] = bundle.obj.observatory.name if bundle.obj.observatory else ''

        return bundle.data['id']



class CityResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = City.objects.all()
        resource_name = 'city'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']




class PortInstallationRecordResource(ModelResource):
    fishingport = fields.ForeignKey(FishingPortResource, 'fishingport')
    organization = fields.ForeignKey(UnitResource, 'organization', null=True)
    boat_supplies = fields.ForeignKey(OptionResource, 'boat_supplies', null=True)
    port_environment = fields.ForeignKey(OptionResource, 'port_environment', null=True)
    emergency_measures = fields.ForeignKey(OptionResource, 'emergency_measures', null=True)
    emergency = fields.ForeignKey(OptionResource, 'emergency', null=True)


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = PortInstallationRecord.objects.all()
        resource_name = 'portinstallationrecord'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']


    def dehydrate_id(self, bundle):
        if bundle.obj:
            bundle.data['listname_fishingport'] = bundle.obj.fishingport.name
            bundle.data['listname_organization'] = bundle.obj.organization.name
            bundle.data['listname_boat_supplies'] = bundle.obj.boat_supplies.value if bundle.obj.boat_supplies else ''
            bundle.data['listname_port_environment'] = bundle.obj.port_environment.value if bundle.obj.port_environment else ''
            bundle.data['listname_emergency_measures'] = bundle.obj.emergency_measures.value if bundle.obj.emergency_measures else ''
            bundle.data['listname_emergency'] = bundle.obj.emergency.value if bundle.obj.emergency else ''
            
        return bundle.data['id']


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search/$" % (self._meta.resource_name), self.wrap_view('get_search'), name="api_get_search"),
        ]


    def get_search(self, request, **kwargs):
        info = {}
        for key in request.GET.iterkeys():
            info[key] = request.GET.get(key)

        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        # Do the query.
        result = PortInstallationRecord.objects.all().order_by('fishingport', '-date', '-time')

        #漁港
        if info.get('fishing_port', '') and info.get('fishing_port', '') != '' and info.get('fishing_port', '') != 'undefined':
            fishingport = FishingPort.objects.get(id=info.get('fishing_port', ''))
            result = result.filter(fishingport=fishingport)

        #日期
        if info.get('date_from', '') and info.get('date_from', '') != '' and info.get('date_from', '') != 'undefined':
            result = result.filter(date__gte=info.get('date_from', ''), date__lte=info.get('date_to', ''))

        objects = []
        for r in result:
            bundle = self.build_bundle(obj=r, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)

        return self.create_response(request, object_list)



class AquacultureResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place')


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Aquaculture.objects.all()
        resource_name = 'aquaculture'
        ordering = ['place', 'id']
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "place": ("exact", ),
        }
        

    def dehydrate_id(self, bundle):
        if bundle.obj:
            bundle.data['place__name'] = bundle.obj.place.name if bundle.obj.place else ''
            bundle.data['place__id'] = bundle.obj.place.id if bundle.obj.place else ''

        return bundle.data['id']




class AquaculturePublicWorkResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place')


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = AquaculturePublicWork.objects.all()
        resource_name = 'aquaculturepublicwork'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class AquaculturePublicResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place')


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = AquaculturePublic.objects.all()
        resource_name = 'aquaculturepublic'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class ProjectResource(ModelResource):
    fishingport = fields.ForeignKey(FishingPortResource, 'fishingport')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Project.objects.all()
        resource_name = 'project'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class TideResource(ModelResource):
    fishingport = fields.ForeignKey(FishingPortResource, 'fishingport')


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Tide.objects.all()
        resource_name = 'tide'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class WavesResource(ModelResource):
    fishingport = fields.ForeignKey(FishingPortResource, 'fishingport')


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Waves.objects.all()
        resource_name = 'waves'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']




class PortFisheryOutputResource(ModelResource):
    fishingport = fields.ForeignKey(FishingPortResource, 'fishingport')


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = PortFisheryOutput.objects.all()
        resource_name = 'portfisheryoutput'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class FisheryOutputResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = FisheryOutput.objects.all()
        resource_name = 'fisheryoutput'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class MainProjectResource(ModelResource):
    fishingport = fields.ForeignKey(FishingPortResource, 'fishingport')


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = MainProject.objects.all()
        resource_name = 'mainproject'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class FishingPortPhotoResource(ModelResource):
    fishingport = fields.ForeignKey(FishingPortResource, 'fishingport')
    type = fields.ForeignKey(OptionResource, 'type')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = FishingPortPhoto.objects.all()
        resource_name = 'fishingportphoto'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']


    def obj_delete(self, bundle, **kwargs):
        f = FishingPortPhoto.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            os.remove(os.path.join(ROOT, f.file.name))
        except: pass
        super(FishingPortPhotoResource, self).obj_delete(bundle, **kwargs)



class FishingPortBoatResource(ModelResource):
    fishingport = fields.ForeignKey(FishingPortResource, 'fishingport')
    boat_type = fields.ForeignKey(OptionResource, 'boat_type')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = FishingPortBoat.objects.all()
        resource_name = 'fishingportboat'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']


    def obj_create(self, bundle, request=None, **kwargs):
        boat_type = Option.objects.get(id=bundle.data['boat_type'].split('/')[-2])
        fishingport = FishingPort.objects.get(id=bundle.data['fishingport'].split('/')[-2])
        if FishingPortBoat.objects.filter(fishingport=fishingport, year=bundle.data['year'], boat_type=boat_type):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'此年度已有此種船種數量。')))

        bundle.obj = FishingPortBoat()
        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)
        bundle = self.full_hydrate(bundle)
        self.save_related(bundle)
        bundle.obj.save()

        return bundle



class AverageTemperatureResource(ModelResource):
    observatory = fields.ForeignKey(ObservatoryResource, 'observatory')


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = AverageTemperature.objects.all()
        resource_name = 'averagetemperature'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class AverageRainfallResource(ModelResource):
    observatory = fields.ForeignKey(ObservatoryResource, 'observatory')


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = AverageRainfall.objects.all()
        resource_name = 'averagerainfall'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class AveragePressureResource(ModelResource):
    observatory = fields.ForeignKey(ObservatoryResource, 'observatory')


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = AveragePressure.objects.all()
        resource_name = 'averagepressure'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class TempFileResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = TempFile.objects.all()
        resource_name = 'tempfile'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']

    def obj_delete(self, bundle, **kwargs):
        f = TempFile.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            os.remove(os.path.join(ROOT, f.file.name))
        except: pass
        super(TempFileResource, self).obj_delete(bundle, **kwargs)



class DataShareResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = DataShare.objects.all()
        resource_name = 'datashare'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']


    def obj_delete(self, bundle, **kwargs):
        f = DataShare.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            os.remove(os.path.join(ROOT, f.file.name))
        except: pass
        super(DataShareResource, self).obj_delete(bundle, **kwargs)



class Monitor_OptionResource(ModelResource):

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Monitor_Option.objects.all()
        resource_name = 'monitor_option'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class MonitorResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place', null=True)
    port = fields.ForeignKey(FishingPortResource, 'port', null=True)
    # taken = fields.ForeignKey(UserResource, 'taken', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Monitor.objects.all()
        resource_name = 'monitor'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class AccountResource(ModelResource):
    monitor = fields.ForeignKey(MonitorResource, 'monitor', null=True)
    type = fields.ForeignKey(Monitor_OptionResource, 'type', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Account.objects.all()
        resource_name = 'account'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class ReefResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Reef.objects.all()
        resource_name = 'reef'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "place": ("exact", ),
        }



class ReefLocationResource(ModelResource):
    reef = fields.ForeignKey(ReefResource, 'reef')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ReefLocation.objects.all()
        resource_name = 'reeflocation'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "reef": ("exact", ),
        }



class ReefPutResource(ModelResource):
    reef = fields.ForeignKey(ReefResource, 'reef')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ReefPut.objects.all()
        resource_name = 'reefput'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class ReefPutNumResource(ModelResource):
    reefput = fields.ForeignKey(ReefPutResource, 'reefput')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ReefPutNum.objects.all()
        resource_name = 'reefputnum'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "reefput": ("exact", ),
        }



class ReefProjectResource(ModelResource):
    reef = fields.ForeignKey(ReefResource, 'reef')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ReefProject.objects.all()
        resource_name = 'reefproject'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']


class ReefDataResource(ModelResource):
    reef = fields.ForeignKey(ReefResource, 'reef')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ReefData.objects.all()
        resource_name = 'reefdata'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']


    def obj_delete(self, bundle, **kwargs):
        f = ReefData.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            os.remove(os.path.join(ROOT, f.file.name))
        except: pass
        super(ReefDataResource, self).obj_delete(bundle, **kwargs)