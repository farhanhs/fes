#-*- coding: utf8 -*-
from lxml import etree
from zipfile import ZipFile, ZIP_DEFLATED
from re import compile, sub
from copy import deepcopy
from cStringIO import StringIO
from tempfile import TemporaryFile
from ntpath import splitext, basename


nsprefixes = {
    # Text Content
    'mv':'urn:schemas-microsoft-com:mac:vml',
    'mo':'http://schemas.microsoft.com/office/mac/office/2008/main',
    've':'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'o':'urn:schemas-microsoft-com:office:office',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'm':'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'v':'urn:schemas-microsoft-com:vml',
    'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w10':'urn:schemas-microsoft-com:office:word',
    'wne':'http://schemas.microsoft.com/office/word/2006/wordml',
    # Drawing
    'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic':'http://schemas.openxmlformats.org/drawingml/2006/picture',
    # Properties (core and extended)
    'cp':"http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    'dc':"http://purl.org/dc/elements/1.1/",
    'dcterms':"http://purl.org/dc/terms/",
    'dcmitype':"http://purl.org/dc/dcmitype/",
    'xsi':"http://www.w3.org/2001/XMLSchema-instance",
    'ep':'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties',
    # Content Types (we're just making up our own namespaces here to save time)
    'ct':'http://schemas.openxmlformats.org/package/2006/content-types',
    # Package Relationships (we're just making up our own namespaces here to save time)
    'pr':'http://schemas.openxmlformats.org/package/2006/relationships'
    }


def rDocx(file):
    """
    利用 ZipFile 讀取 docx 的檔案內容。
    """
    mydoc = ZipFile(file)
    doc = {}
    for name in mydoc.namelist():
        if name.endswith((".xml", ".rels")):
            xmlcontent = mydoc.read(name)
            document = etree.fromstring(xmlcontent)
            doc[name] = document
        else:
            doc[name] = mydoc.read(name)
    return doc


def rDocument(doc):
    """
    讀取 docx 內的 document.xml 檔案。
    """
    return doc["word/document.xml"]


def rDocBody(document):
    """
    截取 document.xml 內的 body 區段。
    """
    return document.xpath("/w:document/w:body", namespaces=nsprefixes)[0]


def rRels(doc):
    """
    讀取 docx 內的媒體關聯紀錄檔 document.xml.rels。
    """
    return doc["word/_rels/document.xml.rels"]


def rRelations(doc):
    """
    讀取媒體關聯紀錄檔中的所有關聯。
    """
    return rRels(doc).getchildren()


def cElement(tagname, tagtext=None, nsprefix="w", attributes=None, attrnsprefix=None):
    """
    製造 etree 元件。
    """
    namespacemap = None
    if isinstance(nsprefix, list):
        namespacemap = {}
        for prefix in nsprefix: namespacemap[prefix] = nsprefixes[prefix]
        nsprefix = nsprefix[0]

    if nsprefix: namespace = '{'+nsprefixes[nsprefix]+'}'
    else: namespace = ''
    newelement = etree.Element(namespace+tagname, nsmap=namespacemap)

    if attributes:
        if not attrnsprefix:
            if nsprefix == 'w': attributenamespace = namespace
            else: attributenamespace = ''
        else: attributenamespace = '{'+nsprefixes[attrnsprefix]+'}'

        for tagattribute in attributes:
            newelement.set(attributenamespace+tagattribute, attributes[tagattribute])
    if tagtext: newelement.text = tagtext
    return newelement


def cPagebreak(type='page', orient='portrait'):
    """
    製造分頁符號。
    """
    validtypes = ['page', 'section']
    if type not in validtypes:
        raise ValueError('Page break style "%s" not implemented. Valid styles: %s.' % (type, validtypes))
    pagebreak = cElement('p')
    if type == 'page':
        run = cElement('r')
        br = cElement('br',attributes={'type':type})
        run.append(br)
        pagebreak.append(run)
    elif type == 'section':
        pPr = cElement('pPr')
        sectPr = cElement('sectPr')
        if orient == 'portrait':
            pgSz = cElement('pgSz',attributes={'w':'12240','h':'15840'})
        elif orient == 'landscape':
            pgSz = cElement('pgSz',attributes={'h':'12240','w':'15840', 'orient':'landscape'})
        sectPr.append(pgSz)
        pPr.append(sectPr)
        pagebreak.append(pPr)
    return pagebreak


def _replace(document, search, replace, bs=3):
    """
    以正規表示式搜尋 etree 元件並進行取代。
    """
    newdocument = document
    searchre = compile(search)
    searchels = []

    for element in newdocument.iter():
        if element.tag == "{%s}t" % nsprefixes["w"]:
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
                            txtsearch = ""
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
                                            p = findTypeParent(searchels[i], "{%s}p" % nsprefixes["w"])
                                            searchels[i].text = re.sub(search, "", txtsearch)
                                            insindex = p.getparent().index(p) + 1
                                            for r in replace:
                                                p.getparent().insert(insindex, r)
                                                insindex += 1
                                        else: searchels[i].text = sub(search, replace, txtsearch)
                                        replaced = True
                                    else: searchels[i].text = ""
    return newdocument


def replaceText(document, dict):
    """
    取代 document 內的文字。

    dict: {"placeholder": "actual_value"}
    """
    newdocument = document
    for key, value in dict.items():
        newdocument = _replace(newdocument, u"\<\$%s\$\>"%key, value)
    return newdocument


def replaceImage(doc, dict):
    """
    取代 doc 內的圖片。

    dict: {"origin_image_name": "image_path"}
    """
    relations = rRelations(doc)

    for key, path in dict.items():
        name = "%s.png" % splitext(basename(path))[0]
        for r in relations:
            rId, type, target = r.values()
            if key in target:
                r.set("Target", target.replace(key, name))

        image = open(path, "rb")
        byte = str(image.read())
        image.close()
        doc["word/media/%s" % name] = byte

    return doc


def appendDoc(main_doc, temp_doc):
    """
    將 temp doc 加到 main doc 中。
    包括文字內容、圖片與媒體關聯。
    """
    main_body = rDocBody(rDocument(main_doc))
    temp_body = rDocBody(rDocument(temp_doc))

    starter = len(rRelations(main_doc)) + 1
    for r in rRelations(temp_doc):
        rId, type, target = r.values()
        if "relationships/image" in type:
            for element in temp_body.iter():
                keys, value = element.keys(), element.values()
                if rId in value:
                    element.set(keys[0], "rId%s"%starter)
                    r.set("Id", "rId%s"%starter)
                    main_doc["word/_rels/document.xml.rels"].append(r)
                    starter +=1
            main_doc["word/%s" % target] = str(temp_doc["word/%s" % target])
    main_body.append(temp_body)
    return main_doc


def outputDocx(doc, images=None):
    """
    輸出 docx 至記憶體中。
    """
    temp = StringIO()
    docxfile = ZipFile(temp, mode="w", compression=ZIP_DEFLATED)
    for name in doc:
        if name.endswith((".xml", ".rels")):
            data = etree.tostring(doc[name], pretty_print=True)
            docxfile.writestr(name, data)
        else:
            docxfile.writestr(name, doc[name])
    docxfile.close()
    return temp