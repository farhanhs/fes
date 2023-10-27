#-*- coding: utf8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from general.models import Place, Unit, FishCityMenuManager
import os, json
from django.forms import ModelForm
from harbor.models import FishingPort,FisheryOutput,FishType,FishingPortBoat
from harbor.models import Option as HARBOR_option
from gis.models import PortPhotos
from common.lib import readDATA
from fishuser.models import _ca
from fishuser.models import Option
from fishuser.models import UserProfile
from fishuser.models import LoginHistory
from fishuser.models import WrongLogin
from fishuser.models import DocumentOfProjectModels
from fishuser.models import Plan
from fishuser.models import PlanBudget
from fishuser.models import Project
from fishuser.models import Project_Port
from fishuser.models import DefaultProject
from fishuser.models import FRCMUserGroup
from fishuser.models import Factory
from fishuser.models import Reserve
from fishuser.models import FundRecord
from fishuser.models import Fund
from fishuser.models import BudgetProject
from fishuser.models import Appropriate
from fishuser.models import Progress
from fishuser.models import ScheduledProgress
from fishuser.models import ProjectPhoto
from fishuser.models import FRCMTempFile
from settings import ROOT
from fishuser.views import checkAuthority
import decimal
import datetime
from PIL import Image
import gis.EXIF as EXIF
def TODAY(): return datetime.datetime.today()

def index(R):
    return render_to_response(os.path.join('gis', 'index.html'))

def search(R):
    DATA = json.read(R.GET["search"])

    port = FishingPort.objects.all()
    port_data = []
    boat = []
    output = []
    DATA.sort()
    have_city_search = False
    for row in DATA:
        if row[0] == "1": #縣市搜尋
            if row[1] == "1":
                port_data = list(port)
            else:
                port_data += list(port.filter(place__id = row[1]))
            have_city_search = True

    if not have_city_search:
        port_data = list(port)

    for row in DATA:
        if row[0] == "2": #類型搜尋
            for i in xrange(len(port_data)-1,-1,-1):
                if port_data[i].type.id != int(row[1]):
                    port_data.remove(port_data[i])

        elif row[0] == "3": #名稱搜尋
            temp = port_data
            port_data = []
            for i in temp:
                if row[1] in i.name:
                    port_data.append(i)

        elif row[0] == "4": #漁船搜尋
            if row[3].isdigit():
                info = {'type': '', 'value': {}}
                for i in xrange(len(port_data)-1,-1,-1):
                    try:
                        fishingboat = list(port_data[i].fishingportboat_set.filter(boat_type__id=row[1]).order_by('-year'))[0]
                        info['type'] = fishingboat.boat_type.value
                        if fishingboat.num:
                            if row[2] == "more_than":
                                if fishingboat.num < int(row[3]):
                                    port_data.remove(port_data[i])
                                else:
                                    info['value'][port_data[i].id] = fishingboat.num
                            if row[2] == "less_than":
                                if fishingboat.num > int(row[3]):
                                    port_data.remove(port_data[i])
                                else:
                                    info['value'][port_data[i].id] = fishingboat.num
                            if row[2] == "between":
                                if row[3]>row[4]:
                                    if fishingboat.num > int(row[3]) or fishingboat.num < int(row[4]):
                                        port_data.remove(port_data[i])
                                    else:
                                        info['value'][port_data[i].id] = fishingboat.num
                                else:
                                    if fishingboat.num > int(row[4]) or fishingboat.num < int(row[3]):
                                        port_data.remove(port_data[i])
                                    else:
                                        info['value'][port_data[i].id] = fishingboat.num
                        else:
                            port_data.remove(port_data[i])
                    except:
                        port_data.remove(port_data[i])
                boat.append(info)
                    
        elif row[0] == "5": #魚獲搜尋
            if row[2].isdigit() == True :
                info = {'type': '', 'value': {}}
                for i in xrange(len(port_data)-1,-1,-1):
                    try:
                        portfisheryoutput = list(port_data[i].portfisheryoutput_set.order_by("-year"))[0]
                        info['type'] = '漁貨產值'
                        if portfisheryoutput.value:
                            if row[1] == "more_than":
                                if portfisheryoutput.value < int(row[2]):
                                    port_data.remove(port_data[i])
                                else:
                                    info['value'][port_data[i].id] = portfisheryoutput.value
                            if row[1] == "less_than":
                                if portfisheryoutput.value > int(row[2]):
                                    port_data.remove(port_data[i])
                                else:
                                    info['value'][port_data[i].id] = portfisheryoutput.value
                            if row[1] == "between":
                                between = json.read(row[2])
                                if between[0]>between[1]:
                                    if portfisheryoutput.value > int(between[0]) or portfisheryoutput.value < int(between[1]):
                                        port_data.remove(port_data[i])
                                    else:
                                        info['value'][port_data[i].id] = portfisheryoutput.value

                                if between[1]>between[0]:
                                    if portfisheryoutput.value > int(between[1]) or portfisheryoutput.value < int(between[0]):
                                        port_data.remove(port_data[i])
                                    else:
                                        info['value'][port_data[i].id] = portfisheryoutput.value
                        else:
                            port_data.remove(port_data[i])
                    except:
                        port_data.remove(port_data[i])
                output.append(info)
    temp = []
    field_title = [
                    ['id', u'編號'],
                    ['name', u'漁港名稱'],
                    ['place', u'所屬縣市'],
                    ['X', u'X座標'],
                    ['Y', u'Y座標'],
                    ['type', u'漁港類別'],
                    ['img_url',u'照片網址'],
                    ]
    for i in boat: field_title.append([i['type'], i['type']])
    for i in output[0:1]: field_title.append([i['type'], i['type']])
    for i in xrange(len(port_data)):
        try:
            photo=port_data[i].fishingportphoto_set.filter(type = 31).order_by("-name")[0].rUrl()
        except:
            noimg = FishingPort.objects.get(id =1)
            photo=''
        temp.append({
                        'id': port_data[i].id,
                        'name': port_data[i].name,
                        'place': port_data[i].place.name,
                        'X': str(port_data[i].xcoord),
                        'Y': str(port_data[i].ycoord),
                        'type': port_data[i].type.value,
                        'img_url':photo
        })
        for j in boat:
            temp[i][j['type']] = j['value'][port_data[i].id]
        for j in output:
            temp[i][j['type']] = j['value'][port_data[i].id]

    return HttpResponse(json.write([temp, field_title]))

def searchList(R):
    try:
        search_string = R.GET["search"]
    except:
        search_string = ""

    return render_to_response(os.path.join('gis', 'list.html'), {"search_string":search_string})

def option_group(R):
    user, DATA = R.user, readDATA(R)
    region_list={}
    port_type_list={}
    boat_type_list={}
    region = Place.objects.filter(uplevel = 1)
    for r in region:
        region_list[r.id] = {"text":r.name}
    port = HARBOR_option.objects.filter(swarm = 'fishingport_type')
    for p in port:
        port_type_list[p.id] = {"text":p.value}
    boat = HARBOR_option.objects.filter(swarm = 'boat_type')
    for b in boat:
        boat_type_list[b.id] = {"text":b.value}
    options = {}
    try:
        if _ca(user=user, project='', project_id=0, right_type_value='GIS詳細搜尋'):
            num_compare = {"more_than":{"text":u"大於", "type": "text"},"between":{"text":u"介於", "type": "between_text"},"less_than":{"text":u"小於", "type": "text"}}
            options["1"] = {"text":u"縣市(可多值)", "type": "selector", "option":region_list}
            options["2"] = {"text":u"漁港類型", "type": "selector", "option":port_type_list}
            options["3"] = {"text":u"漁港名稱", "type": "text"}
            options["4"] = {"text":u"漁船種類","type":"selector","option":boat_type_list}
            options["5"]={"text":u"漁獲產值(仟元)","type":"selector","option":num_compare}
            for i in options["4"]["option"]:
                options["4"]["option"][i]["type"] = "selector"
                options["4"]["option"][i]["option"] = num_compare
        else:
            options["1"] = {"text":u"縣市(可多值)", "type": "selector", "option":region_list}
    except:
        options["1"] = {"text":u"縣市(可多值)", "type": "selector", "option":region_list}

    return HttpResponse(json.write(options))

def findLatlng(R):
    return render_to_response(os.path.join('gis', 'findlatlng.html'))


def _demarcatePort(lat, lng):
    ports = FishingPort.objects.all()
    distance = None
    location = None
    for p in ports:
        if p.ycoord and p.xcoord:
            d = ((p.ycoord - decimal.Decimal(str(lat)))**2 + (p.xcoord - decimal.Decimal(str(lng)))**2)
            if not distance or d < distance:
                distance = d
                location = p
    return location


def _searchPhoto(top, bottom, left, right):
    top, bottom, left, right = decimal.Decimal(str(top)), decimal.Decimal(str(bottom)), decimal.Decimal(str(left)), decimal.Decimal(str(right))
    photos = PortPhotos.objects.filter(lat__lte=top, lat__gte=bottom, lng__gte=left, lng__lte=right)
    return list(photos)


def _rEXIFGISCode(file):
    image = open(file, 'rb')
    tags = EXIF.process_file(image)
    try:
        lat = tags["GPS GPSLatitude"].printable[1:-1].split(', ')
        lng =  tags["GPS GPSLongitude"].printable[1:-1].split(', ')
    except:
        return False

    lat_val = (int(lat[0]) + int(lat[1])/60.0 + int(lat[2].split('/')[0])/3600000000.0)
    lng_val = (int(lng[0]) + int(lng[1])/60.0 + int(lng[2].split('/')[0])/36000000000.0)
    return [decimal.Decimal(str(lat_val)), decimal.Decimal(str(lng_val))]


def _rEXIFTime(file):
    image = open(file, 'rb')
    tags = EXIF.process_file(image)
    try:
        time = tags["Image DateTime"].values.split(' ')[0].replace(':', '-') + ' ' + tags["Image DateTime"].values.split(' ')[1]
        return time
    except:
        return None


def PhotoUpLoad(R):
    user, file, data = R.user, R.FILES, R.POST
    try:
        if not _ca(user=user, project='', project_id=0, right_type_value='GIS詳細搜尋'):
            return HttpResponse('{status:"user_upload_error"}')
    except:
        return HttpResponse('{status:"user_upload_error"}')
    photo_lat = decimal.Decimal(str(data.get('lat', None)))
    photo_lng = decimal.Decimal(str(data.get('lng', None)))
    port = _demarcatePort(photo_lat, photo_lng)
    title = data.get('title', None)
    memo = data.get('describe', None)
    imagefile = file.get('imageFile', None)
    time = TODAY()

    try:
        im = Image.open(imagefile)
    except:
        return HttpResponse('{status:"image_error"}')

    if not title:
        return HttpResponse('{status:"title_error"}')

    row = PortPhotos(
            fishingport = port,
            lat = photo_lat,
            lng = photo_lng,
            name = title,
            memo = memo,
            uploader = user,
            uploadtime = time,
    )
    row.save()
    getattr(row, 'file').save('%s.%s'%(row.id, 'jpg'), imagefile)
    row.save()

    path = os.path.join(ROOT, row.file.name)
    time = _rEXIFTime(path)

    setattr(row, 'shoot_time',time)
    row.save()
    
    im = Image.open(path)
    new_name = str(row.id) + '.jpg'
    old_name = path.split('/')[-1]
    new_file = path.replace(old_name, new_name)
    im.save(new_file, "JPEG")
    w = im.size[0]/320.0
    h = im.size[1]/240.0
    if w >= h:
        thumb = im.resize( (320, int(im.size[1]/w)), Image.BILINEAR )
    else:
        thumb = im.resize( (int(im.size[0]/h), 240), Image.BILINEAR )
    thumb_name = new_file.replace(new_name, str(row.id) + '_w320h240.jpg')
    thumb.save(thumb_name, "JPEG")
    
    row.file.name = str(row.file).replace(old_name, new_name)
    row.save()
    
    if row.file:
        if row.uploader == user:
            right = 'true'
        else:
            right = 'false'
        url = row.rUrl()
        thumb = row.rThumbUrl()
        content = '{"id":"'
        content += str(row.id)
        content += '", "title":"'
        content += str(row.name).replace('"', '\\"')
        content += '", "describe":"'
        content += str(row.memo).replace('"', '\\"').replace("\r\n", "\\r\\n")
        content += '", "lat":'
        content += str(row.lat)
        content += ', "lng":'
        content += str(row.lng)
        content += ', "right":'
        content += right
        content += ', "src":"'
        content += url
        content += '", "thumb":"'
        content += thumb
        content += '", "owner":"'
        content += row.uploader.user_profile.rName()
        content += '", "time":"'
        content += str(row.uploadtime)
        content += '", "shoot_time":"'
        content += str(row.shoot_time)
        content += '", "port_name":"'
        content += str(row.fishingport.name)
        content += '"}'

    return HttpResponse('{status:"accept", data:' + content + '}')


def EXIFPhotoUpLoad(R):
    user, file, data = R.user, R.FILES, R.POST
    try:
        if not _ca(user=user, project='', project_id=0, right_type_value='GIS詳細搜尋'):
            return HttpResponse('{status:"user_upload_error"}')
    except:
        return HttpResponse('{status:"user_upload_error"}')

    title = data.get('title', None)
    memo = data.get('describe', None)
    imagefile = file.get('imageFile', None)
    time = TODAY()

    try:
        im = Image.open(imagefile)
    except:
        return HttpResponse('{status:"image_error"}')

    if not title:
        return HttpResponse('{status:"title_error"}')

    row = PortPhotos(
            name = title,
            memo = memo,
            uploader = user,
            uploadtime = time,
    )
    row.save()
    getattr(row, 'file').save('%s.%s'%(row.id, 'jpg'), imagefile)
    row.save()

    path = os.path.join(ROOT, row.file.name)
    coord = _rEXIFGISCode(path)
    time = _rEXIFTime(path)

    if not coord:
        row.delete()
        return HttpResponse('{status:"gps_error"}')

    port = _demarcatePort(coord[0], coord[1])
    setattr(row, 'fishingport',port)
    row.save()
    setattr(row, 'lat',coord[0])
    row.save()
    setattr(row, 'lng',coord[1])
    row.save()
    setattr(row, 'shoot_time',time)
    row.save()

    im = Image.open(path)
    new_name = str(row.id) + '.jpg'
    old_name = path.split('/')[-1]
    new_file = path.replace(old_name, new_name)
    im.save(new_file, "JPEG")
    w = im.size[0]/320.0
    h = im.size[1]/240.0
    if w >= h:
        thumb = im.resize( (320, int(im.size[1]/w)), Image.BILINEAR )
    else:
        thumb = im.resize( (int(im.size[0]/h), 240), Image.BILINEAR )
    thumb_name = new_file.replace(new_name, str(row.id) + '_w320h240.jpg')
    thumb.save(thumb_name, "JPEG")

    row.file.name = str(row.file).replace(old_name, new_name)
    row.save()

    if row.file:
        if row.uploader == user:
            right = 'true'
        else:
            right = 'false'
        url = row.rUrl()
        thumb = row.rThumbUrl()
        content = '{"id":"'
        content += str(row.id)
        content += '", "title":"'
        content += str(row.name).replace('"', '\\"')
        content += '", "describe":"'
        content += str(row.memo).replace('"', '\\"').replace("\r\n", "\\r\\n")
        content += '", "lat":'
        content += str(row.lat)
        content += ', "lng":'
        content += str(row.lng)
        content += ', "right":'
        content += right
        content += ', "src":"'
        content += url
        content += '", "thumb":"'
        content += thumb
        content += '", "owner":"'
        content += row.uploader.user_profile.rName()
        content += '", "time":"'
        content += str(row.uploadtime)
        content += '", "shoot_time":"'
        content += str(row.shoot_time)
        content += '", "port_name":"'
        content += str(row.fishingport.name)
        content += '"}'

    return HttpResponse('{status:"accept", data:' + content + '}')


def photoSearch(R):
    user = R.user
    photos = _searchPhoto(R.GET['top'], R.GET['bottom'], R.GET['left'], R.GET['right'])
    images = '{'
    for p in photos:
        if not p.disable and p.file:
            if p.uploader == user:
                right = 'true'
            else:
                right = 'false'
            url = p.rUrl()
            thumb = p.rThumbUrl()
            content = '"'
            content += str(p.id)
            content += '":'
            content += ' {"title":"'
            content += str(p.name).replace('"', '\\"')
            content += '", "describe":"'
            content += str(p.memo).replace('"', '\\"').replace("\r\n", "\\r\\n")
            content += '", "lat":'
            content += str(p.lat)
            content += ', "lng":'
            content += str(p.lng)
            content += ', "right":'
            content += right
            content += ', "src":"'
            content += url
            content += '", "thumb":"'
            content += thumb
            content += '", "owner":"'
            content += p.uploader.user_profile.rName()
            content += '", "time":"'
            content += str(p.uploadtime)
            content += '", "port_name":"'
            content += str(p.fishingport.name)
            content += '"}'
            images += content
            images += ','

    if len(photos) > 1:
        images = images[:-1] + '}'
    else:
        images += '}'
 
    return HttpResponse(images)


def photoDisable(R, **kw):
    user = R.user
    row = PortPhotos.objects.get(id=kw['photo_id'])

    deny = [4, 5, 7, 10, 12, 13]
    if user.user_profile.group in deny:
        right = False
    else:
        right = True
    if user == row.uploader:
        right = True
    if user.is_staff:
        right = True

    if right:
        row.delete()
        return HttpResponse('{status:"accept"}')
    else:
        return HttpResponse('{status:"user_delete_error"}')


def readImage(R, **kw):
    user = R.user
    image = PortPhotos.objects.get(id=kw['photo_id'])

    if image.file:
        if image.uploader == user:
            right = 'true'
        else:
            right = 'false'
        url = image.rUrl()
        thumb = image.rThumbUrl()
        content = '{"'
        content += str(image.id)
        content += '":'
        content += ' {"title":"'
        content += str(image.name).replace('"', '\\"')
        content += '", "describe":"'
        content += str(image.memo).replace('"', '\\"').replace("\r\n", "\\r\\n")
        content += '", "lat":'
        content += str(image.lat)
        content += ', "lng":'
        content += str(image.lng)
        content += ', "own":'
        content += right
        content += ', "src":"'
        content += url
        content += '", "thumb":"'
        content += thumb
        content += '", "owner":"'
        content += image.uploader.user_profile.rName()
        content += '", "time":"'
        content += str(image.uploadtime)
        content += '", "port_name":"'
        content += str(image.fishingport.name)
        content += '"}}'
    return HttpResponse(content)


def openImage(R, **kw):
    user = R.user
    image = PortPhotos.objects.get(id=kw['photo_id'])
    path = os.path.join(ROOT, image.file)
    return HttpResponse(FileIterWrapper(open(rpath)), content_type="image/jpg")




