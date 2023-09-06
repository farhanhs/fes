function change_location(){
    var $obj = $(this);
    var row_id = $obj.val().split('/')[5];
    $('#location').html(locations[row_id]);
    $('#location').val('');
    $('#location').blur();
}

function add_guide(){
    var $obj = $(this);
    var field_name = $obj.attr('field_name');
    var value = $('#' + field_name).val();
    if (!value){
        return false;
    }
    var data = {
        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
    }
    data['add_' + field_name] = value;
    $.ajax({
        url: '/supervise/api/v2/supervisecase/' + case_id + '/',
        type: 'PUT',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json',
        success: function (json, text, xhr) {
            $('#' + field_name).val('');
            for (i=0; i < json[field_name].length; i++){
                var g_id = json[field_name][i]['id'];
                var g_name = json[field_name][i]['name'];
                if (!$('#tr_' + field_name + '_' + g_id).html()){
                    var html = '';
                    html += '<tr align="center" id="tr_' + field_name + '_' + g_id + '">';
                    html +=     '<td width="90%">' + json[field_name][i]['name'] + '</td>';
                    html +=     '<td>';
                    html +=         '<botton class="btn btn-danger btn-xs remove_guide" case_id="' + case_id + '" guide_id="' + g_id + '" field_name="' + field_name + '" title="刪除">';
                    html +=             '<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>';
                    html +=         '</botton>';
                    html +=     '</td>';
                    html += '</tr>';
                    $(html).insertBefore($('#insert_place_' + field_name));
                }
            }
            $('.remove_guide').unbind('click');
            $('.remove_guide').click(remove_guide);
        },
        error: function(){}
    })
}
                    
function remove_guide(){
    var $obj = $(this);
    var guide_id = $obj.attr('guide_id');
    var field_name = $obj.attr('field_name');
    var data = {
        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
    }
    data['remove_' + field_name] = guide_id;
    if (confirm('確定刪除嗎？')){
        $.ajax({
            url: '/supervise/api/v2/supervisecase/' + case_id + '/',
            type: 'PUT',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',
            success: function (json, text, xhr) {
                $('#tr_' + field_name +'_' + guide_id).remove();
            },
            error: function(){}
        })
    }
}

function add_error(){
    var $obj = $(this);
    var guide_id = $obj.closest('div').attr('row_id');
    Lobibox.prompt('text', //Any input type will be valid
        {
            title: '請輸入缺失編號',
            //Attributes of <input>
            attrs: {
                placeholder: ""
            },
            callback : function($this,type,ev){
                if (type == 'ok'){
                    var error_no = $this.getValue();
                    if (!error_no){
                        Lobibox.notify('warning', {
                            title: '系統訊息',
                            msg: '請輸入缺失編號',
                        });
                    }
                    var data = {
                        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
                        row_id: case_id,
                        error_no: error_no,
                        guide_id: guide_id,
                    }
                    $.ajax({
                        url: '/supervise/add_error_by_self/',
                        type: 'POST',
                        data: data,
                        dataType: 'json',
                        success: function (json, text, xhr) {
                            if (json['status']){
                                var $div = $(json['html']).appendTo($('.table_errors[row_id="' + guide_id + '"] > tbody'));
                                $div.find('.deleteRow').click(deleteRow);
                                $div.find('.BlurUpdateInfo').blur(BlurUpdateInfo);
                            } else {
                                Lobibox.notify('warning', {
                                    title: '系統訊息',
                                    msg: json['msg'],
                                });
                            }
                        },
                        error: function(){}
                    })
                }
            }
        }
    );
}

function search_error(e) {
    var $obj = $('#error_keyword');
    var keyword = $obj.val();
    var data = {
        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
        keyword: keyword
    };
    $.ajax({
        url: '/supervise/search_error/',
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function (json) {
            $('#search_error_result').html($(json['html']));
        },
        error: function (data) {
        },
    })
}

function click_copy(ev){
    var $obj = $(this);
    CopyToClipboard($obj.html());
    Lobibox.notify('success', {
        title: '系統訊息',
        msg: '已複製符號',
        delay: 1000,
    });
}

function CopyToClipboard(input) {
    var textToClipboard = input;

    var success = true;
    if (window.clipboardData) { // Internet Explorer
        window.clipboardData.setData ("Text", textToClipboard);
    }
    else {
        // create a temporary element for the execCommand method
        var forExecElement = CreateElementForExecCommand (textToClipboard);

            /* Select the contents of the element 
                (the execCommand for 'copy' method works on the selection) */
        SelectContent (forExecElement);

        var supported = true;

        // UniversalXPConnect privilege is required for clipboard access in Firefox
        try {
            if (window.netscape && netscape.security) {
                netscape.security.PrivilegeManager.enablePrivilege ("UniversalXPConnect");
            }

            // Copy the selected content to the clipboard
            // Works in Firefox and in Safari before version 5
            success = document.execCommand ("copy", false, null);
        }
        catch (e) {
            success = false;
        }

        // remove the temporary element
        document.body.removeChild (forExecElement);
    }
}

function CreateElementForExecCommand (textToClipboard) {
    var forExecElement = document.createElement ("div");
    // place outside the visible area
    forExecElement.style.position = "absolute";
    forExecElement.style.left = "-10000px";
    forExecElement.style.top = "-10000px";
    // write the necessary text into the element and append to the document
    forExecElement.textContent = textToClipboard;
    document.body.appendChild (forExecElement);
    // the contentEditable mode is necessary for the  execCommand method in Firefox
    forExecElement.contentEditable = true;

    return forExecElement;
}

function SelectContent (element) {
    // first create a range
    var rangeToSelect = document.createRange ();
    rangeToSelect.selectNodeContents (element);

    // select the contents
    var selection = window.getSelection ();
    selection.removeAllRanges ();
    selection.addRange (rangeToSelect);
}

function show_error_move_dialog(){
    var $obj = $(this);
    var guide_id = $obj.closest('.div_guide').attr('row_id');
    var $dialog = $('#error_move_dialog');
    $('#table_wait_to_move_errors > tbody').find('tr').remove();
    $('#table_move_to_target > tbody').find('tr').remove();
    $.each($('.table_errors[row_id="' + guide_id + '"] > tbody').find('tr'), function(){
        var $obj = $(this);
        var data = {
            id: $obj.attr('id').replace('error_tr_', ''),
            ec_no: $obj.find('.ec_no').html(),
            level: $obj.find('select[field_name="level"] > option:selected').text(),
            context: $obj.find('textarea[field_name="context"]').val()
        };
        var $div = $('#obj_wait_to_move_error').tmpl(data).appendTo($('#table_wait_to_move_errors > tbody'));
    });
    $.each($('.div_guide'), function(){
        var $obj = $(this);
        var data = {
            id: $obj.attr('row_id'),
            type: $obj.find('[name="guide_type"]').html(),
            name: $obj.find('[name="guide_name"]').html(),
        };
        var $div = $('#obj_wait_to_move_target').tmpl(data).appendTo($('#table_move_to_target > tbody'));
        if (guide_id == data['id']){
            $div.find('input').prop('checked', true);
        }
    });

    $dialog.find('.modal-body').css('height', document.body.clientHeight-150);
    $dialog.modal('show');
};

function error_move(){
    var $dialog = $('#error_move_dialog');
    var move_error_ids = [];
    $.each($('#table_wait_to_move_errors > tbody').find('input:checked'), function(){
        var $obj = $(this);
        move_error_ids.push($obj.closest('tr').attr('row_id'));
    });
    var target_guide_id = $('#table_move_to_target > tbody').find('[name="select_guide"]:checked').attr('value');
    if (!move_error_ids){
        Lobibox.notify('warning', {
            title: '系統訊息',
            msg: '您沒有選擇要移動的缺失',
        });
    } else {
        if (target_guide_id){
            var guide = '/supervise/api/v2/guide/' + target_guide_id + '/';
        } else {
            var guide = null;
        };
        $.each(move_error_ids, function(index, id){
            $.ajax({
                url: '/supervise/api/v2/error/' + id + '/',
                type: 'PUT',
                data: JSON.stringify({
                    guide: guide
                }),
                contentType: 'application/json',
                dataType: 'json',
                beforeSend: function(XHR) {
                    XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
                },
                success: function (json, text, xhr) {
                    $('#error_tr_' + id).appendTo($('.table_errors[row_id="' + target_guide_id + '"] > tbody'));
                },
                error: function (json) {
                    Lobibox.notify('error', {
                        title: '錯誤訊息',
                        msg: json.responseText,
                    });
                }
            });
        });
        $dialog.modal('hide');
    }
}

function guide_rename(){
    var $obj = $(this);
    var guide_id = $obj.closest('.div_guide').attr('row_id');
    var guide_name = $obj.closest('.div_guide').find('[name="guide_name"]').html();
    Lobibox.prompt('text', //Any input type will be valid
        {
            title: '請輸入要變更的委員姓名',
            //Attributes of <input>
            attrs: {
                value: guide_name
            },
            callback : function($this,type,ev){
                if (type == 'ok'){
                    var value = $this.getValue();
                    if (!value){
                        Lobibox.notify('warning', {
                            title: '錯誤訊息',
                            msg: '請輸入要變更的委員姓名',
                        });
                    } else {
                        if ($('[name="guide_name"]').filter(function(){
                                return $(this).html() === value
                            }).length != 0){
                            Lobibox.notify('warning', {
                                title: '錯誤訊息',
                                msg: '此紀錄已有此委員，不可重複',
                            });
                        } else {
                            $.ajax({
                                url: '/supervise/api/v2/guide/?name=' + value,
                                type: 'GET',
                                contentType: 'application/json',
                                dataType: 'json',
                                beforeSend: function(XHR) {
                                    XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
                                },
                                success: function (json, text, xhr) {
                                    if (json.objects.length > 0){
                                        update_new_guide(guide_id, json.objects[0]['id'], json.objects[0]['name']);
                                    } else {
                                        $.ajax({
                                            url: '/supervise/api/v2/guide/',
                                            type: 'POST',
                                            data: JSON.stringify({
                                                name: value
                                            }),
                                            contentType: 'application/json',
                                            dataType: 'json',
                                            beforeSend: function(XHR) {
                                                XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
                                            },
                                            success: function (json, text, xhr) {
                                                update_new_guide(guide_id, json['id'], json['name']);
                                            },
                                            error: function (json) {
                                                Lobibox.notify('error', {
                                                    title: '錯誤訊息',
                                                    msg: json.responseText,
                                                });
                                            }
                                        });
                                    };
                                },
                                error: function (json) {
                                    Lobibox.notify('error', {
                                        title: '錯誤訊息',
                                        msg: json.responseText,
                                    });
                                }
                            });
                        }
                    }
                }
            }
        }
    );
}

function update_new_guide(old_id, new_id, name){
    var $target_guide = $('.div_guide[row_id="' + old_id + '"]');
    var errors = $('.table_errors[row_id="' + old_id + '"] > tbody').find('tr');
    $target_guide.attr('row_id', new_id);
    var guide_type = $target_guide.find('[name="guide_type"]').html();
    $target_guide.find('.table_errors').attr('row_id', new_id);
    $target_guide.find('[name="guide_name"]').html(name);
    if (guide_type.indexOf('外部委員') != -1){
        var data = {
            add_outguide: name,
            remove_outguide: old_id,
        };
    } else {
        var data = {
            add_inguide: name,
            remove_inguide: old_id,
        };
    }
    $.ajax({
        url: '/supervise/api/v2/supervisecase/' + case_id + '/',
        type: 'PUT',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json',
        beforeSend: function(XHR) {
            XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
        },
        success: function (json, text, xhr) {
        },
        error: function (json) {
            Lobibox.notify('error', {
                title: '錯誤訊息',
                msg: json.responseText,
            });
        }
    });
    $.each(errors, function(){
        var $obj = $(this);
        var error_id = $obj.attr('id').replace('error_tr_', '');
        $.ajax({
            url: '/supervise/api/v2/error/' + error_id + '/',
            type: 'PUT',
            data: JSON.stringify({
                guide: '/supervise/api/v2/guide/' + new_id + '/',
            }),
            contentType: 'application/json',
            dataType: 'json',
            beforeSend: function(XHR) {
                XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
            },
            success: function (json, text, xhr) {
            },
            error: function (json) {
                Lobibox.notify('error', {
                    title: '錯誤訊息',
                    msg: json.responseText,
                });
            }
        });
    });
}

function delete_guide(){
    var $obj = $(this);
    var guide_id = $obj.closest('.div_guide').attr('row_id');
    var $target_guide = $('.div_guide[row_id="' + guide_id + '"]');
    var guide_type = $target_guide.find('[name="guide_type"]').html();
    if (guide_type.indexOf('外部委員') != -1){
        var data = {
            remove_outguide: guide_id,
        };
    } else {
        var data = {
            remove_inguide: guide_id,
        };
    }
    var errors = $('.table_errors[row_id="' + guide_id + '"] > tbody').find('tr');
    if (errors.length != 0){
        Lobibox.notify('warning', {
            title: '系統訊息',
            msg: '您必須刪除或移動委員所屬缺失才能刪除。',
        });
    } else {
        $.ajax({
            url: '/supervise/api/v2/supervisecase/' + case_id + '/',
            type: 'PUT',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',
            beforeSend: function(XHR) {
                XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
            },
            success: function (json, text, xhr) {
                $target_guide.remove();
                $('.table_errors[row_id="' + guide_id + '"]').remove();
            },
            error: function (json) {
                Lobibox.notify('error', {
                    title: '錯誤訊息',
                    msg: json.responseText,
                });
            }
        });
    }
}

function create_guide(){
    var $obj = $(this);
    if ($obj.attr('guide_type') == 'out'){
        var guide_type = '外部委員';
        var field_name = 'add_outguide';
    } else {
        var guide_type = '內部委員';
        var field_name = 'add_inguide';
    };

    var default_guide_html = `<select style="width:60%;display: inline-block;" id="select_default_guide_name" class="input-lg form-control"><option value="input">自行輸入委員名稱</option>`;
    for (i=0;i<default_guide.length;i++){
        default_guide_html += `<option value="${default_guide[i]}">${default_guide[i]}</option>`;
    };
    default_guide_html += `</select>`;
    default_guide_html += `<input style="width:40%;display: inline-block;" id="input_guide_name" type="text" class="input-lg form-control" value="" placeholder="委員名稱">`;
    setTimeout(function(){
        $('#input_guide_name').focus();
    }, 500);
    Lobibox.confirm({
        closeOnEsc: false,
        iconClass : 'glyphicon glyphicon-info-sign',
        title: '<span style="font-size: 1em;">請選擇要新增的【' + guide_type + '】</span>',
        msg: default_guide_html,
        buttons: {
            accept: {
                'class': 'lobibox-btn lobibox-btn-yes',
                text: '確定新增',
                closeOnClick: true
            },
            cancel: {
                'class': 'lobibox-btn lobibox-btn-no',
                text: '取消',
                closeOnClick: true
            }
        },
        callback: function ($this, type, ev) {
            if(type=="accept"){
                if ($('#select_default_guide_name').val() == 'input'){
                    var value = $('#input_guide_name').val();
                } else {
                    var value = $('#select_default_guide_name').val();
                };
                if (!value){
                    Lobibox.notify('warning', {
                        title: '錯誤訊息',
                        msg: '請輸入要新增的委員姓名',
                    });
                } else {
                    if ($('[name="guide_name"]').filter(function(){
                            return $(this).html() === value
                        }).length != 0){
                        Lobibox.notify('warning', {
                            title: '錯誤訊息',
                            msg: '此紀錄已有此委員，不可重複',
                        });
                    } else {
                        var data = {};
                        data[field_name] = value;
                        $.ajax({
                            url: '/supervise/api/v2/supervisecase/' + case_id + '/',
                            type: 'PUT',
                            data: JSON.stringify(data),
                            contentType: 'application/json',
                            dataType: 'json',
                            beforeSend: function(XHR) {
                                XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
                            },
                            success: function (json, text, xhr) {
                                $.ajax({
                                    url: '/supervise/api/v2/guide/?name=' + value,
                                    type: 'GET',
                                    contentType: 'application/json',
                                    dataType: 'json',
                                    beforeSend: function(XHR) {
                                        XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
                                    },
                                    success: function (json, text, xhr) {
                                        var data = json.objects[0];
                                        data['guide_type'] = guide_type;
                                        var $div = $('#obj_div_guide').tmpl(data).appendTo($('#td_guide_and_errors'));
                                        Lobibox.notify('success', {
                                            title: '系統訊息',
                                            msg: '已新增' + guide_type,
                                        });
                                    },
                                    error: function (json) {
                                        Lobibox.notify('error', {
                                            title: '錯誤訊息',
                                            msg: json.responseText,
                                        });
                                    }
                                });
                            },
                            error: function (json) {
                                Lobibox.notify('error', {
                                    title: '錯誤訊息',
                                    msg: json.responseText,
                                });
                            }
                        });
                    }
                }
            }
        }
    })
}

function select_default_guide_name(){
    var $obj = $(this);
    if ($obj.val() == 'input'){
        $('#input_guide_name').show();
    } else {
        $('#input_guide_name').hide();
    }
}

function remove_default_guide(){
    var $obj = $(this);
    var name = $obj.attr('name');
    Lobibox.confirm({
        msg: '是否確定要移除此常用委員？',
        buttons: {
            accept: {
                'class': 'lobibox-btn lobibox-btn-yes',
                text: '確認移除',
                closeOnClick: true
            },
            cancel: {
                'class': 'lobibox-btn lobibox-btn-no',
                text: '取消',
                closeOnClick: true
            },
        },
        callback: function ($this, type, ev) {
            if(type=="accept"){
                $.ajax({
                    url: '/supervise/api/v2/guide/?name=' + name,
                    type: 'GET',
                    contentType: 'application/json',
                    dataType: 'json',
                    beforeSend: function(XHR) {
                        XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
                    },
                    success: function (json, text, xhr) {
                        for (i=0;i<json.objects.length;i++){
                            $.ajax({
                                url: '/supervise/api/v2/guide/' + json.objects[i]['id'] + '/',
                                type: 'PUT',
                                data: JSON.stringify({
                                    is_default: false
                                }),
                                contentType: 'application/json',
                                dataType: 'json',
                                beforeSend: function(XHR) {
                                    XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
                                },
                                success: function (json, text, xhr) {
                                    $obj.closest('tr').remove();
                                    Lobibox.notify('success', {
                                        title: '系統訊息',
                                        msg: '已移除常用委員',
                                    });
                                },
                                error: function (json) {
                                    Lobibox.notify('error', {
                                        title: '錯誤訊息',
                                        msg: json.responseText,
                                    });
                                }
                            });
                        }
                    },
                    error: function (json) {
                        Lobibox.notify('error', {
                            title: '錯誤訊息',
                            msg: json.responseText,
                        });
                    }
                });
            }
        }
    })
}

function add_default_guide(){
    var value = prompt("請輸入要加入的常用委員名稱", "");
    if (!value){
        Lobibox.notify('error', {
            title: '錯誤訊息',
            msg: '請輸入要加入的常用委員名稱',
        });
    } else {
        $.ajax({
            url: '/supervise/api/v2/guide/?name=' + value,
            type: 'GET',
            contentType: 'application/json',
            dataType: 'json',
            beforeSend: function(XHR) {
                XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
            },
            success: function (json, text, xhr) {
                if (json.objects.length != 0){
                    $.ajax({
                        url: '/supervise/api/v2/guide/' + json.objects[0]['id'] + '/',
                        type: 'PUT',
                        data: JSON.stringify({
                            is_default: true
                        }),
                        contentType: 'application/json',
                        dataType: 'json',
                        beforeSend: function(XHR) {
                            XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
                        },
                        success: function (json, text, xhr) {
                            $('#default_guide_dialog').find('table > tbody').append(`<tr>
                                    <td>
                                        <button class="btn btn-danger remove_default_guide" name="${json['name']}">X</button>
                                    </td>
                                    <td>${json['name']}</td>
                                </tr>`);
                            Lobibox.notify('success', {
                                title: '系統訊息',
                                msg: '已加入常用委員',
                            });
                        },
                        error: function (json) {
                            Lobibox.notify('error', {
                                title: '錯誤訊息',
                                msg: json.responseText,
                            });
                        }
                    });
                } else {
                    $.ajax({
                        url: '/supervise/api/v2/guide/' + json.objects[0]['id'] + '/',
                        type: 'POST',
                        data: JSON.stringify({
                            name: value,
                            is_default: true
                        }),
                        contentType: 'application/json',
                        dataType: 'json',
                        beforeSend: function(XHR) {
                            XHR.setRequestHeader('X-CSRFToken', CSRFMIDDLEWARETOKEN);
                        },
                        success: function (json, text, xhr) {
                            $('#default_guide_dialog').find('table > tbody').append(`<tr>
                                    <td>
                                        <button class="btn btn-danger remove_default_guide" name="${json['name']}">X</button>
                                    </td>
                                    <td>${json['name']}</td>
                                </tr>`);
                            Lobibox.notify('success', {
                                title: '系統訊息',
                                msg: '已加入常用委員',
                            });
                        },
                        error: function (json) {
                            Lobibox.notify('error', {
                                title: '錯誤訊息',
                                msg: json.responseText,
                            });
                        }
                    });
                }
                
            },
            error: function (json) {
                Lobibox.notify('error', {
                    title: '錯誤訊息',
                    msg: json.responseText,
                });
            }
        });
    }
}


$(document).ready(function(){
    $('#place').change(change_location); //更新行政區
    $('#place').change();
    $('.add_guide').click(add_guide); //領隊、工作人員
    $('.remove_guide').click(remove_guide); //領隊、工作人員
    $('.click_copy').click(click_copy); //點擊複製

    $(document).on('change', '#select_default_guide_name', select_default_guide_name);
    $('#error_move').click(error_move);
    $(document).on('click', '.add_error', add_error); //新增缺失
    $(document).on('click', '.guide_rename', guide_rename); //委員更名
    $(document).on('click', '.show_error_move_dialog', show_error_move_dialog); //移動缺失
    $(document).on('click', '.delete_guide', delete_guide); //刪除缺失

    $(document).on('click', '.remove_default_guide', remove_default_guide); //移除常用委員
    $(document).on('click', '#add_default_guide', add_default_guide); //加入常用委員

    $('.create_guide').click(create_guide);
});