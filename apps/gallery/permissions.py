#-*- coding: utf8 -*-
"""
預設群組（:class:`django.contrib.auth.models.Group`）說明：
    * IM_MANAGER：管理人員，可編輯所有物件。
    * IM_VIEWER：觀察者，可檢視所有物件。
    * IM_UPLOADER：相片上傳者，僅能上傳相片至查驗點、並對其上傳之相片進行修改或刪除。
"""
MAJOR_ENGINEER_NAME = u'負責主辦工程師'
MINOR_ENGINEER_NAME = u'協同主辦工程師'
INSPECTOR_NAME = u'監造廠商'
CONTRACTOR_NAME = u'營造廠商'

IM_PERMISSIONS = {
    INSPECTOR_NAME: [
        'view_case',
        'create_node',
        'update_node',
        'remove_node',
        'upload_photo',
        'update_photo',
        'remove_photo',
        'create_comment',
        'update_comment',
        'remove_comment',
    ],
    CONTRACTOR_NAME: [
        'view_case',
        'upload_photo',
        'update_photo',
        'create_comment',
    ],
    MAJOR_ENGINEER_NAME: [
        'view_case',
        'create_node',
        'update_node',
        'remove_node',
        'upload_photo',
        'update_photo',
        'remove_photo',
        'create_comment',
        'update_comment',
        'remove_comment',
        'verify_public',
    ],
    MINOR_ENGINEER_NAME: [
        'view_case',
        'create_node',
        'update_node',
        'remove_node',
        'upload_photo',
        'update_photo',
        'remove_photo',
        'create_comment',
        'update_comment',
        'remove_comment',
        'verify_public',
    ]
}
