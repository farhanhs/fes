var _p = {
    B_TEMPLATE: '#edit_template',
    M_TEMPLATE: '#template_menu',
    EO_GUILD: '#export_oper_guide',
    EXPORT_NAME: '#temp_name',
    CANCEL_EXPORT_TEMPLATE_BUTTON: '#cancel_export',
    START_EXPORT_TEMPLATE_BUTTON: '#start_export',
    TEMPLATE_CARD: '#templatecard_layout',
    PICKED_LAYOUT: '#pickedtemp_layout',
    EDITORBOX: '#template_editor',
    EDITOR_LIST: '#template_list',
    EDITOR_BOOK: '#template_book',
    EDITOR_SAMPLE: '#sample_book',
    EDITOR_TABS: '#template_tabs',
    TEMPTAB_MY: '#templates_my',
    TEMPTAB_UNIT: '#templates_unit',
    TEMPTAB_PUBLIC: '#templates_public',
    SAMPLETREE: '#sample_tree',
    TEMPLATE_NAME: '#template_name',
    TEMPLATE_OPENNESS: '#public',
    ADD_TEMAPLTE: '#add_template',
    DEL_TEMAPLTE: '#del_template',
    ADD_SAMPLE: '#add_sample',
    DEL_SAMPLE: '#del_sample',
    TEMPLATE_EDIT: '.temp_edit',
    TEMPLATE_HOLDER: '.templates_holder',
    TEMPLATE_FILTER: '.name_filter',
    TEMPLATE_GROUP: '.templates_group',
    TEMPLATE_UNIT: '.template_unit',
    INSERT_CHECK: '.temp_insert_check',
    INSERT_CHECKED: '.temp_insert_check:checked',
    SELECTED_UNIT: '.selected_unit',
    CURRENT_SELECTED: '.selected_unit:visible',
    PICKED_CARD: '.picked_card',
    PICKED_SAMPLE: '.picked_samples',
    UNPICK: '.unpick_temp',
    UED_TAB: '.uneditable',
    DEFAULT_NODE_CLASS: '.glyphicon-folder-close',
    EDITOR_TITLE: '編輯查驗點樣版',
    INSERT_TITLE: '於查驗點『{node}』插入樣版',
    NT_EXPORT: '匯出為樣版',
    NT_INSERT: '插入樣版',
    NT_CANCEL: '取消插入',
    NT_CLOSE: '結束編輯',
    ALERT_TEMP_NAME: '請輸入樣版名稱',
    ALERT_TEMP_SELECT: '請勾選樣版！',
    ALERT_NODE_SELECT: '請選擇查驗點！',
    CANCEL: '取消',
    CREATE: '建立',
    DELETE: '刪除',
    ALERT_NONE_TEMPLATE_NAME: '請輸入樣版名稱',
    ALERT_CREATE_TEMPLATE_SURE: '是否建立『{template}』樣版？',
    ALERT_NONE_TEMPLATE_SELECTED: '請選擇要刪除的樣版！',
    ALERT_DELETE_TEMPLATE_SURE: '是否刪除『{template}』樣版？',
    ALERT_MULIT_SAMPLE_SELECTED: '請選擇單一資料夾！',
    ALERT_NONE_SAMPLE_SELECTED: '請選擇資料夾！',
    NO_CP_GUILD: '<p style="font-size: 18px; font-weight : bold;">本案尚未建立查驗點，請依照本工程特性設立查驗點，或利用樣版功能加入查驗點。</p>',
}

_s = $.extend(_s, _p);

var editor_dialog, editor_layout, is_insert;


function initial_toolbar_template_control() {
    $(_s.B_TEMPLATE).button().click(function() {
        open_edit_dialog();
    });

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
        $('.ui-button-text').click(function() {
            menu.hide();
        });
        return false;
    }

    /* 隱藏照片選取提示面板與操作紐 */
    function off_select() {
        $(_s.SELECT_PANEL).hide();
        $(_s.EDIT_TOOLS).hide();
        $(_s.IMG_SELECTED).each(function() {
            $(this).remove();
        })
    }

    /* 隱藏選取框與操作紐、取消所有選取只選取當下節點 */
    function off_multi_select() {
        $(_s.NODETREE).jstree().hide_checkboxes();
        $(_s.CTL_PANEL).hide();
        $(_s.EXPORT_NAME).val('');

        $(_s.NODETREE).find('.jstree-clicked').each(function (index, node) {
            if ($(_s.LOCATION).data().node.id != $(this).closest('li').attr('node_id')) {
                $(_s.NODETREE).jstree().deselect_node(node);
            }
        });
    }

    $(_s.CANCEL_EXPORT_TEMPLATE_BUTTON).button({
        'text':true, 
    }).click(function() {
        /* 恢復瀏覽模式 */
        $(_s.DEFAULT_NODE_CLASS).prev(_s.JSTREE_CHECK_CLASS).show();
        off_multi_select();
    });

    
    $(_s.START_EXPORT_TEMPLATE_BUTTON).button({
        'text':true, 
    }).click(function() {
        var name = $(_s.EXPORT_NAME).val(),
            nodes = $(_s.NODETREE).jstree('get_selected'),
            excluded = [];


        find_uncheck(nodes);
        function find_uncheck(id_array) {
            $.each(id_array, function(index, value) {
                var node = $(_s.NODETREE).jstree().get_node(value);

                if (!$(_s.NODETREE).jstree().get_node(value).state.selected) {
                    excluded.push(value);
                }
                find_uncheck($(_s.NODETREE).jstree().get_node(value).children);
            });
        }

        if (!name) {
            apprise(_s.ALERT_TEMP_NAME, '', function(result){
                $(_s.EXPORT_NAME).focus();
            });
            return false;
        }

        $.ajax({
            url: _s.API_URL + 'template/' + CASE_ID + '/export/',
            type: 'POST',
            data: JSON.stringify({'name': name, 'nodes': nodes, 'excluded': excluded}),
            contentType: 'application/json',
            dataType: 'json',
            success: function (json, text, xhr) {
                $(_s.B_TEMPLATE).click();
                off_multi_select();
                load_mytab(json['id']);
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    });
}


function reset_dialog() {
    $(_s.EDITOR_SAMPLE).html('');
    $(_s.INSERT_CHECKED).prop('checked', false);
    $(_s.SELECTED_UNIT).removeClass(_s.SELECTED_UNIT.replace('.', ''));
}


function open_edit_dialog() {
    is_insert = false;
    $(_s.TEMPLATE_EDIT).show();
    $(_s.UED_TAB).hide();
    $('a[href="' + _s.TEMPTAB_MY + '"]').click();
    reset_dialog();
    
    editor_dialog.dialog('option', 'buttons', [{
        text: _s.NT_CLOSE,
        click: function() {
            editor_dialog.dialog('close');
        }
    }]);
    editor_dialog.dialog('option', 'title', _s.EDITOR_TITLE);
    editor_dialog.dialog('open');
}


function open_insert_dialog(node_id, node_text, active) {
    is_insert = true;
    $(_s.TEMPLATE_EDIT).hide();
    $(_s.UED_TAB).show();
    reset_dialog();

    if (node_id === undefined) {
        node_id = $(_s.NODETREE).jstree('get_selected')[0];
    }

    if (node_text === undefined) {
        node_text = $(_s.NODETREE).jstree().get_node($(_s.NODETREE).jstree('get_selected')[0]).text;
    }

    editor_dialog.dialog('option', 'buttons', [{
        text: _s.NT_CANCEL,
        click: function() {
            editor_dialog.dialog('close');
        }
    },{
        text: _s.NT_INSERT,
        click: function() {
            var selected = $(_s.INSERT_CHECKED);

            if (selected.length) {
                var data = [];
                $.each(selected, function(index, value) {
                    data.push($(value).attr('value'));
                });

                var template_id = selected.attr('template_id');
                $.ajax({
                    url: _s.API_URL + 'node/' +  node_id + '/insert/',
                    type: 'PUT',
                    contentType: 'application/json',
                    data: JSON.stringify(data),
                    dataType: 'json',
                    success: function (json, text, xhr) {
                        $(_s.NODETREE).jstree(true).refresh_node(node_id);
                        editor_dialog.dialog('close');
                    },
                    error: function(xhr, ajaxOptions, thrownError) {
                        REST_ERROR(xhr, ajaxOptions, thrownError);
                    }
                });
            } else {
                apprise(_s.ALERT_TEMP_SELECT, {'textOk': _s.OK});
            }
        }
    }]);
    $(_s.INSERT_CHECK).css({'visibility': 'visible'});
    editor_dialog.dialog('option', 'title', _s.INSERT_TITLE.supplant({node: node_text}));
    editor_dialog.dialog('open');
    if (active) {
        $('a[href="' + active + '"]').click();
    }
}



function initial_editor() {
    if (!editor_dialog) {
        editor_dialog = $(_s.EDITORBOX).dialog({
            width: 900,
            height: 550,
            autoOpen: false,
            draggable: false,
            closeOnEsc: true,
            modal: true,
            resizable: false,
            open: function() {
                $('.ui-widget-overlay').addClass('custom_overlay');
                $('.ui-widget-overlay').click(function() {
                    $(_s.EDITORBOX).dialog('close');
                });

                if (!editor_layout) {
                    editor_layout = $(_s.EDITORBOX).layout({
                        west: {
                            paneSelector: _s.EDITOR_LIST,
                            resizable: true,
                            minSize: 400,
                        },
                        center: {
                            paneSelector: _s.EDITOR_BOOK,
                            minSize: 500,
                        }
                    });
                    setup_editor();
                } else {
                    editor_layout.resizeAll();
                }
            },
            beforeClose: function() {
                $('.ui-widget-overlay').removeClass('custom_overlay');
            },
            close: function() {
                $(_s.INSERT_CHECKED).prop('checked', false);
                $(_s.INSERT_CHECK).css({'visibility': 'hidden'});
            }
        });
    }
}


function load_mytab(focuson) {
    $(_s.TEMPTAB_MY).find(_s.TEMPLATE_GROUP).html('');
    $.ajax({
        url: _s.API_URL + 'template/?owner=my',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: function (json, text, xhr) {
            $.each(json.objects, function(index, value) {
                var unit = $(_s.TEMPLATE_CARD).tmpl(value);
                $(_s.TEMPTAB_MY).find(_s.TEMPLATE_GROUP).append(unit);
                if (focuson && parseInt(focuson) == parseInt(value['id'])) {
                    $(_s.TEMPLATE_GROUP).scrollTop($(_s.TEMPLATE_GROUP)[0].scrollHeight);
                    unit.click();
                }
            });
            if (is_insert) {
                $(_s.INSERT_CHECK).css({'visibility': 'visible'});
            } else {
                $(_s.INSERT_CHECK).css({'visibility': 'hidden'});
            }
        },
        error: function(xhr, ajaxOptions, thrownError) {
            REST_ERROR(xhr, ajaxOptions, thrownError);
        }
    });
}


function setup_editor() {
    $(_s.EDITOR_TABS).tabs({
        create: function(event, ui) {
            load_mytab();
        },
        activate: function(event, ui) {
            var hash = ui.newTab.context.hash,
                tag = hash.replace('#templates_', '');

            if (($(hash).find(_s.TEMPLATE_GROUP).html().length < 1) || !is_insert) {
                $(hash).find(_s.TEMPLATE_GROUP).html('');
                if (!is_insert) {
                    $(_s.EDITOR_SAMPLE).html('');
                    $(_s.INSERT_CHECKED).prop('checked', false);
                }

                $.ajax({
                    url: _s.API_URL + 'template/?owner=' + tag + '&case=' + CASE_ID,
                    type: 'GET',
                    contentType: 'application/json',
                    dataType: 'json',
                    success: function (json, text, xhr) {
                        $.each(json.objects, function(index, value) {
                            $(hash).find(_s.TEMPLATE_GROUP).append($(_s.TEMPLATE_CARD).tmpl({id: value.id, name: value.name}));
                        });
                        if (is_insert) {
                            $(_s.INSERT_CHECK).css({'visibility': 'visible'});
                        } else {
                            $(_s.INSERT_CHECK).css({'visibility': 'hidden'});
                        }
                    },
                    error: function(xhr, ajaxOptions, thrownError) {
                        REST_ERROR(xhr, ajaxOptions, thrownError);
                    }
                });
            }
        }
    });

    $(_s.TEMPLATE_GROUP).on('click', _s.TEMPLATE_UNIT, select_template);
    $(_s.TEMPLATE_GROUP).on('click', _s.INSERT_CHECK, check_template);
    $(_s.EDITOR_TABS).on('keyup', _s.TEMPLATE_FILTER, filter_template);
    $(_s.EDITOR_TABS).on('click', _s.ADD_TEMAPLTE, add_template);
    $(_s.EDITOR_TABS).on('click', _s.DEL_TEMAPLTE, del_template);
    $(_s.EDITOR_SAMPLE).on('change', _s.TEMPLATE_NAME, update_template_name);
    $(_s.EDITOR_SAMPLE).on('click', _s.ADD_SAMPLE, add_sample);
    $(_s.EDITOR_SAMPLE).on('click', _s.DEL_SAMPLE, del_sample);
    $(_s.EDITOR_SAMPLE).on('click', _s.UNPICK, unpick_template);

    function add_template() {
        var name = $(_s.TEMPLATE_FILTER).val();
        check_name(name);

        function check_name(name) {
            if (!name) {
                apprise(_s.ALERT_NONE_TEMPLATE_NAME, {'input': true, 'textOk': _s.CREATE, 'textCancel': _s.CANCEL}, function(result){
                    if (result && result.replace(/(^[\s]*)|([\s]*$)/g, '') == '') {
                        check_name(false);
                    } else if (result) {
                        create_template(result);
                    }
                });
            } else {
                apprise(_s.ALERT_CREATE_TEMPLATE_SURE.supplant({template: name}), {'confirm': true, 'textOk': _s.CREATE, 'textCancel': _s.CANCEL}, function(result){
                    if(result){
                        create_template(name);
                    };
                    return false;
                });
            }
        }


        function create_template(name) {
            $.ajax({
                url: _s.API_URL + 'template/',
                type: 'POST',
                data: JSON.stringify({'name': name}),
                contentType: 'application/json',
                dataType: 'json',
                success: function (json, text, xhr) {
                    load_mytab(json['id']);
                },
                error: function(xhr, ajaxOptions, thrownError) {
                    REST_ERROR(xhr, ajaxOptions, thrownError);
                }
            });
        }
    }

    function del_template() {
        var template_id = $(_s.CURRENT_SELECTED).attr('template_id'),
            template_name = $(_s.CURRENT_SELECTED).attr('text');

        if (!template_id) {
            apprise(_s.ALERT_NONE_TEMPLATE_SELECTED, {'textOk': _s.OK});
            return false;
        }

        apprise(_s.ALERT_DELETE_TEMPLATE_SURE.supplant({template: template_name}), {'confirm': true, 'textOk': _s.DELETE, 'textCancel': _s.CANCEL}, function(result){
            if(result){
                $.ajax({
                    url: _s.API_URL + 'template/' + template_id + '/',
                    type: 'DELETE',
                    contentType: 'application/json',
                    dataType: 'json',
                    success: function (json, text, xhr) {
                        $(_s.CURRENT_SELECTED).remove();
                        $(_s.EDITOR_SAMPLE).html('');
                    },
                    error: function(xhr, ajaxOptions, thrownError) {
                        REST_ERROR(xhr, ajaxOptions, thrownError);
                    }
                });
            };
        });
    }


    function add_sample() {
        var template_id = $(_s.CURRENT_SELECTED).attr('template_id'),
            samples = $(_s.SAMPLETREE).jstree('get_selected'),
            parent_point = '#';
            parent_sample = '';

        if (samples.length == 1) {
            parent_point = $(_s.SAMPLETREE).jstree().get_node($('#' + samples[0]));
            parent_sample = parent_point.data.sample_id;
        } else if (samples.length > 1) {
            apprise(_s.ALERT_MULIT_SAMPLE_SELECTED, {'textOk': _s.OK});
            return false;
        }

        $.ajax({
            url: _s.API_URL + 'sample/',
            type: 'POST',
            data: JSON.stringify({'template_id': template_id, 'parent_id': parent_sample}),
            contentType: 'application/json',
            dataType: 'json',
            success: function (json, text, xhr) {
                var tree = $(_s.SAMPLETREE).jstree(),
                    node = tree.create_node(parent_point, {'text': json.name, 'data': {'sample_id': json.id}, 'li_attr': {'sample_id': json.id}}, 'last');
                tree.edit(node);
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    }

    function del_sample() {
        var samples = $(_s.SAMPLETREE).jstree('get_selected');

        if (!samples.length) {
            apprise(_s.ALERT_NONE_SAMPLE_SELECTED, {'textOk': _s.OK});
            return false;
        }

        $.each(samples, function(index, value) {
            $(_s.SAMPLETREE).jstree().delete_node($(_s.SAMPLETREE).jstree().get_node($('#' + value)));
        });
    }


    function unpick_template() {
        $(_s.SELECTED_UNIT+'[template_id="' + $(this).parents(_s.PICKED_CARD).data('id') + '"]' ).click();
    }


    function update_template_name() {
        var template_id = $(_s.CURRENT_SELECTED).attr('template_id'),
            template_name = $(this).val();

        $.ajax({
            url: _s.API_URL + 'template/' + template_id,
            type: 'PUT',
            data: JSON.stringify({'name': template_name}),
            contentType: 'application/json',
            dataType: 'json',
            success: function (json, text, xhr) {
                $(_s.CURRENT_SELECTED).replaceWith($(_s.TEMPLATE_CARD).tmpl(json));
            },
            error: function(xhr, ajaxOptions, thrownError) {
                REST_ERROR(xhr, ajaxOptions, thrownError);
            }
        });
    }


    function pick_insert_temp(obj) {
        var box = obj.find(_s.INSERT_CHECK),
            add = box.prop('checked'),
            template_id = obj.attr('template_id');


        if (add) {
            obj.addClass(_s.SELECTED_UNIT.replace('.', ''));
        } else {
            obj.removeClass(_s.SELECTED_UNIT.replace('.', ''));
        }

        if (add) {
            var card = $(_s.PICKED_LAYOUT).tmpl({name: obj.attr('text')}),
                tree = card.find(_s.PICKED_SAMPLE);

            card.data('id', template_id);
            tree.jstree({
                'core': {
                    'animation': 0,
                    'multiple ': false,
                    'themes': {
                        'name': 'proton',
                        'responsive': true
                    },
                    'data': {
                        'url' : function (node){
                            return node.id === '#' ? _s.API_URL + 'sample/' + template_id + '/roots' : _s.API_URL + 'sample/' + node.data.sample_id + '/samples';
                        },
                    }
                },
            })
            .delegate('.jstree-closed>a', 'click.jstree', function(event){
                $.jstree.reference(this).open_node(this, false, false);
            });

            if ($(_s.EDITOR_SAMPLE).html().length < 1) {
                $(_s.EDITOR_SAMPLE).append('<h4 style="text-align: center; margin: 0px;">已選取樣版<h4><hr style="margin-top: 2px; margin-bottom: 2px; height: 1px; color: #272727; background-color: #272727;">')
            }

            $(_s.EDITOR_SAMPLE).append(card);
        } else {
            $(_s.EDITOR_SAMPLE).find(_s.PICKED_CARD).each(function(index, value) {
                if ($(value).data('id') == template_id) {
                    $(value).remove();
                }
            });
        }
    }

    function pick_edit_temp(obj) {
        $(_s.SELECTED_UNIT).removeClass(_s.SELECTED_UNIT.replace('.', ''));
        obj.addClass(_s.SELECTED_UNIT.replace('.', ''));


        var template_id = obj.attr('template_id'),
            title_group = $('<div class="form-inline"></div>');

        $(_s.EDITOR_SAMPLE).html('');
        // 暫不開放一般使用者制定公開樣版
        // $(_s.EDITOR_SAMPLE).append('<input type="text" id="' + _s.TEMPLATE_NAME.replace('#', '') + '"><input type="checkbox" id="' + _s.TEMPLATE_OPENNESS.replace('#', '') + '" style="margin: 0px 5px 0px 25px;"><label for="public">公開<label>');

        title_group.append('<input type="text" id="' + _s.TEMPLATE_NAME.replace('#', '') + '" class="form-control" style="width: 200px!important;">');
        if (obj.parents(_s.TEMPTAB_MY).length) {
            title_group.append('<input type="button" id="' + _s.ADD_SAMPLE.replace('#', '') + '" class="btn btn-default" value="新增資料夾"><input type="button" id="' + _s.DEL_SAMPLE.replace('#', '') + '" class="btn btn-default" value="刪除資料夾">');    
        }

        $(_s.EDITOR_SAMPLE).append(title_group);
        $(_s.EDITOR_SAMPLE).append('<hr style="margin: 2px 0px;">');
        $(_s.EDITOR_SAMPLE).append('<div id="' + _s.SAMPLETREE.replace('#', '') + '"></div>');

        // 暫不開放一般使用者制定公開樣版
        // $(_s.EDITOR_SAMPLE).find(_s.TEMPLATE_OPENNESS).prop('checked', obj.attr('is_public') == 'true');
        $(_s.EDITOR_SAMPLE).find(_s.TEMPLATE_NAME).attr('value', obj.attr('text'));

        if (!obj.parents(_s.TEMPTAB_MY).length) {
            // 暫不開放一般使用者制定公開樣版
            // $(_s.EDITOR_SAMPLE).find(_s.TEMPLATE_OPENNESS).prop('disabled', true);
            $(_s.EDITOR_SAMPLE).find(_s.TEMPLATE_NAME).prop('disabled', true);
        }

        $(_s.SAMPLETREE).jstree({
            'plugins': [
                'dnd', 'contextmenu'
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
                        return node.id === '#' ? _s.API_URL + 'sample/' + template_id + '/roots' : _s.API_URL + 'sample/' + node.data.sample_id + '/samples';
                    },
                }
            },
            'dnd': {
                'is_draggable': function(node) {
                    if ($(_s.EDITOR_TABS).tabs('option', 'selected') == 0) {
                        return true;
                    }
                    return false;
                }
            },
            'contextmenu': {
                'items': show_contextmenu
            }
        })
        .delegate('.jstree-closed>a', 'click.jstree', function(event){
            $.jstree.reference(this).open_node(this, false, false);
        })
        .on('rename_node.jstree', rename_smaple)
        .on('delete_node.jstree', delete_smaple)
        .on('move_node.jstree', move_smaple);

        function show_contextmenu(sample) {
            var tree = $(_s.SAMPLETREE).jstree();
            var disable, create, copy, paste, rename, remove;

            disable = {
                label: _s.NT_FBEDIT,
                action: function(obj) {
                    return false;
                }
            }

            create = {
                label: _s.NT_NEWNODE,
                action: function (obj) {
                    var template_id = $(_s.CURRENT_SELECTED).attr('template_id'),
                        parent_sample = sample.data.sample_id;

                    $.ajax({
                        url: _s.API_URL + 'sample/',
                        type: 'POST',
                        data: JSON.stringify({'template_id': template_id, 'parent_id': parent_sample}),
                        contentType: 'application/json',
                        dataType: 'json',
                        success: function (json, text, xhr) {
                            var tree = $(_s.SAMPLETREE).jstree(),
                                node = tree.create_node(sample, {'text': json.name, 'data': {'sample_id': json.id}, 'li_attr': {'sample_id': json.id}}, 'last');
                            tree.edit(node);
                        },
                        error: function(xhr, ajaxOptions, thrownError) {
                            REST_ERROR(xhr, ajaxOptions, thrownError);
                        }
                    });
                },
            }
            
            rename = {
                label: _s.NT_RENAME,
                action: function (obj) {
                    tree.edit(sample);
                },
            }
            
            remove = {
                label: _s.NT_REMOVE,
                action: function (obj) {
                    tree.delete_node(sample);
                },
            }

            if ($(_s.PERMISSION).attr('permissions').split(/ +/).indexOf('create_node') < 0) {
                return {'Disable': disable};
            }

            if ($(_s.JSTREE_CHECK_CLASS).is(':visible')) {
                return {'Disable': lockedit};
            }

            if ($(_s.EDITOR_TABS).tabs('option', 'selected') == 0) {
                return {'Create': create, 'Copy': copy, 'Paste': paste, 'Rename': rename, 'Remove': remove};
            }
            return {'Disable': disable};
        }


        /* 重新命名樣版查驗點 */
        function rename_smaple(event, data) {
            if (data.text == data.old) {
                return false;
            }

            $.ajax({
                url: _s.API_URL + 'sample/' + data.node.data.sample_id + '/',
                type: 'PUT',
                data: JSON.stringify({'name': data.text}),
                contentType: 'application/json',
                dataType: 'json',
                error: function(xhr, ajaxOptions, thrownError) {
                    REST_ERROR(xhr, ajaxOptions, thrownError);
                }
            });
        }

        /* 刪除樣版查驗點 */
        function delete_smaple(event, data) {
            $.ajax({
                url: _s.API_URL + 'sample/' + data.node.data.sample_id + '/',
                type: 'DELETE',
                contentType: 'application/json',
                dataType: 'json',
                error: function(xhr, ajaxOptions, thrownError) {
                    REST_ERROR(xhr, ajaxOptions, thrownError);
                }
            });
        }

        /* 移動樣版查驗點 */
        function move_smaple(event, data) {
            var put_data = {};
            var parent_node = $(_s.SAMPLETREE).jstree().get_node($('#'+data.parent)),
                children = $(_s.SAMPLETREE).jstree().get_children_dom(parent_node),
                child_count =  children.length;
            if(child_count > 0){
                if(data.position > 0){
                    put_data.before_id = $(children[data.position-1]).attr('sample_id')
                }else{
                    put_data.after_id = $(children[data.position]).attr('sample_id')
                }
            }else{
                put_data.parent_id = parent_node.data.sample_id;
            }

            $.ajax({
                url: _s.API_URL + 'sample/' + data.node.data.sample_id + '/',
                type: 'PUT',
                contentType: 'application/json',
                dataType: 'json',
                data:JSON.stringify(put_data),
                error: function(xhr, ajaxOptions, thrownError) {
                    REST_ERROR(xhr, ajaxOptions, thrownError);
                }
            });
        }
    }


    function check_template(event) {
        var obj = $(this);
        pick_insert_temp(obj.parents(_s.TEMPLATE_UNIT));
        event.stopPropagation();
    }


    function select_template(event) {
        var obj = $(this);
        if (is_insert) {
            var box = obj.find(_s.INSERT_CHECK);

            if (box.prop('checked')) {
                box.prop('checked', false);
            } else {
                box.prop('checked', true);
            }
            pick_insert_temp(obj);
        } else {
            pick_edit_temp(obj)
        }
    }


    function filter_template() {
        var text = $(this).val(),
            items = $(this).parents(_s.TEMPLATE_HOLDER).find(_s.TEMPLATE_UNIT);

        if (text) {
            items.hide();
            items.filter(':contains(' + text + ')').show();
        } else {
            items.show();
        }
    }
}


$(document).ready(function () {
    initial_editor();
    if (GUIDE) {
        apprise(_s.NO_CP_GUILD, {'textOk': _s.OK}, function(result) {
            $(_s.NODETREE).jstree('open_all');
            open_insert_dialog(GUIDE, GIT, _s.TEMPTAB_PUBLIC);
        });
    }
});