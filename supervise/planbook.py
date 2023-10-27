#-*- coding: utf8 -*-
from os.path import join, dirname
from zipfile import ZipFile, ZIP_DEFLATED
from cStringIO import StringIO
from docgen.docxlib import rDocx, rDocument, rDocBody, cPagebreak, replaceText, replaceImage, appendDoc, outputDocx
from docgen.models import Item


SUPERVISION_TEMPLATE_PATH = join(dirname( __file__ ), "templates", "docx", "supervision.docx")
QUALITY_TEMPLATE_PATH = join(dirname( __file__ ), "templates", "docx", "quality.docx")
CONSTRUCTION_TEMPLATE_PATH = join(dirname( __file__ ), "templates", "docx", "construction.docx")
WORK_TEMPLATE_PATH = join(dirname( __file__ ), "templates", "docx", "work_list.docx")


def cSupervisionBook(text_dict={}, items=[]):
    """
    產生監造計畫書檔案。

    :param text_dict: 取代字集，可包含以下資料：
        :param 工程名稱: 工程名稱
        :param 工程主辦機關: 工程主辦機關
        :param 工程序號: 工程序號
        :param 監造單位: 監造單位
        :param 契約金額: 契約金額
        :param 承攬廠商: 承攬廠商
        :param 工程地點: 工程地點
        :param 開工日期: 開工日期
        :param 監造單位負責人: 監造單位負責人
        :param 工程期限: 工程期限
        :param 專任工程人員: 專任工程人員
        :param 保固期限: 保固期限
    :param items: 工項
    :text_dict limit: dict
        :name limit: string
        :authority limit: string
        :number limit: string
        :unit limit: string
        :amount limit: string
        :contractor limit: string
        :location limit: string
        :start limit: string
        :charge limit: string
        :term limit: string
        :engineer limit: string
        :warranty limit: string
    :items limit: list of Item(:class:`docgen.models.Item`) Objects

    :rtype: StringIO
    """

    item_detail = [4, 2, 1]

    book = rDocx(SUPERVISION_TEMPLATE_PATH)
    book_document = rDocument(book)
    book_body = rDocBody(book_document)

    text_dict[u"檢查表"] = u"抽查紀錄表"
    text_dict[u"檢查圖"] = u"檢驗流程圖"
    text_dict[u"檢查點"] = u"檢驗停留點"

    for item in items:
        work = rDocx(WORK_TEMPLATE_PATH)
        work_document = replaceText(rDocument(work), {u"工作項目": item.name})
        work_body = rDocBody(work_document)
        book_body.append(work_body)
    book_body.append(cPagebreak())

    for item in items:
        for detail in item_detail:
            template = rDocx(item.item_templates.get(type_id=detail).file.path)
            template_body = rDocBody(rDocument(template))
            book_body.append(template_body)
    
    book_document = replaceText(book_document, text_dict)
    return outputDocx(book)


def cQualityBook(text_dict={}, items=[]):
    """
    產生品質計畫書檔案。

    :param text_dict: 取代字集，可包含以下資料：
        :param 工程名稱: 工程名稱
        :param 工程主辦機關: 工程主辦機關
        :param 工程序號: 工程序號
        :param 監造單位: 監造單位
        :param 契約金額: 契約金額
        :param 承攬廠商: 承攬廠商
        :param 工程地點: 工程地點
        :param 開工日期: 開工日期
        :param 監造單位負責人: 監造單位負責人
        :param 工程期限: 工程期限
        :param 專任工程人員: 專任工程人員
        :param 保固期限: 保固期限
    :param items: 工項
    :text_dict limit: dict
        :name limit: string
        :authority limit: string
        :number limit: string
        :unit limit: string
        :amount limit: string
        :contractor limit: string
        :location limit: string
        :start limit: string
        :charge limit: string
        :term limit: string
        :engineer limit: string
        :warranty limit: string
    :items limit: list of Item(:class:`docgen.models.Item`) Objects

    :rtype: StringIO
    """

    item_detail = [3, 4, 2, 5]

    book = rDocx(QUALITY_TEMPLATE_PATH)
    book_document = rDocument(book)
    book_body = rDocBody(book_document)

    text_dict[u"檢查表"] = u"自主檢查表"
    text_dict[u"檢查圖"] = u"自主檢查流程圖"
    text_dict[u"檢查點"] = u"自主檢查停留點"

    for item in items:
        work = rDocx(WORK_TEMPLATE_PATH)
        work_document = replaceText(rDocument(work), {u"工作項目": item.name})
        work_body = rDocBody(work_document)
        book_body.append(work_body)
    book_body.append(cPagebreak())

    for item in items:
        for detail in item_detail:
            template = rDocx(item.item_templates.get(type_id=detail).file.path)
            template_body = rDocBody(rDocument(template))
            book_body.append(template_body)
    
    book_document = replaceText(book_document, text_dict)
    return outputDocx(book)


def cConstructionBook(text_dict={}, items=[]):
    """
    產生施工計畫書檔案。

    :param text_dict: 取代字集，可包含以下資料：
        :param 工程名稱: 工程名稱
        :param 工程主辦機關: 工程主辦機關
        :param 工程序號: 工程序號
        :param 監造單位: 監造單位
        :param 契約金額: 契約金額
        :param 承攬廠商: 承攬廠商
        :param 工程地點: 工程地點
        :param 開工日期: 開工日期
        :param 監造單位負責人: 監造單位負責人
        :param 工程期限: 工程期限
        :param 專任工程人員: 專任工程人員
        :param 保固期限: 保固期限
    :param items: 工項
    :text_dict limit: dict
        :name limit: string
        :authority limit: string
        :number limit: string
        :unit limit: string
        :amount limit: string
        :contractor limit: string
        :location limit: string
        :start limit: string
        :charge limit: string
        :term limit: string
        :engineer limit: string
        :warranty limit: string
    :items limit: list of Item(:class:`docgen.models.Item`) Objects

    :rtype: StringIO
    """

    item_detail = [3, 4, 2, 5]

    book = rDocx(CONSTRUCTION_TEMPLATE_PATH)
    book_document = rDocument(book)
    book_body = rDocBody(book_document)

    text_dict[u"檢查表"] = u"自主檢查表"
    text_dict[u"檢查圖"] = u"自主檢查流程圖"
    text_dict[u"檢查點"] = u"自主檢查停留點"

    for item in items:
        work = rDocx(WORK_TEMPLATE_PATH)
        work_document = replaceText(rDocument(work), {u"工作項目": item.name})
        work_body = rDocBody(work_document)
        book_body.append(work_body)
    book_body.append(cPagebreak())

    for item in items:
        for detail in item_detail:
            template = rDocx(item.item_templates.get(type_id=detail).file.path)
            template_body = rDocBody(rDocument(template))
            book_body.append(template_body)
    
    book_document = replaceText(book_document, text_dict)
    return outputDocx(book)


def cZipFile(data_set={}, item_id=[], supervision=True, quality=True, construction=True):
    """
    產生計畫書壓縮檔。

    :param data_set: 資料集，可包含以下資料：
        :param name: 工程名稱
        :param authority: 工程主辦機關
        :param number: 工程序號
        :param unit: 監造單位
        :param amount: 契約金額
        :param contractor: 承攬廠商
        :param location: 工程地點
        :param start: 開工日期
        :param charge: 監造單位負責人
        :param term: 工程期限
        :param engineer: 專任工程人員
        :param warranty: 保固期限
    :param item_id: 工項 id
    :param supervision: 是否產生監造計畫書
    :param quality: 是否產生品質計畫書
    :param construction: 是否產生施工計畫書

    :data_set limit: dict
        :name limit: string
        :authority limit: string
        :number limit: string
        :unit limit: string
        :amount limit: string
        :contractor limit: string
        :location limit: string
        :start limit: string
        :charge limit: string
        :term limit: string
        :engineer limit: string
        :warranty limit: string
    :item_id limit: list of Item(:class:`docgen.models.Item`) id
    :supervision limit: boolean
    :quality limit: boolean
    :construction limit: boolean

    :rtype: StringIO
    """
    text_dict = {}
    text_dict[u"工程名稱"] = data_set["name"]
    text_dict[u"工程主辦機關"] = data_set["authority"]
    text_dict[u"工程序號"] = data_set["number"]
    text_dict[u"監造單位"] = data_set["unit"]
    text_dict[u"契約金額"] = data_set["amount"]
    text_dict[u"承攬廠商"] = data_set["contractor"]
    text_dict[u"工程地點"] = data_set["location"]
    text_dict[u"開工日期"] = data_set["start"]
    text_dict[u"監造單位負責人"] = data_set["charge"]
    text_dict[u"工程期限"] = data_set["term"]
    text_dict[u"專任工程人員"] = data_set["engineer"]
    text_dict[u"保固期限"] = data_set["warranty"]

    items = [Item.objects.get(id=id) for id in item_id]


    temp = StringIO()
    zipfile = ZipFile(temp, mode='w', compression=ZIP_DEFLATED)

    if supervision:
        file = cSupervisionBook(text_dict=text_dict, items=items)
        zipfile.writestr(u"%s - 監造計畫書.docx"%data_set["name"], file.getvalue())
        file.seek(0)

    if quality:
        file = cQualityBook(text_dict=text_dict, items=items)
        zipfile.writestr(u"%s - 品質計畫書.docx"%data_set["name"], file.getvalue())
        file.seek(0)

    if construction:
        file = cConstructionBook(text_dict=text_dict, items=items)
        zipfile.writestr(u"%s - 施工計畫書.docx"%data_set["name"], file.getvalue())
        file.seek(0)

    zipfile.close()
    return temp