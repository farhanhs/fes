var _s = {
    API_URL: '/gallery/api/v1/',
    BODY: 'body',
    L_HEAD: '#layout_head',
    L_SIDE: '#layout_side',
    L_MAIN: '#layout_main',
    L_TOOL: '#layout_tools',
    L_SHOW: '#layout_images',
    P_LOADING: '#loading_page',
    SUB_TMP: '#sub_layout',
    IMG_TMP: '#img_layout',
    CMT_TMP: '#comment_layout',
    DPI_TMP: '#picked_layout',
    DIV_TMP: '#divider_layout',
    ERROR: '#error_dialog',
    PERMISSION: '#permissions',
    MENU: '#accordion',
    I_LOCATION: '#improve_location',
    T_LOCATION: '#time_location',
    LOCATION: '#node_location',
    CONTROL: '#control',
    BY_IMPROVE: '#by_improve',
    BY_TIME: '#by_time',
    BY_NODE: '#by_node',
    NODETREE: '#node_tree',
    TIMETREE: '#time_tree',
    IMPROVETREE: '#improve_tree',
    B_UPLOAD: '#upload_file',
    B_ODERING: '#odering_photo',
    B_SORTING: '#sorting_photo',
    M_DOWNLOAD: '#{doc}_menu',
    M_ODERING: '#odering_menu',
    M_SORTING: '#sorting_menu',
    UPLOAD_DIALOG: '#upload_dialog',
    CANCEL_DOWNLOAD_PHOTODOC_BUTTON: '#cancel_download',
    START_DOWNLOAD_PHOTODOC_BUTTON: '#start_download',
    SELECT_PANEL: '#select_panel',
    PICKIMG_NOTE: '#picking_note',
    PICKED_IMG: '#picked_img',
    VIEW_PHOTO_FORMAT_BUTTON: '#display_format',
    CANCEL_PREVIEW_PHOTODOC_BUTTON: '#cancel_preview',
    START_PREVIEW_PHOTODOC_BUTTON: '#start_preview',
    PREVIEW_FORM: '#preview_form',
    DOWNLOAD_FORM: '#download_form',
    UPLOADER: '#uploader',
    EDIT_TOOLS: '#edit_tools',
    EDIT_DEL: '#photos_delete',
    EDIT_NOTE: '#photos_edit_note',
    EDIT_DATE: '#photos_edit_date',
    EDIT_PUBLIC: '#photos_edit_public',
    EDIT_CANCEL: '#photos_edit_cancel',
    EDIT_NOTE_DIALOG: '#photos_edit_note_dialog',
    EDIT_NOTE_TEXT: '#edit_photos_note',
    EDIT_DATE_DIALOG: '#photos_edit_date_dialog',
    EDIT_PUBLIC_DIALOG: '#photos_edit_public_dialog',
    EDIT_DATA_INPUT: '#edit_take_date',
    SHOWBOX: '#showbox',
    L_PHOTO: '#showbox_photo',
    L_INFO: '#showbox_info',
    IMPROVE_TAB: '#improvetab_',
    TIME_TAB: '#timetab_',
    NODE_TAB: '#nodetab_',
    IMGPN: '#image_pn',
    CPN: '#current_pn',
    TPN: '#total_pn',
    TURN_CCW: '#turn_ccw',
    TURN_CW: '#turn_cw',
    TURN_SAVE: '#turn_save',
    GRID_ONOFF: '#switch_grid',
    FORMER: '#arrow_left',
    AFTER: '#arrow_right',
    VIEW_TOOLS: '#view_tools',
    LOADING: '#loading_img',
    ANCHOR: '#anchor',
    PAN: '#panlayer',
    DOCK: '#dock',
    IMAGE: '#portrait',
    GRID: '#gird',
    CLOSEBOX: '#close_showbox',
    IMGDATE: '#photo_date',
    IMGNOTE: '#photo_note',
    IMGPUBLIC: '#photo_is_public',
    POSTCMT: '#submit_comment',
    INFOLIST: '#info_list',
    CMTLIST: '#comments_list',
    NOCMT: '#nocomment',
    DO_GUIDE: "#download_oper_guide",
    PICK_BOARD: '.pick_board',
    PICK_CTL: '.picked_ctl',
    PICK_UNIT: '.picked_unit',
    PICK_TB: '.picked_thumb',
    PICK_NO: '.picked_num',
    B_DOWNLOAD: '.download_document',
    N_OPTIONS: '.node_option',
    T_OPTIONS: '.time_option',
    TRACKS: '.tracks',
    CRUMBS: '.select_node',
    DOC_OPT: '.doc_option',
    ORDERING_OPT: '.order_option',
    SORTING_OPT: '.sort_option',
    CTL_PANEL: '.oper_guide',
    INPUTS: '.inputs',
    DOWNLOAD: '.download',
    LAZY: '.lazy',
    SUB_UNIT: '.subnode_unit',
    SUB_MASK: '.subnode_name',
    IMG_UNIT: '.thumbnail_unit',
    IMG_HEAD: '.img_head',
    IMG_DELETE: '.img_remove',
    IMG_MASK: '.img_mask',
    IMG_BLOCK: '.img_block',
    IMG_TB: '.img_thumbnail',
    IMG_TEXT: '.img_text',
    IMG_SELECTED: '.img_selected',
    IMG_TAKE_TIME: '.take_time',
    NO: '.no',
    PAGES: '.pages',
    GRID_ON: '.grid_on',
    GRID_OFF: '.grid_off',
    NEXT: '.preview_next',
    GUT: '.gut',
    PHOTO_ATTR: '.photo_attr',
    PHOTO_TEXT: '.photo_text',
    DEL_CMT: '.delete_comment',
    DRAG_DIV: '.drag_div',
    EDIT_TIP: '.tips',
    IMAGE_COUNT: '.grid_image_count',
    SUB_COUNT: '.grid_sub_count',
    FORMAT_UNIT: '.format_unit',
    FU_FILL: '.format_unit_fill',
    JSTREE_CHECK_CLASS: '.jstree-checkbox',
    UPLOAD_STATUS: '.plupload_total_status',
    CMTAREA: 'textarea[name="comment"]',
    LOCATION_ANCHOT: 'a[node_id={id}]',
    FOLDER_ANCHOT: 'div[node_id={id}]',
    NODETREE_KEY: 'nodetree',
    TIMETREE_KEY: 'timetree',
    OK: '確定',
    NT_FBEDIT: '無編輯權限',
    NT_NAEDIT: '鎖定編輯狀態',
    NT_NEWNODE: '新增查驗點',
    NT_COPY: '複製查驗點',
    NT_PASTE: '貼上查驗點',
    NT_RENAME: '修改名稱',
    NT_REMOVE: '刪除',
    MOVE_NODE_ALERT: '預設資料夾無法移動！',
    IMAGE_COUNT_TIP: '照片數量',
    SUB_COUNT_TIP: '照片數量(本身/含子查驗點)',
    IMP_COUNT_TIP: '照片數量(本身/含子資料夾)',
    LOCATION_TITLE: '目前位置：',
    UPLOAD_TARGET: '上傳至：',
    UPLOAD_LOW_ALERT: '大小不足 90 KB，請挑選正常品質之相片進行上傳！',
    UPLOAD_UP_ALERT: '大小超過 4 MB，請先壓縮後再進行上傳！',
    CUSTOMIPT: '自訂查驗單：',
    SELECT_NONE_ALERT: '請選取欲輸出的查驗照片！',
    NO_IMG_INCLUDE: '所選查驗點不含照片！',
    SORT_ALERT: '依{mode}瀏覽時無法進行手動排序，請於查驗點內的自訂排序模式下操作！',
    SINGLE_DEL_ALERT: '是否刪除檔案 {file}？相關留言也將被刪除！',
    MULTI_DEL_ALERT: '共 {total} 個檔案準備刪除，是否執行？相關留言也將被刪除！',
    MULTI_PART_DEL_ALERT: '共選取 {total} 個檔案，但有 {part} 個檔案無刪除權限，其餘 {execute} 張照片將被刪除，是否執行？相關留言也將被刪除！',
    MULTI_NON_DEL_ALERT: '您並無刪除這 {total} 個檔案的權限，無法執行刪除！',
    MULTI_PART_MOVE_ALERT: '共選取 {total} 個檔案，但有 {part} 個檔案無移動照片的權限，只有 {execute} 張照片移動至『{target}』資料夾！',
    MULTI_NON_MOVE_ALERT: '您並無移動這 {total} 個檔案的權限，無法執行移動！',
    EDIT_NOTE_TIP: '將同時編輯 {total} 個檔案的說明，請輸入新的說明內容。',
    EDIT_DATE_TIP: '將同時更改 {total} 個檔案的拍攝日期，請選擇正確的日期。',
    EDIT_PUBLIC_TIP: '將同時確認或取消 {total} 個檔案的公開狀態，若不想更動請選擇取消。',
    EDIT_DATE_ALERT: '無法在依拍照時間瀏覽時修改日期，須於查驗點中操作。',
    EDIT_ALERT: '將同時修改 {total} 個檔案的資訊，原有資料將被覆蓋，確定修改？',
    PUBLIC_ALERT: '將同時將 {total} 個檔案的狀態改為{state}，是否確定操作？',
    EMP_DATE_ALERT: '未設定日期，檔案拍攝日期將不會被修改。',
    DEL_CMT_ALERT: '是否刪除該留言？',
    ITIME_SORT_ALERT: '依拍照時間瀏覽時片將自動依拍照時間排序，無法操作排序！',
    IMPROVE_SORT_ALERT: '缺失改善照片將自動依改善前中後排序，無法操作排序！',
    IMPROVE_PHOTO_EDIT_ALERT: '缺失改善照片僅提供瀏覽，無法在此編輯！',
    CLOSE_ALERT: '正在上傳照片，是否確定要關閉頁面？',
    PHOTO_FORMAT_TITLE: '文件圖片排列格式',
}


var layout, showbox_dialog, showbox_layout, panobj, refresh_time, target_time, copy_node;


String.prototype.supplant = function (o) {
    return this.replace(/{([^{}]*)}/g,
        function (a, b) {
            var r = o[b];
            return typeof r === 'string' || typeof r === 'number' ? r : a;
        }
    );
};


var REST_ERROR = function (xhr, ajaxOptions, thrownError) {
    var $dialog = $(_s.ERROR);
    var json = $.parseJSON(xhr.responseText);
    var buttons = {};
    buttons['Close'] = function () {
        $(this).dialog('close');
    };
    if (xhr.status == 500) {
        var title = 'Error ' + xhr.status;
        var html = json;
        var width = 1024;
        var height = 800;
    } else {
        var s = '';
        for(var k in json){
            s += k + ': ' + json[k];
        }
        var title = 'Error ' + xhr.status + ' = ' + s;
        var html = '<pre style="color: red; background-color: yellow">'+json['traceback']+'</pre>';
        var width = 600;
        var height = 550;
    }
    $dialog.html(html).dialog({
        title: title,
        buttons: buttons,
        height: height,
        width: width
    })
};


function dialog_width() {
    return Math.floor($(_s.BODY).width()  * .95);
}


function dialog_height() {
    return Math.floor($(_s.BODY).height() * .95);
}


/* 設置介面 */
function initial_layout() {
    layout = $(_s.BODY).layout({
        north: {
            paneSelector: _s.L_HEAD,
            resizable: false,
        },
        west: {
            paneSelector: _s.L_SIDE,
            size: 300,
            onresize: $.layout.callbacks.resizePaneAccordions
        },
        center: {
            paneSelector: _s.L_MAIN,
            childOptions: {
                north: {
                    paneSelector: _s.L_TOOL,
                    resizable: false,
                    spacing_open: 0
                },
                center: {
                    paneSelector: _s.L_SHOW,
                    onresize: resize_element
                }
            }
        }
    });

    $(_s.MENU).accordion({
        heightStyle: 'fill',
        change: function(event, ui) {
            var current_tab = $(_s.MENU).find('.ui-state-active')[0];

            $(_s.TRACKS).hide();
            $(_s.PAGES).hide();
            $(_s.EDIT_TOOLS).hide();
            $(_s.IMG_SELECTED).remove();

            switch (current_tab.id) {
                case _s.BY_IMPROVE.replace('#', ''):
                    $(_s.I_LOCATION).show();

                    var selected = $(_s.IMPROVETREE).jstree('get_selected')[0];
                    if ($(_s.NODE_TAB + selected).length > 0) {
                        $(_s.NODE_TAB + selected).show();
                        check_marked_photo($(_s.NODE_TAB + selected));
                    } else {
                        $('#'+$(_s.IMPROVETREE).jstree('get_selected')[0]).children('a').trigger('click');
                    }
                    // } else if($('#'+$(_s.IMPROVETREE).jstree('get_selected')[0]).length > 0) {
                    //     $('#'+$(_s.IMPROVETREE).jstree('get_selected')[0]).children('a').trigger('click');
                    // } else {
                        // if ($('#'+refresh_time).length > 0) {
                        //     $('#'+refresh_time).children('a').trigger('click');
                        // } else if (target_time) {
                        //     $('#take_'+target_time).children('a').trigger('click');
                        // }
                        // refresh_time = false;
                        // target_time = false;
                    // }
                    break
                case _s.BY_TIME.replace('#', ''):
                    $(_s.T_LOCATION).show();

                    var selected = $(_s.TIMETREE).jstree('get_selected')[0];
                    if ($(_s.TIME_TAB + selected).length > 0) {
                        $(_s.TIME_TAB + selected).show();
                        check_marked_photo($(_s.TIME_TAB + selected));
                    } else if($('#'+$(_s.TIMETREE).jstree('get_selected')[0]).length > 0) {
                        $('#'+$(_s.TIMETREE).jstree('get_selected')[0]).children('a').trigger('click');
                    } else {
                        if ($('#'+refresh_time).length > 0) {
                            $('#'+refresh_time).children('a').trigger('click');
                        } else if (target_time) {
                            $('#take_'+target_time).children('a').trigger('click');
                        }
                        refresh_time = false;
                        target_time = false;
                    }
                    break;
                case _s.BY_NODE.replace('#', ''):
                    $(_s.LOCATION).show();
                    var selected = $(_s.NODETREE).jstree('get_selected')[0];
                    if ($(_s.NODE_TAB + selected).length > 0) {
                        $(_s.NODE_TAB + selected).show();
                        check_marked_photo($(_s.NODE_TAB + selected));
                    } else {
                        $('#'+$(_s.NODETREE).jstree('get_selected')[0]).children('a').trigger('click');
                    }
                    break;
            }
            setup_option();
            layout.resizeAll();
        }
    });
    
    var active = $(_s.MENU).children('div').length - 1;
    $(_s.MENU).accordion('option', 'active', active);
    initial_control();
}


function initial_showbox() {
    if (!showbox_dialog) {
        showbox_dialog = $(_s.SHOWBOX).dialog({
            width: dialog_width(),
            height: dialog_height(),
            autoOpen: false,
            draggable: false,
            closeOnEsc: true,
            modal: true,
            resizable: false,
            // show: 'slide',
            // hide: 'slide',
            open: function() {
                $('.ui-dialog-titlebar').hide();
                $('.ui-widget-overlay').addClass('custom_overlay');
                $('.ui-widget-overlay').click(function() {
                    $(_s.SHOWBOX).dialog('close');
                });
                $(_s.CLOSEBOX).click(function() {
                    $(_s.SHOWBOX).dialog('close');
                });

                if (!showbox_layout) {
                    showbox_layout = $(_s.SHOWBOX).layout({
                        center: {
                            paneSelector: _s.L_PHOTO,
                            onresize: resize_showbox
                        },
                        east: {
                            paneSelector: _s.L_INFO,
                            resizable: false,
                            size: 300,
                            spacing_open: 0
                        }
                    });
                } else {
                    showbox_layout.resizeAll();
                }

                var number = $(_s.SHOWBOX).data('obj');

                setup_showbox(number);
                setup_showbox_element();
            },
            beforeClose: function() {
                $(_s.IMAGE).attr('src', '');
                $('.ui-dialog-titlebar').show();
                $('.ui-widget-overlay').removeClass('custom_overlay');
            },
            close: function() {
                if (refresh_time || target_time) {
                    reflash_time_tree();
                }
            },
            resize: function(){
                if (dialogLayout) {
                    dialogLayout.resizeAll();
                }
            }
        });
    }

    $(_s.IMGDATE).datetimepicker({
        language: 'zh_tw',
        format: 'yyyy-mm-dd',
        weekStart: 1,
        todayBtn:  1,
        autoclose: 1,
        todayHighlight: 1,
        startView: 2,
        minView: 2,
        forceParse: 0,
        pickerPosition: 'bottom-left'
    });

    $(_s.IMGDATE).on('changeDate', function(ev) {
        var index = parseInt($(_s.IMAGE).data('no')) - 1,
            date = $(_s.IMGDATE).data('date');

        var current = $(_s.PAGES).filter(':visible'),
            images = current.find(_s.IMG_UNIT),
            data = $(images[index]).data();

        $(_s.IMG_UNIT).each(function(index, value) {
            if ($(value).data('id') == data['id']) {
                $(value).data('time', date);
            }
        });

        $.ajax({
            url: _s.API_URL + 'photo/' + data['id'] + '/',
            type: 'PUT',
            data: JSON.stringify({'take_date': date}),
            contentType: 'application/json',
            dataType: 'json',
            success: function (comment_data, text, xhr) {
                data['time'] = date;
                refresh_time = 'take_' + date;
                target_time = date;
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    });

    $(_s.IMGNOTE).blur(function() {
        var index = parseInt($(_s.IMAGE).data('no')) - 1,
            note = $(_s.IMGNOTE).val();

        var current = $(_s.PAGES).filter(':visible'),
            images = current.find(_s.IMG_UNIT),
            data = $(images[index]).data();

        $(_s.IMG_UNIT).each(function(index, value) {
            if ($(value).data('id') == data['id']) {
                $(value).data('note', note);
            }
        });
         
        $.ajax({
            url: _s.API_URL + 'photo/' + data['id'] + '/',
            type: 'PUT',
            data: JSON.stringify({'note': note}),
            contentType: 'application/json',
            dataType: 'json',
            success: function (comment_data, text, xhr) {
                data['note'] = note;
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    });

    $(_s.IMGPUBLIC).change(function() {
        var index = parseInt($(_s.IMAGE).data('no')) - 1,
            is_public = $(_s.IMGPUBLIC).is(':checked');

        var current = $(_s.PAGES).filter(':visible'),
            images = current.find(_s.IMG_UNIT),
            data = $(images[index]).data();

        $.ajax({
            url: _s.API_URL + 'photo/' + data['id'] + '/',
            type: 'PUT',
            data: JSON.stringify({'is_public': is_public}),
            contentType: 'application/json',
            dataType: 'json',
            success: function (comment_data, text, xhr) {
                data['is_public'] = is_public;
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    });

    $(_s.POSTCMT).click(function() {
        var index = parseInt($(_s.IMAGE).data('no')) - 1,
            content = $(_s.CMTAREA).val();

        var current = $(_s.PAGES).filter(':visible'),
            images = current.find(_s.IMG_UNIT),
            data = $(images[index]).data();

        if (!content) {
            return false;
        }

        $.ajax({
            url: _s.API_URL + 'comment/',
            type: 'POST',
            data: JSON.stringify({'photo_id': data['id'], 'content': content}),
            contentType: 'application/json',
            dataType: 'json',
            success: function (comment_data, text, xhr) {
                $(_s.NOCMT).hide();
                $(_s.CMTAREA).val('');

                var data = {
                    id: comment_data.id, 
                    creator__name: comment_data.creator__name, 
                    create_time: moment(comment_data.create_time).format('YYYY-MM-DD HH:mm').toString(),
                    content: comment_data.content
                };

                setup_comment_unit(data);
                $(_s.CMTLIST).scrollTop($(_s.CMTLIST).height());
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        })
    })
}


function initial_control() {
    $(_s.TRACKS).find('ol').find('li').html(_s.LOCATION_TITLE);
    $(_s.TRACKS).hide();

    $(_s.LOCATION).show();
    $(_s.LOCATION).on('click', _s.CRUMBS, function() {
        $(_s.NODETREE).find('.jstree-clicked').each(function (index, node) {
            $(_s.NODETREE).jstree().deselect_node(node);
        });
        $(_s.NODETREE).jstree('select_node', $(this).attr('node_id'));
    });

    $(_s.T_LOCATION).on('click', _s.CRUMBS, function() {
        $(_s.TIMETREE).find('.jstree-clicked').each(function (index, node) {
            $(_s.TIMETREE).jstree().deselect_node(node);
        });
        $(_s.TIMETREE).jstree('select_node', $(this).attr('node_id'));
    });

    $(_s.I_LOCATION).on('click', _s.CRUMBS, function() {
        $(_s.IMPROVETREE).find('.jstree-clicked').each(function (index, node) {
            $(_s.IMPROVETREE).jstree().deselect_node(node);
        });
        $(_s.IMPROVETREE).jstree('select_node', $(this).attr('node_id'));
    });

    $(_s.PICKED_IMG).mousewheel(function(event, delta) {
        this.scrollLeft -= (delta * 50);
        event.preventDefault();
   });

    initial_upload_dialog();
    initial_toolbar_control();
    initial_subnode_unit_control();
    initial_thumbnail_unit_control();
    initial_edittool_control();
    initial_image_tools_control();
    layout.resizeAll();
}


function initial_upload_dialog() {
    $(_s.UPLOADER).plupload({
        runtimes: 'html5',
        unique_names: true,
        multipart_params: {},
        filters : [{extensions : 'jpg, jpeg'}],
        init: {
            BeforeUpload: function (uploader, file) {
                var dialog = $(_s.UPLOAD_DIALOG),
                    uri = dialog.attr('uri');

                uploader.settings.multipart_params.node = uri;
                uploader.settings.multipart_params.node_id = $.url(uri).segment(-1);
                uploader.settings.multipart_params.file_id = file.id;

                if (COMPRESS) {
                    if (file.size <= 2*1024*1024) {
                        $(_s.UPLOADER).plupload({resize: {crop: false}});
                    } else if (file.size <= 4*1024*1024) {
                        $(_s.UPLOADER).plupload({resize: {quality: 90}});
                    } else {
                        $(_s.UPLOADER).plupload({resize: {quality: 70}});
                    }
                }
                uploader.settings.url = _s.API_URL + 'photo/upload/' + $.url(uri).segment(-1) + '/?format=json';
            },
            FilesAdded: function (uploader ,files){
                $.each(files, function(i, file) {
                    if(file.size < (90*1024)){
                        alert(file.name + _s.UPLOAD_LOW_ALERT);
                        uploader.removeFile(file)
                    }
                    if(!COMPRESS && file.size > 4*1024*1024) {
                        alert(file.name + _s.UPLOAD_UP_ALERT);
                        uploader.removeFile(file)
                    }
                }
                )
            },
            UploadComplete: function (uploader, files) {
                var node = $(_s.NODETREE).jstree().get_node($('#' + $(_s.NODETREE).jstree('get_selected')));
                    parent_id = node.parent;

                node.data.images_count += files.length;
                node.data.total_count += files.length;
                update_node_grid(node);

                while (parent_id != '#') {
                    var parent_node = $(_s.NODETREE).jstree().get_node($('#' + parent_id));
                    parent_node.data.total_count += files.length;
                    update_node_grid(parent_node);
                    parent_id = $(_s.NODETREE).jstree().get_parent(parent_node);
                }

                setup_img_margin();
                reflash_time_tree();
                $(_s.UPLOAD_DIALOG).dialog('close');
            }
        },
        preinit: function (uploader) {
            uploader.bind('FileUploaded', function(uploader, file, res){
                var json = $.parseJSON(res.response)[0];
                if (json['__status__']) {
                    var page = $(_s.NODE_TAB + uploader.settings.multipart_params.node_id);
                    setup_thumbnail_unit(page, [json]);
                }
            });
        }
    });
}


function initial_toolbar_control() {
    /* 工具列按鈕設定 */
    $(_s.B_UPLOAD).button().click(upload_dialog);

    $(_s.B_ODERING).button({
        'text':true, 
        'icons':{secondary: 'ui-icon-triangle-1-s'},
    }).click(function() {
        return show_menu_option(this, _s.M_ODERING);
    });

    $(_s.B_SORTING).button({
        'text':true, 
        'icons':{secondary: 'ui-icon-triangle-1-s'},
    }).click(function() {
        return show_menu_option(this, _s.M_SORTING);
    });

    $(_s.B_DOWNLOAD).button({
        'text':true, 
        'icons':{secondary: 'ui-icon-triangle-1-s'},
    }).click(function() {
        return show_menu_option(this, _s.M_DOWNLOAD.supplant({doc: $(this).attr('doc')}));
    });

    $(_s.M_ODERING).menu().hide();
    $(_s.M_SORTING).menu().hide();
    $(_s.B_DOWNLOAD).each(function(index, value) {
        $(_s.M_DOWNLOAD.supplant({doc: $(value).attr('doc')})).menu().hide();
    });

    /* 顯示上傳介面 */
    function upload_dialog() {
        var node = $(_s.LOCATION).data('node');
        var dialog = $(_s.UPLOAD_DIALOG),
            uploader = $(_s.UPLOADER).plupload('getUploader');

        uploader.splice();

        var uri = _s.API_URL + 'node/' + node.id + '/',
            target = node.text;

        dialog.attr('uri', uri).dialog({
            draggable: false,
            resizable: false,
            title: _s.UPLOAD_TARGET + target.replace(/\//g, ' /'),
            width: 600
        });
        uploader.refresh();
    };

    /* 顯示進階選項 */
    function show_menu_option(obj, temp) {
        var menu = $(temp).show().position({
            my: 'left top',
            at: 'left bottom',
            of: obj
        });
        $(document).one('click', function() {
            menu.hide();
        });
        $('.ui-button-icon-secondary').click(function() {
            menu.hide();
        });
        $('.ui-button-text').click(function() {
            menu.hide();
        });
        return false;
    }

    /* 操作下載文件 */
    $(_s.DOC_OPT).click(document_download);

    function document_download() {
        var option = $(this).attr('option'),
            doc = $(this).attr('doc');

        switch (option) {
            case 'single':
                off_select();
                off_multi_select();

                if ($(_s.NODETREE).jstree().get_node($('#' + $(_s.LOCATION).data('node').id)).data.images_count < 1) {
                    apprise(_s.NO_IMG_INCLUDE, {'textOk': _s.OK});
                    break
                }
                var form = $(_s.DOWNLOAD_FORM),
                    section = form.find(_s.INPUTS),
                    doc_type = '<input name="doc_type" value="' + doc + '">',
                    node_id = '<input name="node_id" value="' + $(_s.LOCATION).data('node').id + '">';

                section.html('');
                section.append(doc_type);
                section.append(node_id);
                form.find(_s.DOWNLOAD).get(0).click();
                break
            case 'multi':
                off_select();
                $(_s.DO_GUIDE).show();
                $(_s.NODETREE).jstree().show_checkboxes();
                $(_s.DOWNLOAD_FORM).data('doc', doc);
                $(_s.DO_GUIDE).show();
                break
            case 'select':
                off_select();
                off_multi_select();
                resize_panel();

                $(_s.SELECT_PANEL).data('doc', doc);
                $(_s.SELECT_PANEL).data('page_unit', $(this).attr('page_unit'));
                $(_s.SELECT_PANEL).show();
                switch_format_display(true);
                break
        }
    }
    

    function switch_format_display(display) {
        if (display == undefined) {
            display = !$('.webui-popover').is(":visible");
        }

        if (display) {
            document_format();
            $(_s.VIEW_PHOTO_FORMAT_BUTTON).webuiPopover('show');
            $(_s.VIEW_PHOTO_FORMAT_BUTTON).find('strong').html('隱藏格式');
            mark_format_unit();
        } else {
            $(_s.VIEW_PHOTO_FORMAT_BUTTON).webuiPopover('hide');
            $(_s.VIEW_PHOTO_FORMAT_BUTTON).find('strong').html('顯示格式');
        }
    }


    function document_format() {
        var doc = $(_s.SELECT_PANEL).data('doc');
        if (doc) {
            var format = picked = $('#' + doc + '_format').tmpl();
            $(_s.VIEW_PHOTO_FORMAT_BUTTON).webuiPopover('destroy');
            $(_s.VIEW_PHOTO_FORMAT_BUTTON).webuiPopover({title: _s.PHOTO_FORMAT_TITLE, content: format, trigger:'manual', dismissible: false});
        }
    }

    /* 顯示照片格式的按鈕設定 */
    $(_s.VIEW_PHOTO_FORMAT_BUTTON).webuiPopover({title: _s.PHOTO_FORMAT_TITLE, content: '', trigger:'manual', dismissible: false});
    $(_s.VIEW_PHOTO_FORMAT_BUTTON).button({
        'text': true,
    }).click(function() {
        switch_format_display();
    });


    /* 取消照片選取的按鈕設定 */
    $(_s.CANCEL_PREVIEW_PHOTODOC_BUTTON).button({
        'text': true, 
    }).click(function() {
        /* 恢復瀏覽模式 */
        off_select();
    });

    /* 開始預覽的按鈕設定 */
    $(_s.START_PREVIEW_PHOTODOC_BUTTON).button({
        'text': true, 
    }).click(function() {
        start_preview();
    });

    /* 取消查驗點選取的按鈕設定 */
    $(_s.CANCEL_DOWNLOAD_PHOTODOC_BUTTON).button({
        'text': true, 
    }).click(function() {
        /* 恢復瀏覽模式 */
        off_multi_select();
    });

    /* 開始下載的按鈕設定 */
    $(_s.START_DOWNLOAD_PHOTODOC_BUTTON).button({
        'text': true, 
    }).click(function() {
        /* 產生表單下載並恢復瀏覽模式 */
        var form = $(_s.DOWNLOAD_FORM),
            doc = form.data('doc'),
            section = form.find('.inputs'),
            input = '',
            ic = 0;

        $.each($(_s.NODETREE).jstree('get_selected'), function(index, value) {
            ic += $(_s.NODETREE).jstree().get_node(value).data.images_count;
        });

        if (ic < 1) {
            apprise(_s.NO_IMG_INCLUDE, {'textOk': _s.OK});
        } else {
            section.html('');
            input = '<input name="doc_type" value="' + doc + '">';
            section.append(input);
            $(_s.NODETREE).find('.jstree-clicked').each(function (index, node) {
                var input = '<input name="node_id" value="' + $(node).closest('li').attr('node_id') + '">';
                section.append(input);
            });
            form.data('doc', '');
            form.find('.download').get(0).click();
            off_multi_select();
        }
    });

    /* 隱藏照片選取提示面板與操作紐 */
    function off_select() {
        $(_s.PICKED_IMG).html('');
        $(_s.PICKED_IMG).hide();
        $(_s.PICKIMG_NOTE).show();
        $(_s.SELECT_PANEL).hide();
        $(_s.EDIT_TOOLS).hide();
        $(_s.IMG_SELECTED).each(function() {
            $(this).remove();
        });
        switch_format_display(false);
    }

    /* 隱藏選取框與操作紐、取消所有選取只選取當下節點 */
    function off_multi_select() {
        $(_s.NODETREE).jstree().hide_checkboxes();
        $(_s.CTL_PANEL).hide();
        $(_s.DO_GUIDE).hide();
        $(_s.NODETREE).find('.jstree-clicked').each(function (index, node) {
            if ($(_s.LOCATION).data().node.id != $(this).closest('li').attr('node_id')) {
                $(_s.NODETREE).jstree().deselect_node(node);
            }
        });
        switch_format_display(false);
    }

    /* 顯示自選圖片文件預覽 */
    function start_preview() {
        var images = $(_s.PICKED_IMG).find(_s.PICK_TB),
            doc = $(_s.SELECT_PANEL).data('doc');

        if (images.length) {
            var photo_id = ''
            images.each(function (index, value) {
                photo_id += ($(value).data('id') + ',')
            })

            var tmp = $('<div align="center"><img src="/media/gallery/img/loader.gif"></div>');
            tmp.dialog({
                title: _s.CUSTOMIPT + $(_s.LOCATION).data('node').text,
                height: 800,
                width: 800,
                modal: true,
                buttons: {
                    '重選': function() {
                        $(this).dialog('close');
                    },
                    '下載': function() {
                        var form = $(_s.PREVIEW_FORM + '_' + doc);
                        var section = form.find(_s.INPUTS);

                        section.html('');
                        images.each(function (index, value) {
                            section.append('<input name="photo_id" value="' + $(value).data('id') + '">');
                        })
                        form.find(_s.DOWNLOAD).get(0).click();
                        off_select();
                        $(this).dialog('close');
                    },
                },
                close: function() {
                    $(this).dialog('destroy').remove();
                }
            });
            
            $.ajax({
                url: _s.API_URL + 'photo/preview_docx/?doc_type=' + doc + '&photo_id=' + photo_id,
                type: 'GET',
                contentType: 'application/json',
                dataType: 'json',
                success: function (json, text, xhr) {
                    tmp.html(json['html']);
                    tmp.find('img').load(function() {
                        $(this).css({'max-width': '100%', 'max-height': '100%'});
                    });
                },
                error: function(xhr, ajaxOptions, thrownError) {
                    REST_ERROR(xhr, ajaxOptions, thrownError);
                }
            });
        } else {
            alert(_s.SELECT_NONE_ALERT);
        }
    }

    /* 查驗點照片排序 */
    $(_s.ORDERING_OPT).click(sort_node_unit)

    function sort_node_unit() {
        $(_s.B_ODERING).find('strong').html($(this).text());
        setup_total_sorting();
    }

    /* 時間點照片排序 */
    $(_s.SORTING_OPT).click(sort_time_unit)

    function sort_time_unit() {
        $(_s.B_SORTING).find('strong').html($(this).text());
        setup_total_sorting();
    }

    setup_option();

    if (NODETEMPLATE) {
        initial_toolbar_template_control();
    }
}


function initial_subnode_unit_control() {
    $(_s.L_SHOW).on('click', _s.SUB_UNIT, function(e){
        $('#'+$(this).attr('node_id')).children('a').trigger('click');
    });
}


function mark_photo(unit) {
    var mask, selected;
    mask = unit.children(_s.IMG_MASK);
    selected = $('<div class="' + _s.IMG_SELECTED.replace('.', '') + '"></div>');
    selected.appendTo(mask);
}


function mark_format_unit() {
    $(_s.FORMAT_UNIT).removeClass(_s.FU_FILL.replace('.', ''));
    if ($(_s.PICK_TB).length) {
        var tail = $(_s.PICK_TB).length % $(_s.SELECT_PANEL).data('page_unit') || $(_s.SELECT_PANEL).data('page_unit');
        for(i=1;i<=tail;i++) {
            $(_s.FORMAT_UNIT+'_'+i).addClass(_s.FU_FILL.replace('.', ''))
        }
    }
}


function check_marked_photo(page) {
    if ($(_s.SELECT_PANEL).is(':visible')) {
        var picked_id = [];

        $(_s.PICKED_IMG).find(_s.PICK_TB).each(function(index, value) {
            picked_id.push($(value).data('id'));
        });

        page.find(_s.IMG_UNIT).each(function(index, value) {
            if ($.inArray($(value).data('id'), picked_id) > -1) {
                mark_photo($(value))
            }
        });
    }
}


function initial_thumbnail_unit_control() {
    /* 刪除圖片 */
    $(_s.L_SHOW).on('click', _s.IMG_DELETE, function(e){
        delete_file($(this).parents(_s.IMG_UNIT));
    });

    /* 點擊縮圖時的反應 */
    $(_s.L_SHOW).on('click', _s.IMG_TB, function(e){
        e.preventDefault;
        var unit = $(this).parents(_s.IMG_UNIT);
        if (!(e.ctrlKey || $(_s.SELECT_PANEL).is(':visible'))) {
            $(_s.SHOWBOX).data('obj', unit.find(_s.NO).html()).dialog('open');
            return false;
        }
        if ($(_s.MENU).find('.ui-state-active')[0].id == _s.BY_IMPROVE.replace('#', '') && !$(_s.SELECT_PANEL).is(':visible')) {
            apprise(_s.IMPROVE_PHOTO_EDIT_ALERT, {'textOk': _s.OK});
            return false;
        }

        if(e.ctrlKey){
            if(unit.hasClass('editable')){
                mark_photo(unit);
                $(_s.EDIT_TOOLS).fadeIn('fast');
            }
        }
        if ($(_s.SELECT_PANEL).is(':visible')) {
            if (!e.ctrlKey) {
                mark_photo(unit);
            }
            pickup_photo(unit);
        }
    });

    /* 點擊已選取縮圖時的反應 */
    $(_s.L_SHOW).on('click', _s.IMG_SELECTED, function(e){
        e.stopPropagation();
        var unit = $(this).parents(_s.IMG_UNIT);
        if(e.ctrlKey){
            $(this).remove();
            if ($(_s.IMG_SELECTED).length == 0){
                $(_s.EDIT_TOOLS).fadeOut('fast');
            }
        }
        if ($(_s.SELECT_PANEL).is(':visible')) {
            if (!e.ctrlKey) {
                $(this).remove();
            }
            unpick_photo(unit);
        }
    });


    function set_pick_num(picked, num) {        
        // var data = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" version="1.1"><text x="50%" y="50%" text-anchor="middle" alignment-baseline="middle" fill="#AA0000" font-size="50" font-weight="bold">' + num + '</text></svg>'
        // picked.find(_s.PICK_NO).css({'background-image': "url('"+data+"')"});

        // var image = new Image();
        // image.src = data;
        // var canvas = document.createElement('canvas');
        // canvas.width = image.width;
        // canvas.height = image.height;
        // var context = canvas.getContext('2d');
        // context.drawImage(image, 0, 0);

        picked.find(_s.PICK_NO).css({'background-image': 'url("/media/gallery/img/numbers/' + num + '.png")'});
    }


    function sort_pick_nums() {
        $(_s.PICK_TB).each(function(index, element) {
            set_pick_num($(element), index%$(_s.SELECT_PANEL).data('page_unit') + 1);
        });
    }

    function pickup_photo(unit) {
        var picked = $(_s.DPI_TMP).tmpl().css({'background-image': 'url('+unit.data('thumb_url')+')'});
        picked.data('id', unit.data('id'));
        set_pick_num(picked, $(_s.PICK_TB).length%$(_s.SELECT_PANEL).data('page_unit') + 1)
        $(_s.PICKED_IMG).append(picked);

        var tip = $('<div class="ui-tooltip-content ui-widget-content"><img width="400" src=' + unit.data('thumb_url') + '></div>'),
            cancel_pick = $('<div class="cancel_pick"><strong>取消選取</strong></div>');

        cancel_pick.data('id', unit.data('id'));
        cancel_pick.button().click(function() {
            var obj = $(this);
            $(_s.IMG_SELECTED).each(function(index, value) {
                $('.qtip').hide();
                if ($(value).parents(_s.IMG_UNIT).data('id') == obj.data('id')) {
                    $(value).click();
                    return true;
                }
                picked.remove();
            });
        });

        tip.append(cancel_pick);
        picked.qtip({
            content: tip,
            show: {
                event: 'mousedown',
                solo: true,

            },
            hide: {
                event: 'unfocus'
            },
            style: {
                classes: 'picked_tip',
                width: 420,
                height: 450,
                tip: {
                  corner: 'bottomMiddle'
                }
            },
            position: {
                my: 'bottom center',
                at: 'top center',
                target: picked,
                adjust: {
                    y: -20,
                    resize: true
                }
            },
        });

        $(_s.PICKIMG_NOTE).hide();
        $(_s.PICKED_IMG).show();
        $(_s.PICKED_IMG).sortable('refresh');
        mark_format_unit();
    }

    function unpick_photo(unit) {
        $(_s.PICKED_IMG).find(_s.PICK_TB).each(function(index, value) {
            if (unit.data('id') == $(value).data('id')) {
                $(value).remove();
            }
        });

        if ($(_s.PICKED_IMG).find(_s.PICK_TB).length < 1) {
            $(_s.PICKED_IMG).hide();
            $(_s.PICKIMG_NOTE).show();
        } else {
            sort_pick_nums();
        }
        mark_format_unit();
    }

    $(_s.PICKED_IMG).sortable({
        axis: "x",
        cursor: "move",
        items: _s.PICK_TB,
        stop: function(event, ui) {
            $('.qtip').hide();
            sort_pick_nums();
        }
    });


    /* 點擊已選取縮圖時的反應 */
    $(_s.L_SHOW).on('mousedown', _s.IMG_SELECTED, function(e){
        var files = $(_s.IMG_SELECTED).parents(_s.IMG_UNIT),
            current_tab = $(_s.MENU).find('.ui-state-active')[0],
            drag_div;

        if (current_tab.id == _s.BY_NODE.replace('#', '')) {
            drag_div = $('<div class="' + _s.DRAG_DIV.replace('.', '') + '"><span class="glyphicon glyphicon-hand-left"></span></div>');
        } else {
            drag_div = $('<div class="' + _s.DRAG_DIV.replace('.', '') + '"><span class="glyphicon glyphicon-remove"></span></div>');
        }
        return $.vakata.dnd.start(e, {'jstree' : true, 'obj' : files, 'nodes' : [{ id : false, text: $(this).text() }], }, $('<div></div>').append(drag_div));
    });

    /* 開始拖曳將已選取縮圖半透明處理 */
    $(_s.L_SHOW).on('dnd_start.vakata', function(e, data){
        $(_s.IMG_SELECTED).parents(_s.IMG_UNIT).css('opacity', '0.5');
    });

    /* 拖曳已選取縮圖時的反應 */
    $(document).on('dnd_stop.vakata', function(e, data){
        if ($(data.element).hasClass(_s.IMG_SELECTED.replace('.', ''))) {
            var target = $(data.event.target);
            var target_id = target.parents('li').attr('id');
            var id_array = [];

            $(_s.IMG_SELECTED).parents(_s.IMG_UNIT).css('opacity', '1');
            if (target_id && target_id.indexOf('take_') < 0) {
                var files = data.data.obj,
                    move_num = files.length,
                    no_permission = [],
                    move_count = 0;

                files.each(function(index, element) {
                    var file = $(element);
                    if (!file.find(_s.IMG_DELETE).length) {
                        no_permission.push(file.find(_s.NO).html());
                    }
                })
                move_num -= no_permission.length;
                if (no_permission.length==files.length) {
                    alert(_s.MULTI_NON_MOVE_ALERT.supplant({total: files.length}));
                    return false;
                }

                files.each(function(index, element) {
                    var file = $(element);
                    id_array.push(file.data('id'));
                    if (file.find(_s.IMG_DELETE).length) {
                        $.ajax({
                            url: _s.API_URL + 'photo/' + file.data('id') + '/',
                            type: 'PUT',
                            contentType: 'application/json',
                            dataType: 'json',
                            data:JSON.stringify({'node_id': target_id}),
                            success: function () {
                                var target_page = $(_s.NODE_TAB + target_id);
                                if (target_page.length > 0) {
                                    target_page.append(file);
                                    setup_page_sorting(target_page);
                                } else {
                                    file.remove();
                                }

                                file.find(_s.IMG_SELECTED).remove();
                                setup_page_sorting($(_s.PAGES).filter(':visible'));

                                move_count += 1
                                if (move_count == move_num) {
                                    if (no_permission.length) {
                                        alert(_s.MULTI_PART_MOVE_ALERT.supplant({total: files.length, part: no_permission.length, execute: move_num, target: target.context.innerText}));    
                                    } else {
                                        $(_s.EDIT_TOOLS).fadeOut('fast');
                                    }
                                }
                            },
                        });
                    }
                });

                $(_s.IMG_UNIT).each(function(index, value) {
                    if (id_array.indexOf($(value).data('id')) > -1) {
                        $(value).data('node_name', $(_s.NODETREE).jstree().get_node(target_id).text);
                    }
                });

                var node = $(_s.NODETREE).jstree().get_node($('#' + $(_s.NODETREE).jstree('get_selected'))),
                    parent_id = node.parent;

                node.data.images_count -= move_num;
                node.data.total_count -= move_num;
                update_node_grid(node);

                while (parent_id != '#') {
                    var parent_node = $(_s.NODETREE).jstree().get_node($('#' + parent_id));
                    parent_node.data.total_count -= move_num;
                    update_node_grid(parent_node);
                    parent_id = $(_s.NODETREE).jstree().get_parent(parent_node);
                }

                var new_node = $(_s.NODETREE).jstree().get_node($('#' + target_id)),
                    parent_id = new_node.parent;

                new_node.data.images_count += move_num;
                new_node.data.total_count += move_num;
                update_node_grid(new_node);

                while (parent_id != '#') {
                    var parent_node = $(_s.NODETREE).jstree().get_node($('#' + parent_id));
                    parent_node.data.total_count += move_num;
                    update_node_grid(parent_node);
                    parent_id = $(_s.NODETREE).jstree().get_parent(parent_node);
                }
            }
        }
    });
}


function initial_edittool_control() {
    var note_dialog, date_dialog;
    var today = new Date();

    $(_s.EDIT_DEL).click(function() {
        delete_file($(_s.IMG_SELECTED).parents(_s.IMG_UNIT));
    });

    $(_s.EDIT_NOTE).click(function() {
        note_dialog.dialog('open');
    });

    $(_s.EDIT_DATE).click(function() {
        date_dialog.dialog('open');
    });

    $(_s.EDIT_PUBLIC).click(function() {
        public_dialog.dialog('open');
    });

    $(_s.EDIT_CANCEL).click(function() {
        off_select();
    });

    $(_s.EDIT_DATA_INPUT).datetimepicker({
        language: 'zh_tw',
        format: 'yyyy-mm-dd',
        weekStart: 1,
        todayBtn:  1,
        autoclose: 1,
        todayHighlight: 1,
        startView: 2,
        minView: 2,
        forceParse: 0
    });

    $(_s.EDIT_DATA_INPUT).datetimepicker('setEndDate', '{year}-{month}-{day}'.supplant({year: today.getFullYear(), month: today.getMonth()+1, day: today.getDate()}));

    $(_s.EDIT_DATA_INPUT).on('changeDate', function(ev) {
        $(_s.EDIT_DATA_INPUT).parents('div').find('input').attr('value', $(_s.EDIT_DATA_INPUT).data('date'));
    });

    /* 批次修改說明對話框 */
    note_dialog = $(_s.EDIT_NOTE_DIALOG).dialog({
        height: 500,
        width: 500,
        modal: true,
        autoOpen: false,
        resizable: false,
        open: function( event, ui ) {
            $(_s.EDIT_NOTE_DIALOG).find(_s.EDIT_TIP).text(_s.EDIT_NOTE_TIP.supplant({total: $(_s.IMG_SELECTED).length}));
        },
        close: function() {
            $(_s.EDIT_NOTE_DIALOG).find('form')[0].reset();
        },
        buttons: {
            '確定': function() {
                var files = $(_s.IMG_SELECTED).parents(_s.IMG_UNIT),
                    note = $(_s.EDIT_NOTE_TEXT).val(),
                    counter = 0,
                    id_array = [];
                
                if (!confirm(_s.EDIT_ALERT.supplant({total: files.length}))) {
                    return false;
                }

                files.each(function(index, file) {
                    var file = $(file),
                        id = file.data().id;
                    id_array.push(id)

                    $.ajax({
                        url: _s.API_URL + 'photo/' + id + '/',
                        type: 'PUT',
                        data: JSON.stringify({'note': note}),
                        contentType: 'application/json',
                        dataType: 'json',
                        success: function (json, text, xhr) {
                            counter += 1;
                            file.data('note', note);
                            if(counter == files.length){
                                off_select();
                                note_dialog.dialog('close');
                            }
                        }
                    }); 
                });

                $(_s.IMG_UNIT).each(function(index, value) {
                    if (id_array.indexOf($(value).data('id')) > -1) {
                        $(value).data('note', note);
                    }
                });
            },
            '取消': function() {
                note_dialog.dialog('close');
            }
        }
    });
    
    /* 批次修改拍攝日期對話框 */
    date_dialog = $(_s.EDIT_DATE_DIALOG).dialog({
        height: 500,
        width: 500,
        modal: true,
        autoOpen: false,
        resizable: false,
        open: function( event, ui ) {
            $(_s.EDIT_DATE_DIALOG).find(_s.EDIT_TIP).text(_s.EDIT_DATE_TIP.supplant({total: $(_s.IMG_SELECTED).length}));
        },
        close: function() {
            $(_s.EDIT_DATE_DIALOG).find('form').find('input').attr('value', '');
            $(_s.EDIT_DATA_INPUT).datetimepicker('update', '');
        },
        buttons: {
            '確定': function() {
                var files = $(_s.IMG_SELECTED).parents(_s.IMG_UNIT),
                    date = $(_s.EDIT_DATE_DIALOG).find('form').find('input').val();
                    counter = 0,
                    id_array = [];
                
                if (date == '') {
                    alert(_s.EMP_DATE_ALERT);
                    return false;
                }

                if (!confirm(_s.EDIT_ALERT.supplant({total: files.length}))) {
                    return false;
                }

                if ($(_s.MENU).find('.ui-state-active')[0].id == _s.BY_TIME.replace('#', '') && $(_s.TIMETREE).find('.jstree-clicked').length > 0) {
                    refresh_time = $(_s.TIMETREE).find('.jstree-clicked').parent('li').attr('id');
                    target_time = date;
                } else {
                    refresh_time = false;
                }

                files.each(function(index, file) {
                    var file = $(file),
                        id = file.data().id;
                    id_array.push(id);

                    $.ajax({
                        url: _s.API_URL + 'photo/' + id + '/',
                        type: 'PUT',
                        data: JSON.stringify({'take_date': date}),
                        contentType: 'application/json',
                        dataType: 'json',
                        success: function (json, text, xhr) {
                            counter += 1;
                            file.data('time', date);
                            file.find(_s.IMG_TAKE_TIME).html(date);
                            if(counter == files.length){
                                off_select();
                                reflash_time_tree();
                                date_dialog.dialog('close');
                            }
                        }
                    }); 
                });

                $(_s.IMG_UNIT).each(function(index, value) {
                    if (id_array.indexOf($(value).data('id')) > -1) {
                        $(value).data('time', date);
                    }
                });
            },
            '取消': function() {
                date_dialog.dialog('close');
            }
        }
    });
    
    /* 批次修改公開審核對話框 */
    public_dialog = $(_s.EDIT_PUBLIC_DIALOG).dialog({
        height: 300,
        width: 500,
        modal: true,
        autoOpen: false,
        resizable: false,
        open: function( event, ui ) {
            $(_s.EDIT_PUBLIC_DIALOG).find(_s.EDIT_TIP).text(_s.EDIT_PUBLIC_TIP.supplant({total: $(_s.IMG_SELECTED).length}));
        },
        close: function() {
            $(_s.EDIT_PUBLIC_DIALOG).find('form').find('input').prop('checked', false);
        },
        buttons: {
            '確定': function() {
                var files = $(_s.IMG_SELECTED).parents(_s.IMG_UNIT),
                    is_public = $(_s.EDIT_PUBLIC_DIALOG).find('form').find('input').is(':checked');
                    counter = 0,
                    id_array = [];

                if (!confirm(_s.PUBLIC_ALERT.supplant({total: files.length, state: (is_public) ? '公開' : '非公開'}))) {
                    return false;
                }

                files.each(function(index, file) {
                    var file = $(file),
                        id = file.data().id;
                    id_array.push(id);
                    $.ajax({
                        url: _s.API_URL + 'photo/' + id + '/',
                        type: 'PUT',
                        data: JSON.stringify({'is_public': is_public}),
                        contentType: 'application/json',
                        dataType: 'json',
                        success: function (json, text, xhr) {
                            counter += 1;
                            file.data('is_public', is_public);
                            if(counter == files.length){
                                off_select();
                                public_dialog.dialog('close');
                            }
                        }
                    }); 
                });

                $(_s.IMG_UNIT).each(function(index, value) {
                    if (id_array.indexOf($(value).data('id')) > -1) {
                        $(value).data('is_public', is_public);
                    }
                });
            },
            '取消': function() {
                public_dialog.dialog('close');
            }
        }
    });
    
    /* 取消照片選取與操作紐 */
    function off_select() {
        $(_s.EDIT_TOOLS).hide();
        $(_s.IMG_SELECTED).each(function() {
            $(this).remove();
        })
    }
}


function initial_image_tools_control() {
    $(_s.IMGPN).click(reset_img);
    $(_s.TURN_CCW).click(turn_img);
    $(_s.TURN_CW).click(turn_img);
    $(_s.TURN_SAVE).click(save_rotation);
    $(_s.GRID_ONOFF).click(switch_grid);

    function reset_img() {
        $(_s.DOCK).data('angle', 0);
        $(_s.DOCK).rotate({animateTo: 0});
        $(_s.GUT).rotate({animateTo: 0});
        panobj.panzoom('reset');
    }

    function turn_img() {
        var angle = $(_s.DOCK).data('angle') | 0;
        angle += parseInt($(this).attr('value'));

        $(_s.DOCK).data('angle', angle);
        $(_s.DOCK).rotate({animateTo: angle});
        $(_s.GUT).rotate({animateTo: angle * -1});
    }

    function save_rotation() {

        function getRotationDegrees(obj) {
            var matrix = obj.css('-webkit-transform') || obj.css('-moz-transform') || obj.css('-ms-transform') || obj.css('-o-transform') || obj.css('transform');
            if(matrix !== 'none') {
                var values = matrix.split('(')[1].split(')')[0].split(',');
                var a = values[0];
                var b = values[1];
                var angle = Math.round(Math.atan2(b, a) * (180/Math.PI));
            } else {
                var angle = 0;
            }
            return (angle < 0) ? angle + 360 : angle;
        }

        $(_s.PAN).css({'visibility': 'hidden'});
        $(_s.LOADING).css({'visibility': 'visible'});

        setTimeout(function(deg) {
            var degree = getRotationDegrees($(_s.DOCK)),
                index = parseInt($(_s.IMAGE).data('no')) - 1,
                current = $(_s.PAGES).filter(':visible'),
                images = current.find(_s.IMG_UNIT),
                data = $(images[index]).data();

            $.ajax({
                url: _s.API_URL + 'photo/' + data['id'] + '/',
                type: 'PUT',
                data: JSON.stringify({'degree': degree}),
                contentType: 'application/json',
                dataType: 'json',
                success: function (json, text, xhr) {
                    $(_s.IMG_UNIT).each(function(index, value) {
                        if ($(value).data('id') == data['id']) {
                            $(value).data('sized_url', json['sized_url']);
                            $(value).data('thumb_url', json['thumb_url']);
                            $(value).find(_s.IMG_TB).attr('data-original', json['thumb_url']);
                            $(value).find(_s.IMG_TB).attr('src', json['thumb_url']);
                        }
                    });

                    if ($(_s.L_PHOTO).is(":visible") && index == (parseInt($(_s.IMAGE).data('no')) - 1)) {
                        setup_showbox(index+1);
                    }
                },
                error: function(xhr, ajaxOptions, thrownError) {
                    REST_ERROR(xhr, ajaxOptions, thrownError);
                }
            });
        }, 800);
    }

    function switch_grid() {
        var grid = $(_s.GRID);

        if(grid.hasClass('hidden')) {
            grid.removeClass('hidden');
            $(_s.GRID_ON).hide();
            $(_s.GRID_OFF).show();
        } else {
            grid.addClass('hidden');
            $(_s.GRID_ON).show();
            $(_s.GRID_OFF).hide();
        }
    }
}


function initial_image_loader() {
    $(_s.IMAGE).on('load', function() {
        var container = $(_s.L_PHOTO),
            loading = $(_s.LOADING),
            panlayer = $(_s.PAN),
            dock = $(_s.DOCK),
            image = $(_s.IMAGE);

        var img_w = image.width(),
            img_h = image.height(),
            box_w = container.width() * 0.9,
            box_h = container.height() * 0.9;

        image.data('org_w', this.width);
        image.data('org_h', this.height);

        if ((img_w > box_w && img_h > box_h) || (img_w < box_w && img_h < box_h)) {
            var w_ratio = img_w / box_w,
                h_ratio = img_h / box_h;

            if (w_ratio > h_ratio) {
                image.css({'width': box_w});
            } else {
                image.css({'height': box_h});
            }

        } else if (img_w > box_w) {
            image.css({'width': box_w});
        } else if (img_h > box_h) {
            image.css({'height': box_h});
        }

        var set_w = image.width(),
            set_h = image.height(),
            act_w = container.width(),
            act_h = container.height();

        loading.css({'visibility': 'hidden'});
        dock.css({'width': set_w, 'height': set_h, 'left': act_w + (act_w-set_w)/2, 'top': act_h + (act_h-set_h)/2});
        panlayer.css({'visibility': 'visible'});
        panlayer.panzoom('reset');
        setup_grid(set_w, set_h);
    }).each(function() {
        if(this.complete){
            $(this).load();
        }
    });
    $(_s.NEXT).click(switch_image);
}


function initial_improvetree() {
    $(_s.IMPROVETREE).jstree({
        'plugins': [
            'grid'
        ],
        'core' : {
            'animation': 0,
            'check_callback': true,
            'themes': {
                'name': 'proton',
                'responsive': true
            },
            'data': {
                'url' : function (node){
                    return node.id === '#' ? _s.API_URL + 'node/root_improve' : _s.API_URL + 'node/sub_node/' + node.id;
                },
                'data' : function (node){
                    return node.id === '#' ? {'case': CASE_ID} : {}
                },
                'success': function (objects, status, response) {
                    var obj = objects[0] || objects,
                        pid = obj.parent;
                    
                    if (pid && pid != '#') {
                        var target = $(_s.NODE_TAB + obj.parent);
                        if (target.find(_s.SUB_UNIT).length < 1) {
                            setup_subunit(target, objects);
                        }
                    }
                }
            }
        },
        'grid': {
            columns: [
                {width: '100%'},
                {
                    value: function(node_data) {
                        return('{child}/{total}'.supplant({child: node_data.images_count, total: node_data.total_count}))
                    },
                    cellClass: _s.SUB_COUNT.replace('.', ''),
                    width: 100
                }
            ]
        }
    })
    .delegate('.jstree-closed>a', 'click.jstree', function(event){
        $.jstree.reference(this).open_node(this, false, false);
    })
    .on('ready.jstree', function(event) {
        $(_s.IMAGE_COUNT).qtip({
            content: _s.IMAGE_COUNT_TIP
        });
    })
    .on('changed.jstree', check_improve)
    .on('open_node.jstree', open_node)
    .on('select_node.jstree', load_improve);

    /* 只允許單選 */
    function check_improve(event, data) {
        if (data.selected.length > 1) {
            $(_s.IMPROVETREE).find('.jstree-clicked').each(function (index, node) {
                if (data.node.id != $(node).closest('li').attr('id')) {
                    $(_s.IMPROVETREE).jstree().deselect_node(node, event);
                }
            });
        }
    }

    /* 設定提示 */
    function open_node(event, data) {
        $(_s.SUB_COUNT).qtip({
            content: _s.IMP_COUNT_TIP
        });
    }

    /* 載入缺失改善 */
    function load_improve(event, data) {
        if (data.node != $(_s.I_LOCATION).data('node')) {
            update_location(data.node);

            var page = $(_s.NODE_TAB + data.node.id);
            $(_s.PAGES).hide();
            $(_s.EDIT_TOOLS).hide();
            $(_s.IMG_SELECTED).each(function() {
                $(this).remove();
            });

            if (page.length > 0) {
                page.show();
                setup_lazyload();
                check_marked_photo(page);
            } else {
                $(_s.P_LOADING).css({'opacity': 1});
                page = init_page(_s.NODE_TAB, data.node.id);
                load_image(page, data.node);
            }
        }
    };

    /* 更新目前位置 */
    function update_location(node) {
        var id = node.id,
            name = node.text,
            parent_id = node.parent,
            parents = [];

        var ol = $('<ol class="breadcrumb"></ol>'),
            paths = ['<li><a class="select_node active" node_id="' + id + '" href="#">' + name + '</li>'];

        while (parent_id != '#') {
            var parent_node = $(_s.IMPROVETREE).jstree().get_node($('#' + parent_id));
            paths.unshift('<li><a class="select_node" node_id="' + parent_id + '" href="#">' + parent_node.text + '</li>');
            parent_id = $(_s.IMPROVETREE).jstree().get_parent(parent_node);
        }

        paths.unshift('<li>' + _s.LOCATION_TITLE + '</li>');
        ol.html(paths.join(''));
        $(_s.I_LOCATION).empty();
        $(_s.I_LOCATION).append(ol);
        $(_s.I_LOCATION).data('node', node);
    }

    /* 載入頁面 */
    function load_image(page, node, url) {
        url = url || _s.API_URL + 'photo/?format=json&node=' + node.id;
        $.ajax({
            url: url,
            type: 'GET',
            success: function (json, text, xhr) {
                var meta = json['meta'];
                var objs = json['objects'];
                $(_s.P_LOADING).css({'opacity': 0});

                setup_page(page, objs, node.id);
                if (meta['next']) {
                    load_image(page, node, meta['next']);
                } else {
                    setup_page_element(page);
                    setup_page_sorting(page);
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    }
}


function initial_timetree() {
    $(_s.TIMETREE).jstree({
        'plugins': [
            'grid'
        ],
        'core' : {
            'animation': 0,
            'check_callback': true,
            'themes': {
                'name': 'proton',
                'responsive': true
            },
            'data': {
                'url': _s.API_URL + 'node/timeline',
                'data': {
                    'case': CASE_ID
                }
            }
        },
        'grid': {
            columns: [
                {width: '100%'},
                {
                    value: function(node_data) {
                        return(node_data.count)
                    },
                    cellClass: _s.IMAGE_COUNT.replace('.', ''),
                    width: 60
                }
            ]
        }
    })
    .delegate('.jstree-closed>a', 'click.jstree', function(event){
        $.jstree.reference(this).open_node(this, false, false);
    })
    .on('ready.jstree', function(event) {
        $(_s.IMAGE_COUNT).qtip({
            content: _s.IMAGE_COUNT_TIP
        });
    })
    .on('refresh.jstree', function(event) {
        $(_s.IMAGE_COUNT).qtip({
            content: _s.IMAGE_COUNT_TIP
        });
        if (refresh_time && $(_s.MENU).find('.ui-state-active')[0].id == _s.BY_TIME.replace('#', '')) {
            if ($('#'+refresh_time).length > 0) {
                $('#'+refresh_time).children('a').trigger('click');
            } else if (target_time) {
                $('#take_'+target_time).children('a').trigger('click');
            }
            refresh_time = false;
            target_time = false;
        }
    })
    .on('changed.jstree', check_node)
    .on('select_node.jstree', load_time);


    /* 只允許單選 */
    function check_node(event, data) {
        if (data.selected.length > 1) {
            $(_s.TIMETREE).find('.jstree-clicked').each(function (index, node) {
                if (data.node.id != $(node).closest('li').attr('id')) {
                    $(_s.TIMETREE).jstree().deselect_node(node, event);
                }
            });
        }
    }

    /* 載入時間點 */
    function load_time(event, data) {
        if (data.node != $(_s.T_LOCATION).data('node')) {
            update_location(data.node);

            var page = $(_s.TIME_TAB + data.node.id);
            $(_s.PAGES).hide();
            $(_s.EDIT_TOOLS).hide();
            $(_s.IMG_SELECTED).each(function() {
                $(this).remove();
            });

            if (page.length > 0) {
                page.show();
                setup_lazyload();
                check_marked_photo(page);
            } else {
                page = init_page(_s.TIME_TAB, data.node.id);
                $(_s.P_LOADING).css({'opacity': 1});
                load_image(page, data.node);
            }
        }
    };

    /* 更新目前位置 */
    function update_location(node) {
        var id = node.id,
            name = node.text,
            parent_id = node.parent,
            parents = [];

        var ol = $('<ol class="breadcrumb"></ol>'),
            paths = ['<li><a class="select_node active" node_id="' + id + '" href="#">' + name + '</li>'];

        while (parent_id != '#') {
            var parent_node = $(_s.TIMETREE).jstree().get_node($('#' + parent_id));
            paths.unshift('<li><a class="select_node" node_id="' + parent_id + '" href="#">' + parent_node.text + '</li>');
            parent_id = $(_s.TIMETREE).jstree().get_parent(parent_node);
        }

        paths.unshift('<li>' + _s.LOCATION_TITLE + '</li>');
        ol.html(paths.join(''));
        $(_s.T_LOCATION).empty();
        $(_s.T_LOCATION).append(ol);
        $(_s.T_LOCATION).data('node', node);
    }

    /* 載入頁面 */
    function load_image(page, node, url) {
        url = url || _s.API_URL + 'photo/?format=json&node__case=' + CASE_ID + '&ordering=time&take_date=' + node.id.replace('take_', '');
        $.ajax({
            url: url,
            type: 'GET',
            success: function (json, text, xhr) {
                var meta = json['meta'];
                var objs = json['objects'];
                $(_s.P_LOADING).css({'opacity': 0});

                setup_page(page, objs, node.id);
                if (meta['next']) {
                    load_image(page, node, meta['next']);
                } else {
                    setup_page_element(page);
                    setup_page_sorting(page);
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    }
}


function initial_nodetree() {
    $(_s.NODETREE).jstree({
        'plugins': [
            'dnd', 'contextmenu', 'state', 'grid', 'checkbox'
        ],
        'core': {
            'animation': 0,
            'multiple ': false,
            'check_callback': function (operation, node, node_parent, node_position, more) {
                if (!node && more && more.dnd && more.pos !== 'i') {
                    return false;
                }
                return true;
            },
            'themes': {
                'name': 'proton',
                'responsive': true
            },
            'data': {
                'url' : function (node){
                    return node.id === '#' ? _s.API_URL + 'node/root_node' : _s.API_URL + 'node/sub_node/' + node.id;
                },
                'data' : function (node){
                    return node.id === '#' ? {'case': CASE_ID} : {}
                },
                'success': function (objects, status, response) {
                    var obj = objects[0] || objects,
                        pid = obj.parent;

                    if (pid && pid != '#') {
                        var target = $(_s.NODE_TAB + obj.parent);

                        if (target.find(_s.SUB_UNIT).length < 1) {
                            setup_subunit(target, objects);
                        }
                    }
                }
            }
        },
        'dnd': {
            'is_draggable': function(node) {
                if (node[0].data.default) {
                    return false;
                }
                return true;
            }
        },
        'contextmenu': {
            'items': show_contextmenu
        },
        'state': {
            'key': _s.NODETREE_KEY
        },
        'grid': {
            columns: [
                {width: '100%'},
                {
                    value: function(node_data) {
                        return('{child}/{total}'.supplant({child: node_data.images_count, total: node_data.total_count}))
                    },
                    cellClass: _s.SUB_COUNT.replace('.', ''),
                    width: 100
                }
            ]
        },
        'checkbox': {
            'two_state' : true,
            'three_state': false,
            'visible': false
        }
    })
    // .delegate('.jstree-open>a', 'click.jstree', function(event){
    //     $.jstree.reference(this).close_node(this, false, false);
    // })
    .delegate('.jstree-closed>a', 'click.jstree', function(event){
        $.jstree.reference(this).open_node(this, false, false);
    })
    .on('ready.jstree', function(event) {
        if (!$.vakata.storage.get(_s.NODETREE_KEY)) {
            $(_s.NODETREE).find('.jstree-last').last().children('a').trigger('click');
        }
        $(_s.SUB_COUNT).qtip({
            content: _s.SUB_COUNT_TIP
        });
    })
    .on('state_ready.jstree', function(event) {
        if (!$(_s.NODETREE).jstree().get_node($('#' + $(_s.NODETREE).jstree('get_selected')[0]))) {
            $(_s.NODETREE).find('.jstree-last').last().children('a').trigger('click');
        }
    })
    .on('changed.jstree', check_node)
    .on('open_node.jstree', open_node)
    .on('select_node.jstree', load_node)
    .on('rename_node.jstree', rename_node)
    .on('delete_node.jstree', delete_node)
    .on('move_node.jstree', move_node);


    function show_contextmenu(node) {
        var tree = $(_s.NODETREE).jstree();
        var disable, create, copy, paste, outfall, insert, rename, remove;

        disable = {
            label: _s.NT_FBEDIT,
            action: function(obj) {
                return false;
            }
        }

        lockedit = {
            label: _s.NT_NAEDIT,
            action: function(obj) {
                return false;
            }
        }

        create = {
            label: _s.NT_NEWNODE,
            action: function (obj) {
                var parent_id = node.id;

                $.ajax({
                    url: _s.API_URL + 'node/',
                    type: 'POST',
                    data: JSON.stringify({'parent_id': parent_id}),
                    contentType: 'application/json',
                    dataType: 'json',
                    success: function (json, text, xhr) {
                        node = tree.create_node(node, {'id': json.id, 'text': json.name, 'data': {'images_count': 0, 'total_count': 0}, 'li_attr': {'node_id': json.id}}, 'last');
                        tree.edit(node);

                        var page = $(_s.NODE_TAB + parent_id);
                        var sub_unit = $(_s.SUB_TMP).tmpl({node_id: json.id, text: json.name});
                        if (page.find(_s.SUB_UNIT).length > 0) {
                            sub_unit.insertAfter(page.find(_s.SUB_UNIT).last());
                        } else {
                            page.prepend(sub_unit);
                        }
                        setup_img_margin();
                    },
                    error: function(xhr, ajaxOptions, thrownError) {
                        REST_ERROR(xhr, ajaxOptions, thrownError);
                    }
                });
            },
        }

        if (NODETEMPLATE) {
            insert = {
                label: _s.NT_INSERT,
                action: function (obj) {
                    open_insert_dialog(node.id, node.text);
                },
            }
        } else {
            insert = false;
        }

        if (!node.data.default){
            if (COPYNODE) {
                copy = {
                    label: _s.NT_COPY,
                    action: function (obj) {
                        copy_node = node.id;
                    },
                }
            } else {
                copy = false;
            }

            if (NODETEMPLATE) {
                outfall = {
                    label: _s.NT_EXPORT,
                    action: function (obj) {
                        off_select();
                        $(_s.NODETREE).jstree().show_checkboxes();
                        $(_s.DEFAULT_NODE_CLASS).prev(_s.JSTREE_CHECK_CLASS).hide();
                        $(_s.EO_GUILD).show();

                        var node = $(_s.NODETREE).jstree().get_node($('#' + $(_s.NODETREE).jstree('get_selected')));
                        $.each($(_s.NODETREE).jstree().get_node($('#' + $(_s.NODETREE).jstree('get_selected'))).children_d, function(index, value) {
                            $(_s.NODETREE).jstree('select_node', '#' + value);
                        });
                    },
                }

                function off_select() {
                    $(_s.SELECT_PANEL).hide();
                    $(_s.EDIT_TOOLS).hide();
                    $(_s.IMG_SELECTED).each(function() {
                        $(this).remove();
                    })
                }
            } else {
                outfall = false;
            }
            
            rename = {
                label: _s.NT_RENAME,
                action: function (obj) {
                    tree.edit(node);
                },
            }
            
            remove = {
                label: _s.NT_REMOVE,
                action: function (obj) {
                    tree.delete_node(node);
                },
            }
        } else {
            rename = false;
            remove = false;
        }

        if (copy_node) {
            paste = {
                label: _s.NT_PASTE,
                action: function (obj) {
                    var copyed = []
                    clone_node(node.id, copy_node);

                    function clone_node(copy_to, copy_from) {
                        $.ajax({
                            url: _s.API_URL + 'node/',
                            type: 'POST',
                            data: JSON.stringify({'parent_id': copy_to, 'copy': copy_from}),
                            contentType: 'application/json',
                            dataType: 'json',
                            success: function (json, text, xhr) {
                                copyed.push(json.id)
                                tree.create_node(copy_to, {'id': json.id, 'text': json.name, 'data': {'images_count': 0, 'total_count': 0}, 'li_attr': {'node_id': json.id}}, 'last');
                                
                                var page = $(_s.NODE_TAB + copy_to);
                                var sub_unit = $(_s.SUB_TMP).tmpl({node_id: json.id, text: json.name});
                                if (page.find(_s.SUB_UNIT).length > 0) {
                                    sub_unit.insertAfter(page.find(_s.SUB_UNIT).last());
                                } else {
                                    page.prepend(sub_unit);
                                }
                                setup_img_margin();

                                $.each(json['copy'], function(index, value) {
                                    if ($.inArray(value, copyed) < 0) {
                                        clone_node(json.id, value);
                                    }
                                })
                            },
                            error: function(xhr, ajaxOptions, thrownError) {
                                REST_ERROR(xhr, ajaxOptions, thrownError);
                            }
                        });
                    }
                },
            }
        } else {
            paste = false;
        }

        if ($(_s.PERMISSION).attr('permissions').split(/ +/).indexOf('create_node') < 0) {
            return {'Disable': disable};
        }

        if ($(_s.JSTREE_CHECK_CLASS).is(':visible')) {
            return {'Disable': lockedit};
        }

        return {'Create': create, 'Copy': copy, 'Paste': paste, 'Outfall': outfall, 'Insert': insert, 'Rename': rename, 'Remove': remove};
    }


    function check_node(event, data) {
        if (data.action == 'deselect_node' && $(_s.NODETREE).find('.jstree-clicked').length < 1) {
            // 確保至少有一個 node 被選取
            $(_s.NODETREE).jstree('select_node', '#' + data.node.id);
        }

        if (!$(_s.JSTREE_CHECK_CLASS).is(':visible') && data.selected.length > 1) {
            clicked = $(_s.NODETREE).find('.jstree-clicked').each(function (index, node) {
                if (data.node.id != $(node).closest('li').attr('node_id')) {
                    $(_s.NODETREE).jstree().deselect_node(node, event);
                }
            });
        }

        if (NODETEMPLATE) {
            if ($(_s.JSTREE_CHECK_CLASS).is(':visible') && $(_s.EO_GUILD).is(':visible')) {
                if (data.node.data.default && data.node.state.selected) {
                    $(_s.NODETREE).jstree().deselect_node(data.node);
                    return false;
                }
                
                if (data.node.state.selected) {
                    $.each(data.node.children_d, function(index, value) {
                        $(_s.NODETREE).jstree('select_node', '#' + value);
                    });

                    var gap = false;
                    $.each(data.node.parents, function(index, value) {
                        if (value != '#') {
                            if ($(_s.NODETREE).jstree().get_node($('#' + value)).state.selected) {
                                gap = true;
                                return false;
                            }
                        }
                    });

                    if (gap) {
                        $.each(data.node.parents, function(index, value) {
                            if (!$(_s.NODETREE).jstree().get_node($('#' + value)).state.selected) {
                                $(_s.NODETREE).jstree('select_node', '#' + value);
                            } else {
                                return false;
                            }
                        });

                    }
                }

                if (!data.node.state.selected) {
                    $.each(data.node.children_d, function(index, value) {
                        $(_s.NODETREE).jstree('deselect_node', '#' + value);
                    });
                }
            }
        }
    }


    function open_node(event, data) {
        $(_s.SUB_COUNT).qtip({
            content: _s.SUB_COUNT_TIP
        });

        if (NODETEMPLATE) {
            if ($(_s.JSTREE_CHECK_CLASS).is(':visible') && $(_s.EO_GUILD).is(':visible')) {
                if (data.node.state.selected) {
                    $.each(data.node.children_d, function(index, value) {
                        $(_s.NODETREE).jstree('select_node', '#' + value);
                    });
                }
            }
        }
    }

    /* 載入查驗點 */
    function load_node(event, data) {
        var evt =  window.event || event,
            button = evt.which || evt.button;

        if (button != 1 && (typeof button != "undefined")) {
            return false;
        }

        if ($(_s.JSTREE_CHECK_CLASS).is(':visible')) {
            return false;
        }

        if (data.node != $(_s.LOCATION).data('node')) {
            update_location(data.node);

            var page = $(_s.NODE_TAB + data.node.id);
            $(_s.PAGES).hide();
            $(_s.EDIT_TOOLS).hide();
            $(_s.IMG_SELECTED).each(function() {
                $(this).remove();
            });

            if (page.length > 0) {
                page.show();
                setup_lazyload();
                check_marked_photo(page);
            } else {
                page = init_page(_s.NODE_TAB, data.node.id);
                $(_s.P_LOADING).css({'opacity': 1});
                load_image(page, data.node);
            }
        }
        
        $(_s.SUB_COUNT).qtip({
            content: _s.SUB_COUNT_TIP
        });
    }

    /* 更新目前位置 */
    function update_location(node) {
        var id = node.id,
            name = node.text,
            parent_id = node.parent,
            parents = [];

        var ol = $('<ol class="breadcrumb"></ol>'),
            paths = ['<li><a class="select_node active" node_id="' + id + '" href="#">' + name + '</li>'];

        while (parent_id != '#') {
            var parent_node = $(_s.NODETREE).jstree().get_node($('#' + parent_id));
            paths.unshift('<li><a class="select_node" node_id="' + parent_id + '" href="#">' + parent_node.text + '</li>');
            parent_id = $(_s.NODETREE).jstree().get_parent(parent_node);
        }

        paths.unshift('<li>' + _s.LOCATION_TITLE + '</li>');
        ol.html(paths.join(''));
        $(_s.LOCATION).empty();
        $(_s.LOCATION).append(ol);
        $(_s.LOCATION).data('node', node);
    }

    /* 載入頁面 */
    function load_image(page, node, url) {
        url = url || _s.API_URL + 'photo/?format=json&ordering=priority,create_time&node=' + node.id;
        $.ajax({
            url: url,
            type: 'GET',
            success: function (json, text, xhr) {
                var meta = json['meta'];
                var objs = json['objects'];
                $(_s.P_LOADING).css({'opacity': 0});

                setup_page(page, objs, node.id);
                if (meta['next']) {
                    load_image(page, node, meta['next']);
                } else {
                    // var page = $(_s.NODE_TAB + node.id);
                    setup_page_element(page);
                    setup_page_sorting(page);
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    }

    /* 重新命名查驗點 */
    function rename_node(event, data) {
        if (data.text == data.old) {
            return false;
        }

        $.ajax({
            url: _s.API_URL + 'node/' + data.node.id + '/',
            type: 'PUT',
            data: JSON.stringify({'name': data.text}),
            contentType: 'application/json',
            dataType: 'json',
            success: function(json){
                var node = $(json)[0];

                $(_s.LOCATION_ANCHOT.supplant({id: node.id})).html(node.name);
                $(_s.FOLDER_ANCHOT.supplant({id: node.id})).find('span').html(node.name);
                $(_s.NODE_TAB + node.id).find(_s.IMG_UNIT).each(function(index, element) {
                    $(element).data('node_name', node.name);
                });
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    }

    /* 刪除查驗點 */
    function delete_node(event, data) {
        var total_count = data.node.data.total_count;
        $.ajax({
            url: _s.API_URL + 'node/' + data.node.id + '/',
            type: 'DELETE',
            contentType: 'application/json',
            dataType: 'json',
            success: function (json, text, xhr) {
                $(_s.NODETREE).jstree('select_node', '#' + data.parent);
                $(_s.FOLDER_ANCHOT.supplant({id: data.node.id})).remove();
                setup_img_margin();
                reflash_time_tree();

                var node = $(_s.NODETREE).jstree().get_node($('#' + data.parent));
                    parent_id = node.parent;

                node.data.total_count -= total_count;
                update_node_grid(node);

                while (parent_id != '#') {
                    var parent_node = $(_s.NODETREE).jstree().get_node($('#' + parent_id));
                    parent_node.data.total_count -= total_count;
                    update_node_grid(parent_node);
                    parent_id = $(_s.NODETREE).jstree().get_parent(parent_node);
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    }

    /* 移動查驗點 */
    function move_node(event, data) {
        var put_data = {};
        var parent_node = $(_s.NODETREE).jstree().get_node($('#'+data.parent)),
            children = $(_s.NODETREE).jstree().get_children_dom(parent_node),
            child_count =  children.length;

        if(child_count > 0){
            if(data.position > 0){
                put_data.before_id = children[data.position-1].id;
            }else{
                put_data.after_id = children[data.position].id;
            }
        }else{
            put_data.parent_id = data.parent;
        }

        $.ajax({
            url: _s.API_URL + 'node/' + data.node.id + '/',
            type: 'PUT',
            contentType: 'application/json',
            dataType: 'json',
            data:JSON.stringify(put_data),
            success: function (json, text, xhr) {
                var target_page = $(_s.NODE_TAB + data.parent),
                    sub_unit = $(_s.FOLDER_ANCHOT.supplant({id: data.node.id}));

                if (sub_unit.length < 1) {
                    sub_unit = $(_s.SUB_TMP).tmpl({node_id: data.node.id, text: data.node.text});
                }

                if (target_page.length > 0) {
                    if (put_data.parent_id) {
                        if (target_page.find(_s.SUB_UNIT).length > 0) {
                            sub_unit.insertAfter(page.find(_s.SUB_UNIT).last());
                        } else {
                            target_page.prepend(sub_unit);
                        }
                    } else if (put_data.before_id) {
                        sub_unit.insertAfter($(_s.FOLDER_ANCHOT.supplant({id: put_data.before_id})))
                    } else if (put_data.after_id) {
                        sub_unit.insertBefore($(_s.FOLDER_ANCHOT.supplant({id: put_data.after_id})))
                    }
                } else {
                    sub_unit.remove();
                }

                setup_img_margin();

                var old_parent = $(_s.NODETREE).jstree().get_node($('#' + data.old_parent)),
                    parent_id = old_parent.parent;

                old_parent.data.total_count -= data.node.data.total_count;
                update_node_grid(old_parent);

                while (parent_id != '#') {
                    var parent_node = $(_s.NODETREE).jstree().get_node($('#' + parent_id));
                    parent_node.data.total_count -= data.node.data.total_count;
                    update_node_grid(parent_node);
                    parent_id = $(_s.NODETREE).jstree().get_parent(parent_node);
                }

                var new_parent = $(_s.NODETREE).jstree().get_node($('#' + data.parent)),
                    parent_id = new_parent.parent;

                new_parent.data.total_count += data.node.data.total_count;
                update_node_grid(new_parent);

                while (parent_id != '#') {
                    var parent_node = $(_s.NODETREE).jstree().get_node($('#' + parent_id));
                    parent_node.data.total_count += data.node.data.total_count;
                    update_node_grid(parent_node);
                    parent_id = $(_s.NODETREE).jstree().get_parent(parent_node);
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    }
}


function delete_file(files) {
    var msg;
    var no_permission = [];
    files.each(function(index, file) {
        var unit = $(file);
        if (!unit.find(_s.IMG_DELETE).length) {
            no_permission.push(unit.find(_s.NO).html());
        }
    })

    if (files.length > 1) {
        if (no_permission.length==files.length) {
            msg = _s.MULTI_NON_DEL_ALERT.supplant({total: files.length});
        } else if (no_permission.length) {
            msg = _s.MULTI_PART_DEL_ALERT.supplant({total: files.length, part: no_permission.length, execute: files.length-no_permission.length});
        } else {
            msg = _s.MULTI_DEL_ALERT.supplant({total: files.length});
        }
    } else {
        msg = _s.SINGLE_DEL_ALERT.supplant({file: files.data('origin')});
    }

    if(!confirm(msg)) {
        return false;
    }

    var count = 0;
    files.each(function(index, file) {
        var unit = $(file);
        if (unit.find(_s.IMG_DELETE).length) {
            $.ajax({
                url: _s.API_URL + 'photo/' + unit.data('id') + '/',
                type: 'DELETE',
                contentType: 'application/json',
                dataType: 'json',
                success: function (json, text, xhr) {
                    var page = unit.parents(_s.PAGES);

                    unit.remove();
                    setup_unit_pn(page);
                    setup_lazyload();

                    count += 1;
                    if (count == files.length) {
                        setup_img_margin();
                        reflash_time_tree();
                        $(_s.EDIT_TOOLS).fadeOut('fast');

                        var node = $(_s.NODETREE).jstree().get_node($('#' + $(_s.NODETREE).jstree('get_selected')));
                        parent_id = node.parent;

                        node.data.images_count -= files.length;
                        node.data.total_count -= files.length;
                        update_node_grid(node);

                        while (parent_id != '#') {
                            var parent_node = $(_s.NODETREE).jstree().get_node($('#' + parent_id));
                            parent_node.data.total_count -= files.length;
                            update_node_grid(parent_node);
                            parent_id = $(_s.NODETREE).jstree().get_parent(parent_node);
                        }
                    }
                },
                error: function(xhr, ajaxOptions, thrownError) {
                    REST_ERROR(xhr, ajaxOptions, thrownError);
                }
            })
        }        
    })
}


function switch_image() {
    var no = parseInt($(_s.IMAGE).data('no')),
        move = parseInt($(this).attr('value'));

    setup_showbox(no + move);
}


function update_node_grid(node) {
    $('#'+node.id).children('.jstree-grid-cell').find(_s.SUB_COUNT).text('{child}/{total}'.supplant({child: node.data.images_count, total: node.data.total_count}));
}


function update_time_grid(node) {
    $('#'+node.id).children('.jstree-grid-cell').find(_s.IMAGE_COUNT).text(node.data.count);
}


function reflash_time_tree() {
    $(_s.TIMETREE).find('.jstree-clicked').each(function(i, node) {
        $(_s.TIMETREE).jstree().deselect_node(node);
    });
    $(_s.PAGES).each(function(index, page) {
        if ($(page).attr('id').indexOf(_s.TIME_TAB.replace('#', '')) > -1) {
            $(page).remove();
        }
    })
    $(_s.TIMETREE).jstree('refresh');
}


function setup_option() {
    var current_tab = $(_s.MENU).find('.ui-state-active')[0];
    if (current_tab && current_tab.id == _s.BY_NODE.replace('#', '')) {
        $(_s.N_OPTIONS).show();
        $(_s.T_OPTIONS).hide();
    } else if (current_tab.id == _s.BY_TIME.replace('#', '')) {
        $(_s.T_OPTIONS).show();
        $(_s.N_OPTIONS).hide();
    } else {
        $(_s.T_OPTIONS).hide();
        $(_s.N_OPTIONS).hide();
    }
}


function init_page(type, node_id) {
    var page = $(type + node_id);
    if (page.length < 1) {
        page = $('<div id="' + type.replace('#', '') + node_id + '" class="' + _s.PAGES.replace('.', '') + '"></div>');
        $(_s.L_SHOW).append(page);
        page.hide();
    }
    return page;
}


function setup_page(page, files, node_id) {
    setup_subnode_unit(page, node_id);
    setup_thumbnail_unit(page, files);
    setup_img_margin();
    $(_s.L_SHOW).scrollTop(0);
}


function setup_page_element(page) {
    page.sortable({
        handle: $(_s.IMG_HEAD),
        items: $(_s.IMG_UNIT),
        cancel: _s.IMG_DELETE,
        placeholder: _s.IMG_MASK.replace('.', ''),
        stop: do_sort,
    });

    if ($(_s.SELECT_PANEL).is(':visible')) {
        check_marked_photo(page);    
    }

    function do_sort(event, ui) {
        var current_tab = $(_s.MENU).find('.ui-state-active')[0],
            order = $('a:contains("' + $(_s.B_ODERING).text() + '")').attr('value');
        
        if (current_tab.id == _s.BY_TIME.replace('#', '')) {
            apprise(_s.ITIME_SORT_ALERT, {'textOk': _s.OK}, function(result) {
                page.sortable('cancel');
            });
        } else if (current_tab.id == _s.BY_IMPROVE.replace('#', '')) {
            apprise(_s.IMPROVE_SORT_ALERT, {'textOk': _s.OK}, function(result) {
                page.sortable('cancel');
            });
        } else if (order != 'priority') {
            apprise(_s.SORT_ALERT.supplant({mode: $(_s.B_ODERING).text()}), {'textOk': _s.OK}, function(result) {
                page.sortable('cancel');
            });
        } else {
            setup_unit_pn(page);

            var photo_id = ui.item.data('id'),
                after_id = ui.item.next().data('id');

            $.ajax({
                url:  _s.API_URL + 'photo/' + photo_id + '/',
                type: 'PUT',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify({'after_id': after_id}),
                success: function (data) {
                    ui.item.data('priority', data.priority);
                },
            })
        }
    }
}


function setup_page_sorting(page, order) {
    if ($(_s.B_ODERING).is(':visible')) {
        order = order || $('a:contains("' + $(_s.B_ODERING).text() + '")').attr('value');
    } else if ($(_s.B_SORTING).is(':visible')) {
        order = order || $('a:contains("' + $(_s.B_SORTING).text() + '")').attr('value');
    } else {
        order = 'iimprove_tag';
    }
    
    if (page.attr('id').indexOf(_s.NODE_TAB) > -1) {
        page.find(_s.IMG_UNIT).sortElements(function(x, y) {
            var m = $(x).data(order),
                n = $(y).data(order);

            if (m == n) {
                return $(x).data('priority') > $(y).data('priority') ? 1 : -1;
            }
            return m > n ? 1 : -1;
        });
    } else {
        if (order.indexOf('-') > -1) {
            order = order.replace('-', '');
            page.find(_s.IMG_UNIT).sortElements(function(x, y) {
                var m = $(x).data(order),
                    n = $(y).data(order);

                if (m == n) {
                    return $(x).data('priority') < $(y).data('priority') ? 1 : -1;
                }
                return m < n ? 1 : -1;
            });
        } else {
            page.find(_s.IMG_UNIT).sortElements(function(x, y) {
                var m = $(x).data(order),
                    n = $(y).data(order);

                if (m == n) {
                    return $(x).data('priority') > $(y).data('priority') ? 1 : -1;
                }
                return m > n ? 1 : -1;
            });
        }
    }

    setup_unit_pn(page);
    setup_lazyload();
}


function setup_total_sorting() {
    var order, is_current_node;
    if ($(_s.B_ODERING).is(':visible')) {
        order = order || $('a:contains("' + $(_s.B_ODERING).text() + '")').attr('value');
        is_current_node = true;
    } else {
        order = order || $('a:contains("' + $(_s.B_SORTING).text() + '")').attr('value');
        is_current_node = false;
    }

    $(_s.PAGES).each(function(index, page) {
        var is_node = $(page).attr('id').indexOf(_s.NODE_TAB.replace('#', '')) > -1;
        if ((is_current_node && is_node) || (!is_current_node && !is_node)) {
            setup_page_sorting($(page), order);
        }
    });
}


function setup_unit_pn(page) {
    page.find(_s.IMG_UNIT).each(function(index, unit) {
        $(unit).find(_s.NO).html(index+1);
    });
}


function setup_lazyload() {
    $(_s.LAZY).lazyload({
        threshold: 200,
        effect: 'fadeIn',
        container: $(_s.L_SHOW),
        load : function() {
            $(this).removeClass('lazy');
        }
    });
}


function setup_thumbnail_unit(page, files) {
    $.each(files, function(i, file) {
        file.create_time = moment(file.create_time).format('YYYY-MM-DD').toString();
        file.time = file.time == null ? 'Unset' : moment(file.time).format('YYYY-MM-DD').toString();

        var photo_unit = $(_s.IMG_TMP).tmpl(file).data(file);
        photo_unit.find(_s.NO).html(page.find(_s.IMG_UNIT).length+1);

        photo_unit.hover(function(){
            photo_unit.find(_s.IMG_TEXT).show();
        }, function() {
            photo_unit.find(_s.IMG_TEXT).hide();
        });

        page.append(photo_unit);
    });
    
    page.show();
    setup_lazyload();
}


function setup_subunit(page, objects) {
    for (i=objects.length-1;i>=0;i=i-1) {
        var obj = objects[i];
        if ($('div[node_id="' + obj.id + '"]').length < 1) {
            var sub_unit = $(_s.SUB_TMP).tmpl({node_id: obj.id, text: obj.text});
            page.append(sub_unit);
        }
    }
    setup_img_margin();
}


function setup_subnode_unit(page, node_id) {
    if (page.find(_s.IMG_UNIT).length < 1) {
        var current_tab = $(_s.MENU).find('.ui-state-active')[0];
        if (current_tab.id == _s.BY_TIME.replace('#', '')) {
            return false;
        }

        $('#' + node_id).children('ul').children('li').each(function(index, element) {
            if (current_tab.id == _s.BY_NODE.replace('#', '')) {
                var child = $(_s.NODETREE).jstree().get_node($('#' + $(element).attr('id')));
            } else if (current_tab.id == _s.BY_IMPROVE.replace('#', '')) {
                var child = $(_s.IMPROVETREE).jstree().get_node($('#' + $(element).attr('id')));
            } else {
                return false;
            }
            if ($('div[node_id="' + child.id + '"]').length < 1) {
                var sub_unit = $(_s.SUB_TMP).tmpl({node_id: child.id, text: child.text});
                page.append(sub_unit);
            }
            
        });
    }
}


function setup_showbox(no) {
    var index = parseInt(no) - 1;
    var current = $(_s.PAGES).filter(':visible'),
        images = current.find(_s.IMG_UNIT),
        image = $(images[index]),
        data = image.data();

    var container = $(_s.L_PHOTO),
        panlayer = $(_s.PAN),
        dock = $(_s.DOCK)
        former = $(_s.FORMER),
        after = $(_s.AFTER);

    $(_s.CPN).html(no);
    $(_s.TPN).html(images.length);
    $(_s.IMAGE).data('no', no);
    $(_s.NEXT).show();
    if (no == 1) {
        former.hide();
    }
    if (no == images.length) {
        after.hide();
    }

    var url = data.sized_url + 'compress';

    if (!panobj) {
        panobj = panlayer.panzoom();
        dock.on('mousewheel.focal', function(e) {
            e.preventDefault();
            var delta = e.delta || e.originalEvent.wheelDelta;
            var zoomOut = delta ? delta < 0 : e.originalEvent.deltaY > 0;
            panlayer.panzoom('zoom', zoomOut, {
                increment: 0.1,
                animate: false,
                focal: e
            });
        });
    } else {
        panobj.panzoom('reset');
    }
    reset_image();
    setup_image(url);
    setup_info(data);
}


function setup_showbox_element() {
    var container = $(_s.L_PHOTO),
        anchor = $(_s.ANCHOR)
        panlayer = $(_s.PAN),
        next = $(_s.NEXT);
        tools = $(_s.VIEW_TOOLS),
        loading = $(_s.LOADING),
        info = $(_s.INFOLIST),
        comment = $(_s.CMTLIST);

    anchor.css({'top': -container.height(), 'left': -container.width()});
    next.css({'padding-top': (dialog_height() - $(_s.NEXT).height())/2});
    tools.css({'left': (container.width() - tools.width())/2});
    loading.css({'top': (container.height() - $(_s.LOADING).height())/2, 'left': (container.width() - $(_s.LOADING).width())/2});
    comment.css({'height': container.height() - info.height()});
}


function setup_image(url) {
    var container = $(_s.L_PHOTO),
        panlayer = $(_s.PAN),
        loading = $(_s.LOADING),
        image = $(_s.IMAGE);

    if (image.attr('src')) {
        panlayer.css({'visibility': 'hidden'});
    }

    loading.css({'visibility': 'visible'});
    image.css({'width': '', 'height': ''});
    image.attr('src', url);
}


function setup_info(data) {
    $(_s.PHOTO_ATTR).each(function(index, element) {
        element = $(element);
        if (element.find(_s.IMGDATE).length) {
            $(_s.IMGDATE).datetimepicker('update', data[element.attr('for')]);
        } else if(element.attr('type') == 'checkbox') {
            element.prop('checked', data[element.attr('for')])
        } else if (element.is('textarea')) {
            $(_s.IMGNOTE).val(data[element.attr('for')]);
        } else {
            element.text(data[element.attr('for')]);
        }
    });

    if ($(_s.MENU).find('.ui-state-active')[0].id == _s.BY_IMPROVE.replace('#', '')) {
        $(_s.PHOTO_TEXT).prop("readonly", true);
    } else {
        $(_s.PHOTO_TEXT).prop("readonly", false);
    }

    $(_s.IMGDATE).datetimepicker('setEndDate', $('[for="create_time"]').text());
    setup_comment(data);
}


function setup_comment(data) {
    var list = $(_s.CMTLIST);

    $(_s.NOCMT).show();
    $('li', list).remove();

    $.ajax({
        url: _s.API_URL + 'comment/?ordering=-create_time&photo=' + data['id'],
        type: 'GET',
        success: function (json, text, xhr) {
            var objs = json['objects'];
            if (objs.length > 0) {
                $(_s.NOCMT).hide();

                $.each(objs, function(index, obj) {
                    obj.create_time = moment(obj.create_time).format('YYYY-MM-DD HH:mm').toString();
                    setup_comment_unit(obj);
                });
                list.scrollTop(list[0].scrollHeight);
            }
        },
        error: function(xhr, ajaxOptions, thrownError) {
            REST_ERROR(xhr, ajaxOptions, thrownError);
        }
    });
}


function setup_comment_unit(data) {
    var comment_section = $(_s.CMT_TMP).tmpl(data).data(data).appendTo($(_s.CMTLIST));
    comment_section.hover(
        function(){
            $(this).find(_s.DEL_CMT).fadeIn('fast')
        },
        function(){
            $(this).find(_s.DEL_CMT).fadeOut('fast')
        }
    );
    comment_section.find(_s.DEL_CMT).click(delete_comment);

    function delete_comment() {
        var comment = $(this).parents('li');
        var id = comment.data('id');

        if(!confirm(_s.DEL_CMT_ALERT)){
            return false
        }

        $.ajax({
            url: _s.API_URL + 'comment/' + id + '/',
            type: 'DELETE',
            success: function (json, text, xhr) {
                comment.remove();
                if ($(_s.CMTLIST).find('li').length < 1) {
                    $(_s.NOCMT).show();
                }
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    }
}


function setup_grid(img_w, img_h) {
    var grid_w, grid_h;
    var gird = $(_s.GRID);

    if (img_w > img_h) {
        if(img_h/img_w <= 16/9 && img_h/img_w >= 10/16) {
            grid_w = 8;
            grid_h = 5;
        } else {
            grid_w = 8;
            grid_h = 6;
        }
    } else {
        if(img_h/img_w <= 16/9 && img_h/img_w >= 10/16) {
            grid_w = 5;
            grid_h = 8;
        } else {
            grid_w = 6;
            grid_h = 8;
        }
    }

    var alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
        unit_w = img_w / grid_w,
        unit_h = img_h / grid_h;

    gird.html('');
    gird.css({'width': img_w, 'height': img_h});

    for (i=0;i<grid_h;i++) {
        var grid_raw = $('<tr></tr>')
        for (j=0;j<grid_w;j++) {
            var grid_unit = $('<td class="grid_unit"></td>'),
                grid_text = $('<span class="gut"></span>');

            grid_text.html(alphabet[i] + j);
            grid_unit.html(grid_text)
            grid_raw.append(grid_unit)
        }
        gird.append(grid_raw);
    }
}


function setup_img_margin() {
    var unit_size = 300;
    var layout_width = $(_s.PAGES).width() - 2,
        gap = layout_width%unit_size,
        unit = (layout_width-gap)/unit_size,
        margin = gap / (unit*2);
    
    $(_s.SUB_UNIT).css({'margin-right': margin + 'px', 'margin-left': margin + 'px'});
    $(_s.IMG_UNIT).css({'margin-right': margin + 'px', 'margin-left': margin + 'px'});
    setup_lazyload();
}


function setup_tools_padding() {
    $(_s.EDIT_TOOLS).css({'margin-left': ($(_s.EDIT_TOOLS).parent().width() - $(_s.EDIT_TOOLS).width())/2});
    // $(_s.P_LOADING).css({'left': ($(_s.L_SHOW).width() - $(_s.P_LOADING).width())/2});
}


function reset_image() {
    $(_s.DOCK).data('angle', 0);
    $(_s.DOCK).rotate(0);
    $(_s.GUT).rotate(0);
    $(_s.GRID).addClass('hidden');
    $(_s.GRID_ON).show();
    $(_s.GRID_OFF).hide();
}


function resize_element() {
    setup_tools_padding();
    setup_img_margin();
    resize_dialog();
    resize_panel();
}


function resize_showbox() {
    var container = $(_s.L_PHOTO),
        panlayer = $(_s.PAN),
        dock = $(_s.DOCK),
        tools = $(_s.VIEW_TOOLS),
        loading = $(_s.LOADING),
        image = $(_s.IMAGE);

    var img_w = image.data('org_w'),
        img_h = image.data('org_h'),
        box_w = container.width() * 0.9,
        box_h = container.height() * 0.9;

    if ((img_w > box_w && img_h > box_h) || (img_w < box_w && img_h < box_h)) {
        var w_ratio = img_w / box_w,
            h_ratio = img_h / box_h;

        if (w_ratio > h_ratio) {
            image.css({'width': box_w});
        } else {
            image.css({'height': box_h});
        }

    } else if (img_w > box_w) {
        image.css({'width': box_w});
    } else if (img_h > box_h) {
        image.css({'height': box_h});
    }

    var set_w = image.width(),
        set_h = image.height(),
        act_w = container.width(),
        act_h = container.height();

    dock.css({'width': set_w, 'height': set_h, 'left': act_w + (act_w-set_w)/2, 'top': act_h + (act_h-set_h)/2});
    panobj.panzoom('reset');
    setup_showbox_element();
    setup_grid(set_w, set_h);
}


function resize_dialog() {
    if (showbox_dialog) {
        $(_s.SHOWBOX).dialog('option', 'width', dialog_width());
        $(_s.SHOWBOX).dialog('option', 'height', dialog_height());
        $(_s.SHOWBOX).dialog('option', 'position', 'center');
    }
}

function resize_panel() {
    $(_s.SELECT_PANEL).css({'width': $(_s.P_LOADING).width()});
    $(_s.PICK_BOARD).css({'width': $(_s.P_LOADING).width() - ($(_s.PICK_CTL).width() + 10)});
}


function close_alert() {
    var myEvent = window.attachEvent || window.addEventListener;
    var chkevent = window.attachEvent ? 'onbeforeunload' : 'beforeunload';
    myEvent(chkevent, function(e) {
        var status = $(_s.UPLOAD_STATUS).html();
        if (status == '0%' || status == '100%') {
            return true;
        }
        var confirmationMessage = _s.CLOSE_ALERT;
        (e || window.event).returnValue = confirmationMessage;
        return confirmationMessage;
    });
}

$(document).ready(function () {
    close_alert();
    initial_layout();
    initial_showbox();
    initial_image_loader();
    initial_nodetree();
    initial_timetree();
    if (IMPROVE) {
        initial_improvetree();
    }
});