#-*- coding: utf8 -*-
from os.path import join, dirname
from PIL import Image
from lxml import etree
from zipfile import ZipFile, ZIP_DEFLATED
from re import compile, sub
from math import ceil
from copy import deepcopy
from cStringIO import StringIO
from tempfile import TemporaryFile
from ntpath import splitext, basename

try: from settings import PHOTODOC
except ImportError: PHOTODOC = []


nsprefixes = {
    # Text Content
    "mv":"urn:schemas-microsoft-com:mac:vml",
    "mo":"http://schemas.microsoft.com/office/mac/office/2008/main",
    "ve":"http://schemas.openxmlformats.org/markup-compatibility/2006",
    "o":"urn:schemas-microsoft-com:office:office",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m":"http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v":"urn:schemas-microsoft-com:vml",
    "w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w10":"urn:schemas-microsoft-com:office:word",
    "wne":"http://schemas.microsoft.com/office/word/2006/wordml",
    # Drawing
    "wp":"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a":"http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic":"http://schemas.openxmlformats.org/drawingml/2006/picture",
    # Properties (core and extended)
    "cp":"http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc":"http://purl.org/dc/elements/1.1/",
    "dcterms":"http://purl.org/dc/terms/",
    "dcmitype":"http://purl.org/dc/dcmitype/",
    "xsi":"http://www.w3.org/2001/XMLSchema-instance",
    "ep":"http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
    # Content Types (we"re just making up our own namespaces here to save time)
    "ct":"http://schemas.openxmlformats.org/package/2006/content-types",
    # Package Relationships (we"re just making up our own namespaces here to save time)
    "pr":"http://schemas.openxmlformats.org/package/2006/relationships"
    }


def opendocx(file):
    '''Open a docx file, return a dictionary containing its contents'''
    mydoc = ZipFile(file)
    doc = {}
    for name in mydoc.namelist():
        if name.endswith(('.xml','.rels')):
            xmlcontent = mydoc.read(name)
            document = etree.fromstring(xmlcontent)
            doc[name] = document
        else:
            doc[name] = mydoc.read(name)
    return doc


def getdocument(doc):
    return doc['word/document.xml']


def getrels(doc):
    return doc['word/_rels/document.xml.rels']


def getrelations(doc):
    return doc['word/_rels/document.xml.rels'].getchildren()


def getdocbody(document):
    return document.xpath('/w:document/w:body', namespaces=nsprefixes)[0]


def _replace(document, search, replace, bs=3):
    newdocument = document
    searchre = compile(search)
    searchels = []

    for element in newdocument.iter():
        if element.tag == '{%s}t' % nsprefixes['w']:
            if element.text:
                searchels.append(element)
                if len(searchels) > bs: searchels.pop(0)

                found = False
                for l in range(1, len(searchels)+1):
                    if found: break
                    for s in range(len(searchels)):
                        if found: break
                        if s+l <= len(searchels):
                            e = range(s, s+l)
                            txtsearch = ''
                            for k in e: txtsearch += searchels[k].text

                            match = searchre.search(txtsearch)
                            if match:
                                found = True
                                curlen = 0
                                replaced = False
                                for i in e:
                                    curlen += len(searchels[i].text)
                                    if curlen > match.start() and not replaced:
                                        if isinstance(replace, etree._Element):
                                            replace = [replace]
                                        if isinstance(replace, (list, tuple)):
                                            p = findTypeParent(searchels[i], '{%s}p' % nsprefixes['w'])
                                            searchels[i].text = re.sub(search, '', txtsearch)
                                            insindex = p.getparent().index(p) + 1
                                            for r in replace:
                                                p.getparent().insert(insindex, r)
                                                insindex += 1
                                        else: searchels[i].text = sub(search, replace, txtsearch)
                                        replaced = True
                                    else: searchels[i].text = ''
    return newdocument


def replaceText(document, dict):
    """
    dict: {"placeholder": "actual_value"}
    """
    newdocument = document
    for key, value in dict.items():
        newdocument = _replace(newdocument, u"\<\$%s\$\>"%key, value)
    return newdocument


def _set_image_data(doc, img_rid, img_path):
    document = getdocument(doc)
    img = Image.open(img_path)
    width, height = img.size
    width, height = float(width), float(height)
    del img

    for element in document.iter():
        if element.tag == "{%s}drawing" % nsprefixes["w"]:
            idtag = element.find("%s/%s/%s/%s/%s/%s" % ("{%s}inline" % nsprefixes["wp"], "{%s}graphic" % nsprefixes["a"],
                                                        "{%s}graphicData" % nsprefixes["a"], "{%s}pic" % nsprefixes["pic"],
                                                        "{%s}blipFill" % nsprefixes["pic"], "{%s}blip" % nsprefixes["a"], ))
            if idtag.get("{%s}embed" % nsprefixes["r"]) == img_rid:
                doc_pr = element.find("%s/%s" % ("{%s}inline" % nsprefixes["wp"], "{%s}docPr" % nsprefixes["wp"]))
                nv_pr = element.find("%s/%s/%s/%s/%s/%s" % ("{%s}inline" % nsprefixes["wp"], "{%s}graphic" % nsprefixes["a"],
                                                            "{%s}graphicData" % nsprefixes["a"], "{%s}pic" % nsprefixes["pic"],
                                                            "{%s}nvPicPr" % nsprefixes["pic"], "{%s}cNvPr" % nsprefixes["pic"]))
                doc_pr.set("descr", img_path)
                nv_pr.set("descr", img_path)

                extent = element.find("%s/%s" % ("{%s}inline" % nsprefixes["wp"], "{%s}extent" % nsprefixes["wp"]))
                ext = element.find("%s/%s/%s/%s/%s/%s/%s" % ("{%s}inline" % nsprefixes["wp"], "{%s}graphic" % nsprefixes["a"],
                                                            "{%s}graphicData" % nsprefixes["a"], "{%s}pic" % nsprefixes["pic"],
                                                            "{%s}spPr" % nsprefixes["pic"], "{%s}xfrm" % nsprefixes["a"],
                                                            "{%s}ext" % nsprefixes["a"]))

                ex_w, wx_h = float(extent.get("cx")), float(extent.get("cy"))

                im_ratio = height / width
                ex_ratio = wx_h / ex_w
                if im_ratio < ex_ratio: scale = ex_w / width
                else: scale = wx_h / height

                scale_h = str(int(scale * height))
                scale_w = str(int(scale * width))

                extent.set("cx", scale_w)
                extent.set("cy", scale_h)
                ext.set("cx", scale_w)
                ext.set("cy", scale_h)

                break
    return doc


def replaceImage(doc, dict):
    """
    dict: {"origin_image_name": "image_path"}
    """
    relations = getrelations(doc)

    for key, path in dict.items():
        name = "%s.png" % splitext(basename(path))[0]
        for r in relations:
            rId, type, target = r.values()
            if key in target:
                r.set("Target", target.replace(key, name))
                _set_image_data(doc, rId, path)

        image = open(path, 'rb')
        byte = str(image.read())
        image.close()
        doc['word/media/%s' % name] = byte
    return doc


def appendDoc(main_doc, temp_doc):
    main_body = getdocbody(getdocument(main_doc))
    temp_body = getdocbody(getdocument(temp_doc))

    starter = len(getrelations(main_doc)) + 1
    for r in getrelations(temp_doc):
        rId, type, target = r.values()
        if "relationships/image" in type:

            for element in temp_body.iter():
                keys, value = element.keys(), element.values()
                if rId in value:
                    element.set(keys[0], "rId%s"%starter)
                    r.set("Id", "rId%s"%starter)
                    main_doc['word/_rels/document.xml.rels'].append(r)
                    starter +=1

            main_doc['word/%s' % target] = str(temp_doc['word/%s' % target])

    main_body.append(temp_body)
    return main_doc


def outputdocx(doc, images=None):
    temp = StringIO()
    docxfile = ZipFile(temp, mode='w', compression=ZIP_DEFLATED)
    for name in doc:
        if name.endswith(('.xml','.rels')):
            data = etree.tostring(doc[name], pretty_print=True, encoding='utf8')
            docxfile.writestr(name, data)
        else:
            docxfile.writestr(name, doc[name])
    docxfile.close()
    return temp


def make_examine_doc(img_list):
    total = float(len(img_list))
    name, page_unit = False, False
    for doc in PHOTODOC:
        if doc["doc"] == "examine":
            name = doc["name"]
            page_unit = doc["page_unit"]

    if not page_unit: return False
    if total:
        pages = int(ceil(total / page_unit))
        head = False
        for index in xrange(pages):
            if index == (pages - 1): book = opendocx(join(dirname( __file__ ), "static", "docx", "examine_%s.docx" % len(img_list)))
            else: book = opendocx(join(dirname( __file__ ), "static", "docx", "examine_%s.docx" % int(page_unit)))
            book_document = getdocument(book)

            text_dict, image_dict = {"NAME": img_list[0].node.case.parent.name, "PAGE": str(index+1), "TOTAL": str(pages)}, {}
            for i in xrange(1, page_unit+1):
                text_dict["DATE_%s"%i], text_dict["NOTE_%s"%i], text_dict["CONTENT_%s"%i] = "", "", ""

            for i in xrange(1, page_unit+1):
                if len(img_list):
                    img = img_list.pop(0)
                    if img.time: text_dict["DATE_%s" % i] = img.time.strftime('%Y{y}%m{m}%d{d}').format(y=u'', m=u'', d=u'').decode("utf8")
                    else: text_dict["DATE_%s" % i] = ""
                    text_dict["NOTE_%s" % i] = img.note or ""
                    text_dict["CONTENT_%s" % i] = img.node.rPath()
                    image_dict["image%s.png" % i] = img.rThumbnail(size="document").rPath()

            book_document = replaceText(book_document, text_dict)
            book = replaceImage(book, image_dict)
            if not head:
                head = book
                head_document = book_document
                head_body = getdocbody(book_document)
            else:
                temp = book
                head = appendDoc(head, temp)
        return outputdocx(head)
    else: pass


def make_construction_photo_doc(img_list):
    total = float(len(img_list))
    name, page_unit = False, False
    for doc in PHOTODOC:
        if doc["doc"] == "construction_photo":
            name = doc["name"]
            page_unit = doc["page_unit"]

    if not page_unit: return False
    if total:
        pages = int(ceil(total / page_unit))
        head = False
        for index in xrange(pages):
            if index == (pages - 1): book = opendocx(join(dirname( __file__ ), "static", "docx", "construction_photo_%s.docx" % len(img_list)))
            else: book = opendocx(join(dirname( __file__ ), "static", "docx", "construction_photo_%s.docx" % int(page_unit)))
            book_document = getdocument(book)

            try: unit = img_list[0].node.case.parent.frcmusergroup_set.filter(group__id=4).first().user.user_profile.unit.name or ""
            except: unit = ""
            text_dict, image_dict = {"NAME": img_list[0].node.case.parent.name, "COMPANY": unit}, {}
            for i in xrange(1, page_unit+1):
                text_dict["CONTENT_%s"%i] = ""

            for i in xrange(1, page_unit+1):
                if len(img_list):
                    img = img_list.pop(0)
                    text_dict["CONTENT_%s" % i] = img.node.rPath()
                    image_dict["image%s.png" % i] = img.rThumbnail(size="document").rPath()

            book_document = replaceText(book_document, text_dict)
            book = replaceImage(book, image_dict)
            if not head:
                head = book
                head_document = book_document
                head_body = getdocbody(book_document)
            else:
                temp = book
                head = appendDoc(head, temp)
        return outputdocx(head)
    else: pass


def make_maintain_six_photo_doc(img_list):
    total = float(len(img_list))
    name, page_unit = False, False
    for doc in PHOTODOC:
        if doc["doc"] == "maintain":
            name = doc["name"]
            for sub in doc["sub"]:
                if sub["doc"] == "maintain_6":
                    page_unit = sub["page_unit"]
                    break
            break

    if not page_unit: return False
    if total:
        pages = int(ceil(total / page_unit))
        head = False
        for index in xrange(pages):
            if index == (pages - 1): book = opendocx(join(dirname( __file__ ), "static", "docx", "maintain_six_%s.docx" % str(len(img_list) + (len(img_list)%2 > 0))))
            else: book = opendocx(join(dirname( __file__ ), "static", "docx", "maintain_six_%s.docx" % int(page_unit)))
            book_document = getdocument(book)

            text_dict, image_dict = {"NAME": img_list[0].node.case.parent.name, "TITLE": u"%s %s 年 %s 月" % (img_list[0].node.name, str(img_list[0].time.year-1911), img_list[0].time.month)}, {}
            for i in xrange(1, page_unit+1):
                text_dict["NOTE_%s"%i] = ""

            for i in xrange(1, page_unit+1):
                if len(img_list):
                    img = img_list.pop(0)
                    text_dict["NOTE_%s" % i] = img.note or ""
                    image_dict["image%s.png" % i] = img.rThumbnail(size="document").rPath()

            book_document = replaceText(book_document, text_dict)
            book = replaceImage(book, image_dict)
            if not head:
                head = book
                head_document = book_document
                head_body = getdocbody(book_document)
            else:
                temp = book
                head = appendDoc(head, temp)
        return outputdocx(head)
    else: pass


def make_maintain_nine_photo_doc(img_list):
    total = float(len(img_list))
    name, page_unit = False, False
    for doc in PHOTODOC:
        if doc["doc"] == "maintain":
            name = doc["name"]
            for sub in doc["sub"]:
                if sub["doc"] == "maintain_9":
                    page_unit = sub["page_unit"]
                    break
            break

    if not page_unit: return False
    if total:
        pages = int(ceil(total / page_unit))
        head = False
        for index in xrange(pages):
            if index == (pages - 1): book = opendocx(join(dirname( __file__ ), "static", "docx", "maintain_nine_%s.docx" % str((len(img_list)/3 + (len(img_list)%3 > 0))*3)))
            else: book = opendocx(join(dirname( __file__ ), "static", "docx", "maintain_nine_%s.docx" % int(page_unit)))
            book_document = getdocument(book)

            text_dict, image_dict = {"NAME": img_list[0].node.case.parent.name, "DATE": u"%s 年 %s 月 %s 日" % (str(img_list[0].time.year-1911), img_list[0].time.month, img_list[0].time.day)}, {}
            for i in xrange(1, page_unit+1):
                text_dict["NOTE_%s"%i] = ""

            for i in xrange(1, page_unit+1):
                if len(img_list):
                    img = img_list.pop(0)
                    text_dict["NOTE_%s" % i] = img.note or ""
                    image_dict["image%s.png" % i] = img.rThumbnail(size="document").rPath()

            book_document = replaceText(book_document, text_dict)
            book = replaceImage(book, image_dict)
            if not head:
                head = book
                head_document = book_document
                head_body = getdocbody(book_document)
            else:
                temp = book
                head = appendDoc(head, temp)
        return outputdocx(head)
    else: pass


def make_maintain_twelve_photo_doc(img_list):
    total = float(len(img_list))
    name, page_unit = False, False
    for doc in PHOTODOC:
        if doc["doc"] == "maintain":
            name = doc["name"]
            for sub in doc["sub"]:
                if sub["doc"] == "maintain_12":
                    page_unit = sub["page_unit"]
                    break
            break

    if not page_unit: return False
    if total:
        pages = int(ceil(total / page_unit))
        head = False
        for index in xrange(pages):
            if index == (pages - 1): book = opendocx(join(dirname( __file__ ), "static", "docx", "maintain_twelve_%s.docx" % str((len(img_list)/3 + (len(img_list)%3 > 0))*3)))
            else: book = opendocx(join(dirname( __file__ ), "static", "docx", "maintain_twelve_%s.docx" % int(page_unit)))
            book_document = getdocument(book)

            text_dict, image_dict = {"NAME": img_list[0].node.case.parent.name, "TITLE": img_list[0].node.name}, {}
            for i in xrange(1, page_unit+1):
                text_dict["NOTE_%s"%i] = ""
                text_dict["NODE_%s"%i] = ""

            for i in xrange(1, page_unit+1):
                if len(img_list):
                    img = img_list.pop(0)
                    text_dict["NOTE_%s" % i] = img.note or ""
                    text_dict["NODE_%s" % i] = img.node.name
                    image_dict["image%s.png" % i] = img.rThumbnail(size="document").rPath()

            book_document = replaceText(book_document, text_dict)
            book = replaceImage(book, image_dict)
            if not head:
                head = book
                head_document = book_document
                head_body = getdocbody(book_document)
            else:
                temp = book
                head = appendDoc(head, temp)
        return outputdocx(head)
    else: pass