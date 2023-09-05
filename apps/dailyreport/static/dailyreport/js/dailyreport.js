var int_check = /^-?[0-9]*$/;
var float_check = /^[+|-]?\d*\.?\d*$/;
var date_check = /^(([1-9]\d{0,3}|0)\-\d{2}\-\d{2})|(([1-9]\d{0,3}|0)\.\d{2}\.\d{2})|(([1-9]\d{0,3}|0)\/\d{2}\/\d{2})$/;
var email_check = /^[a-z0-9][-a-z0-9\.]*@([a-z0-9-]+\.)+[a-z]+$/;

//浮點數相加
function FloatAdd(arg1, arg2){
    var r1, r2, m;
    try { r1 = arg1.toString().split(".")[1].length; } catch (e) { r1 = 0; }
    try { r2 = arg2.toString().split(".")[1].length; } catch (e) { r2 = 0; }
    m = Math.pow(10, Math.max(r1, r2));
    return (FloatMul(arg1, m) + FloatMul(arg2, m)) / m;
}

//浮點數相減
function FloatSubtraction(arg1, arg2){
    var r1, r2, m, n;
    try { r1 = arg1.toString().split(".")[1].length } catch (e) { r1 = 0 }
    try { r2 = arg2.toString().split(".")[1].length } catch (e) { r2 = 0 }
    m = Math.pow(10, Math.max(r1, r2));
    n = (r1 >= r2) ? r1 : r2;
    return ((arg1 * m - arg2 * m) / m).toFixed(n);
}

//浮點數相乘
function FloatMul(arg1, arg2){
    var m = 0, s1 = arg1.toString(), s2 = arg2.toString();
    try { m += s1.split(".")[1].length; } catch (e) { }
    try { m += s2.split(".")[1].length; } catch (e) { }
    return Number(s1.replace(".", "")) * Number(s2.replace(".", "")) / Math.pow(10, m);
}

//浮點數相除
function FloatDiv(arg1, arg2){
    var t1 = 0, t2 = 0, r1, r2;
    try { t1 = arg1.toString().split(".")[1].length } catch (e) { }
    try { t2 = arg2.toString().split(".")[1].length } catch (e) { }
    with (Math) {
        r1 = Number(arg1.toString().replace(".", ""))
        r2 = Number(arg2.toString().replace(".", ""))
        return (r1 / r2) * pow(10, t2 - t1);
    }
}

function TransformThousands(num) {
//用來轉換成為千分位表示的數字用的
    var date_check=/^(([1-9]\d{0,3}|0)\-\d{2}\-\d{2})|(([1-9]\d{0,3}|0)\.\d{2}\.\d{2})|(([1-9]\d{0,3}|0)\/\d{2}\/\d{2})$/;
    if (date_check.test(num)){
        return num;
    }
    num = num + "";
    var re = /(-?\d+)(\d{3})/;
    while (re.test(num)) {
        num = num.replace(re,"$1,$2")
    }
    return num;
}

jQuery.needExist = function(id_tag, name) {
    // input 欄位驗證
    var value = $('#'+id_tag).val();
    if (value == '') {
        alert('未填寫 '+ name + ' 欄位');
          throw "";
        return false;
    } else {
        return value;
    }
}

function clone(obj) {
    if (null == obj || "object" != typeof obj) return obj;
    var copy = obj.constructor();
    for (var attr in obj) {
        if (obj.hasOwnProperty(attr)) copy[attr] = obj[attr];
    }
    return copy;
}

String.prototype.ReplaceAll = function (AFindText,ARepText)
{
  raRegExp = new RegExp(AFindText,"g");
  return this.replace(raRegExp,ARepText)
} 

var gettext = function (s) {
    return s;
}

//取得瀏覽器視窗高度
function getBrowserHeight() {
    if ($.support.msie) {
        return document.compatMode == "CSS1Compat" ? document.documentElement.clientHeight :
                 document.body.clientHeight;
    } else {
        return self.innerHeight;
    };
}

//取得瀏覽器視窗寬度
function getBrowserWidth() {
    if ($.support.msie) {
        return document.compatMode == "CSS1Compat" ? document.documentElement.clientWidth :
                 document.body.clientWidth;
    } else {
        return self.innerWidth;
    };
} 

var REST_ERROR = function (xhr, ajaxOptions, thrownError) {
    var $dialog = $('#error_dialog');
    var json = $.parseJSON(xhr.responseText);
    var buttons = {};
    buttons[gettext('Close')] = function () {
        $(this).dialog('close');
    };
    if (xhr.status == 500) {
        var title = 'HTTP ' + xhr.status;
        if (DEBUG) {
            var html = 'Error Code is <span class="notice"><a target="'+json['code']+'" href="'
                +BUGPAGE_URL+json['code']+'/">' + json['code'] + '</a></span>';
            var width = 300;
            var height = 200;
        } else {
            var html = json;
            var width = 1024;
            var height = 800;
        }
    } else {
        var s = '';
        for(var k in json){
            s += k + ': ' + json[k];
        }
        var title = 'Error ' + xhr.status + ' = ' + s;
        var html = '<pre style="color: red; background-color: yellow">'+json['traceback']+'</pre>';
        var width = 600;
        var height = 550;
    };
    $dialog.html(html).dialog({
        title: title,
        buttons: buttons,
        height: height,
        width: width
    })
};


//進行(顯示部分-輸入框)物件切換
function ClickShowInfo(){
    var $obj = $(this);
    var field_name = $obj.attr('field_name');
    var row_id = $obj.attr('row_id');
    $('#show_part_'+field_name+"_"+row_id).hide();
    $('#edit_part_'+field_name+"_"+row_id).show().focus();
}
 
function cutZero(old){
    old = String(old);
    newstr=old;
    if (!old || old.indexOf(".") == -1){
        return old;
    };
    var leng = old.length-old.indexOf(".")-1;
    if(old.indexOf(".")>-1){
        for(i=leng;i>0;i--){
            if(newstr.lastIndexOf("0")>-1 && newstr.substr(newstr.length-1,1)==0){
                var k = newstr.lastIndexOf("0");
                if(newstr.charAt(k-1)=="."){
                    return  newstr.substring(0,k-1);
                }else{
                    newstr=newstr.substring(0,k);
                }
            }else{
                return newstr;
            }
        }
    }
    return old;
}
 
//送資料
function BlurUpdateInfo(){
    //整理欄位資訊
    var $obj = $(this);
    if ($obj.attr('do_nothing') == 'true'){
        return false;
    }
    var row_id = $obj.attr('row_id');
    var field_type = $obj.attr('field_type');
    var field_name = $obj.attr('field_name');
    var table_name = $obj.attr('table_name');
    var module_name = $obj.attr('module_name');
    var class_name = $obj.attr('class');
    var value = $obj.val();
    var old_value = $obj.attr('old_value');
    var old_value = $obj.attr('old_value');
    if (value == old_value){
        if ($obj.attr('no_change') != 'true'){
            $('#show_part_'+field_name+"_"+row_id).show();
            $('#edit_part_'+field_name+"_"+row_id).hide();
        }
        return false;
    }
    if (!value){
        value = null;
    };
    //判斷是否為選單(ForeignKey 欄位)
    var is_select = $obj.attr('is_select');
    var listname_field_name = 'listname_'+field_name;
    //檢查各種格式是否正確
    if ((class_name.indexOf('needExist')) > -1 && !value){
        var message = field_name + '不可為空值！';
        alert(message);
        $('#edit_part_'+field_name+"_"+row_id).attr('value', old_value);
        return false;
    };
    if (field_type=='int' && value){
        if(!(int_check.test(value))){
            var message = field_name + '須為整數！';
            alert(message);
            return false;
        }
    };
    if (field_type=='float' && value){
        if(!(float_check.test(value))){
            var message = field_name + '須為數字！1565';
            alert(message);
            return false;
        }
    };
    if (field_type=='date' && value){
        if(!(date_check.test(value))){
            var message = field_name + '須為日期格式(如2013-01-19)！';
            alert(message);
            return false;
        }
    };
    if (field_type=='email' && value){
        if(!(email_check.test(value))){
            var message = field_name + '須為Email格式！';
            alert(message);
            return false;
        }
    };
    if (value == 'true'){
        value = true;
    } else if (value == 'false'){
        value = false;
    };
    //送資料到進行修改
    var url = '/'+module_name+'/api/v1/'+table_name+'/'+row_id+'/';
    if (value!=old_value){
        var data = {
            csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN
        }
        data[field_name] = value;
        $.ajax({
            url: url,
            type: 'PUT',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',
            success: function (json, text, xhr) {
                //取新的資料回來修改template
                $.ajax({
                    url: url,
                    type: 'GET',
                    contentType: 'application/json',
                    dataType: 'json',
                    success: function (json, text, xhr) {
                        if (is_select){
                            $('#edit_part_'+field_name+"_"+row_id).attr('value', value);
                            $('#edit_part_'+field_name+"_"+row_id).attr('old_value', value);
                            if (!json[listname_field_name]){
                                json[listname_field_name] = '';
                            }
                            $('#show_part_'+field_name+"_"+row_id).html(json[listname_field_name]);
                        } else {
                            if (field_type=='float'||field_type=='int'){
                                json[field_name] = cutZero(json[field_name]);
                            };
                            $('#edit_part_'+field_name+"_"+row_id).attr('value', json[field_name]);
                            $('#edit_part_'+field_name+"_"+row_id).attr('old_value', json[field_name]);
                            if (json[field_name] == 0){
                                var listname_value = '0';
                            } else if (!json[field_name]){
                                var listname_value = '';
                            } else {
                                var listname_value = String(json[field_name]).ReplaceAll('\n', '<br>');
                            };
                            if (field_type=='float'||field_type=='int'){
                                listname_value = TransformThousands(listname_value);
                            } else if (field_type=='str') {
                                if (listname_value=='0'){
                                    listname_value = '';
                                }
                            };
                            $('#show_part_'+field_name+"_"+row_id).html(listname_value);
                        }
                    },
                    error: REST_ERROR
                })
            },
            error: function () {
                $('#edit_part_'+field_name+"_"+row_id).attr('value', old_value);
            },
        })
    };
    //將顯示物件切換回來
    if ($obj.attr('no_change') != 'true'){
        $('#show_part_'+field_name+"_"+row_id).show();
        $('#edit_part_'+field_name+"_"+row_id).hide();
    }
}

function update_priority() {
    var $obj = $(this);
    var id = $obj.attr('id');
    var kind = $('#reset_right_menu').attr('kind');
    var row_id = $('#reset_right_menu').attr('row_id');
    $('#tr_item_' + row_id).click();
    var table_name = $('#reset_right_menu').attr('table_name');
    if (id=='update_priority_up'){
        var direction = 'up';
    } else if (id=='update_priority_down') {
        var direction = 'down';
    } else if (id=='update_priority_outdent') {
        var direction = 'outdent';
    } else if (id=='update_priority_indent') {
        var direction = 'indent';
    };
    var data = {
        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
        table_name: table_name,
        row_id: row_id,
        direction: direction,
    };
    $.ajax({
        url: '/dailyreport/update_priority/',
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function (json) {
            if (json['status']){
                if (direction=='up'){
                    $('#tr_item_' + row_id).insertBefore($('#tr_item_' + json['target_id']));
                } else if (direction=='down') {
                    $('#tr_item_' + row_id).insertAfter($('#tr_item_' + json['target_id']));
                } else if (direction=='outdent') {
                    var class_name = $('#td_item_name_' + row_id).attr('class');
                    var padding_name = class_name.split(' ')[0];
                    var padding_num = padding_name.split('_')[1];
                    var padding_num_2 = String(parseInt(padding_num) - 1);
                    $('#td_item_name_' + row_id).attr('class', class_name.replace(padding_num, padding_num_2))
                    $('#tr_item_' + row_id).insertAfter($('#tr_item_' + json['target_id']));
                } else if (direction=='indent') {
                    var class_name = $('#td_item_name_' + row_id).attr('class');
                    var padding_name = class_name.split(' ')[0];
                    var padding_num = padding_name.split('_')[1];
                    var padding_num_2 = String(parseInt(padding_num) + 1);
                    $('#td_item_name_' + row_id).attr('class', class_name.replace(padding_num, padding_num_2))
                    $('#tr_item_' + row_id).insertAfter($('#tr_item_' + json['target_id']));
                } ;

                $('#tr_item_' + row_id).effect("highlight", {color: 'red'}, 1500);
                var show_or_hide_type = $('#show_or_hide_item').attr('now');

                if (kind=='目錄'){
                    var target_id = row_id;
                    var sub_item_ids = json['sub_item_ids'].split('_');
                    for (t_id=0; t_id<sub_item_ids.length; t_id++){
                        $('#tr_item_' + sub_item_ids[t_id]).insertAfter($('#tr_item_' + target_id));
                        if (show_or_hide_type=='hide' && $('#tr_item_' + sub_item_ids[t_id]).attr('kind') == '工項'){
                            $('#tr_item_' + sub_item_ids[t_id]).hide();
                        }
                        target_id = sub_item_ids[t_id];
                        if (direction=='outdent'){
                            var class_name = $('#td_item_name_' + sub_item_ids[t_id]).attr('class');
                            if (class_name){
                                var padding_name = class_name.split(' ')[0];
                                var padding_num = padding_name.split('_')[1];
                                var padding_num_2 = String(parseInt(padding_num) - 1);
                                $('#td_item_name_' + sub_item_ids[t_id]).attr('class', class_name.replace(padding_num, padding_num_2));
                            }
                        } else if (direction=='indent'){
                            var class_name = $('#td_item_name_' + sub_item_ids[t_id]).attr('class');
                            if (class_name) {
                                var padding_name = class_name.split(' ')[0];
                                var padding_num = padding_name.split('_')[1];
                                var padding_num_2 = String(parseInt(padding_num) + 1);
                                $('#td_item_name_' + sub_item_ids[t_id]).attr('class', class_name.replace(padding_num, padding_num_2));
                            }
                        };
                        $('#tr_item_' + sub_item_ids[t_id]).effect("highlight", {color: 'green'}, 1500);
                    }
                };
                if (show_or_hide_type == 'hide'){
                    $('tr[kind=工項]').hide();
                }
            } else {
                alert(json['msg']);
                return false;
            }
        },
        error: function(){
        
}    })
}

function arrow_keys_to_detect(event){
    var $obj = $(this);
    var tabindex = $obj.attr('tabindex');
    var first = parseInt(tabindex.substring(0, tabindex.length-1));
    var last = parseInt(tabindex[tabindex.length-1]);
    // if (event.keyCode == 37) { //左
    //     $('input[tabindex=' + String(first) + String(last-1) + ']').focus();
    // } else if (event.keyCode == 39) { //右
    //     $('input[tabindex=' + String(first) + String(last+1) + ']').focus();
    // } else 
    if (event.keyCode == 38) { //上
        var n = 1;
        while ($('input[tabindex=' + String(first-n) + String(last) + ']').length==0 && n <= 10){
            n += 1;
        }
        $('input[tabindex=' + String(first-n) + String(last) + ']').focus();
    } else if (event.keyCode == 40) { //下
        var n = 1;
        while ($('input[tabindex=' + String(first+n) + String(last) + ']').length==0 && n <= 10){
            n += 1;
        }
        $('input[tabindex=' + String(first+n) + String(last) + ']').focus();
    }
}

function delete_item(){
    var $obj = $(this);
    var row_id = $('#reset_right_menu').attr('row_id');
    $('#tr_item_' + row_id).click();
    var table_name = $('#reset_right_menu').attr('table_name');
    if (table_name=='item'){
        var msg = '確定要刪除這個項目嗎？所有此工項日報表填報紀錄將會一併刪除!!! 若為目錄類型，亦將會一併刪除所屬全部工項!!!';
    } else {
        var msg = '確定要刪除這個項目嗎？若為目錄類型，亦將會一併刪除所屬全部工項!!!';
    }
    $.ajax({
        url: '/dailyreport/api/v1/' + table_name + '/' + row_id + '/',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: function (json, text, xhr) {
            var delete_ids = json['delete_ids'].split('.');
            if (confirm(msg)){
                if (confirm('再次確認!!! 將會刪除 ' + String(delete_ids.length) + ' 個項目，此動作將無法恢復!!!')){
                    $.ajax({
                        url: '/dailyreport/api/v1/' + table_name + '/' + row_id + '/',
                        type: 'DELETE',
                        contentType: 'application/json',
                        dataType: 'json',
                        success: function (json, text, xhr) {
                            for (n=0; n<delete_ids.length; n++){
                                var delete_id = delete_ids[n];
                                $('#edit_part_unit_price_' + delete_id).attr('value', '0');
                                $('#edit_part_unit_price_' + delete_id).change();
                                $('#tr_item_' + delete_id).remove();
                            }
                        },
                        error: REST_ERROR
                    })
                }
            }
        },
        error: REST_ERROR
    })
    $('#nothing').click();
}

function create_item(){
    var $obj = $(this);
    var id = $obj.attr('id');
    var row_id = $('#reset_right_menu').attr('row_id');
    var table_name = $('#reset_right_menu').attr('table_name');
    if (id=='create_same_dir'){
        var level = 'same_dir';
    } else if (id=='create_sub_dir'){
        var level = 'sub_dir';
    } else if (id=='create_item'){
        var level = 'item';
    }
    var data = {
        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
        table_name: table_name,
        row_id: row_id,
        level: level,
    }
    $.ajax({
        url: '/dailyreport/create_item/',
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function (json) {
            if (json['status']){
                var html = $(json['html']);
                html.insertAfter($('#tr_item_' + json['target_id']));
                $('.ClickShowInfo', html).click(ClickShowInfo);
                $('.BlurUpdateInfo', html).blur(BlurUpdateInfo);
                $('.BlurUpdateInfo', html).keydown(function(event) {
                    var $obj = $(this);
                    if (!$obj.is("textarea") && event.which == 13){
                        $obj.blur();
                    }
                });
                $('.recount_price', html).change(recount_price);
                $('.recount_day', html).change(recount_day);
                $('.right_click_menu', html).contextMenu('reset_right_menu', {
                    onContextMenu: function(e) {
                        return true;
                    },
                    onShowMenu: function(e, menu) {
                        var row_id = $(e.target).attr('row_id');
                        var need_right_click = $('#tr_item_' + row_id).attr('need_right_click');
                        var uplevel_id = $('#tr_item_' + row_id).attr('uplevel_id');
                        var kind = $('#tr_item_' + row_id).attr('kind');
                        $('#reset_right_menu').attr('row_id', row_id);
                        $('#reset_right_menu').attr('kind', kind);
                        if (!need_right_click){
                            $('#create_same_dir, #create_sub_dir, #create_item, #update_priority_up, #update_priority_down, #update_priority_outdent, #update_priority_indent, #delete_item', menu).remove();
                        } else if (!uplevel_id) {
                            $('#create_same_dir, #update_priority_up, #update_priority_down, #update_priority_outdent, #update_priority_indent, #delete_item', menu).remove();
                        } else if (kind != '目錄'){
                            $('#create_same_dir, #create_sub_dir', menu).remove();
                        }
                    return menu;
                    }
                });
                $('#tr_item_' + json['new_row_id']).click();
                $('#tr_item_' + json['new_row_id']).effect("highlight", {color: 'red'}, 1500);
            } else {
                alert(json['msg']);
            }
            
        },
        error: function(){
        }
    })
}


function recount_day(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var field_name = $obj.attr('field_name');
    var day = parseInt($obj.val());
    var dir_list = $('#tr_item_' + row_id).attr('top_dir').split('.');

    for (i=1;i<dir_list.length;i++){
        var min_day = 100000;
        var max_day = 1;
        var sub_items = $('tr[uplevel_id=' + dir_list[i] + ']');
        for (j=0;j<sub_items.length;j++){
            var id = sub_items[j].id.replace('tr_item_', '');
            var es_item_day = parseInt($('#edit_part_es_' + id).val());
            if (!es_item_day && es_item_day != 0){
                es_item_day = parseInt($('#span_part_es_' + id).html());
            }
            var ef_item_day = parseInt($('#edit_part_ef_' + id).val());
            if (!ef_item_day && ef_item_day != 0){
                ef_item_day = parseInt($('#span_part_ef_' + id).html());
            }
            if (es_item_day<min_day){
                min_day = es_item_day;
            }
            if (ef_item_day>max_day){
                max_day = ef_item_day;
            }
        }
        if (field_name=='es'){
            $('#span_part_es_' + dir_list[i]).html(min_day);
            if (min_day>max_day){
                $('#span_part_ef_' + dir_list[i]).html(min_day);
            }
        } else if (field_name=='ef'){
            $('#span_part_ef_' + dir_list[i]).html(max_day);
        }
    }

    if (field_name=='es'){
        var ef_day = parseInt($('#edit_part_ef_' + row_id).val());
        if (ef_day<day){
            $('#edit_part_ef_' + row_id).attr('value', day);
            $('#edit_part_ef_' + row_id).attr('old_value', day);
            $('#show_part_ef_' + row_id).html(day);
            $('#edit_part_ef_' + row_id).change();
        }
    } else if (field_name=='ef'){
        var es_day = parseInt($('#edit_part_es_' + row_id).val());
        if (es_day>day){
            $('#edit_part_es_' + row_id).attr('value', day);
            $('#edit_part_es_' + row_id).attr('old_value', day);
            $('#show_part_es_' + row_id).html(day);
            $('#edit_part_es_' + row_id).change();
        }
    }
}

function transform_page_type(){
    var $obj = $(this);
    var target = $obj.attr('target');
    var replace_target = $obj.attr('replace_target');
    window.location = String(window.location).replace(target, replace_target)
}

function click_update_testrecord_qualified(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var field_name = $obj.attr('field_name');
    var table_name = $obj.attr('table_name');
    var module_name = $obj.attr('module_name');
    var value = $obj.val();
    if (value=='True'){
        value = true;
    } else {
        value = false;
    };

    var url = '/'+module_name+'/api/v1/'+table_name+'/'+row_id+'/';

    var data = {
        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN
    };
    data[field_name] = value;
    $.ajax({
        url: url,
        type: 'PUT',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json',
        success: function (json, text, xhr) {

        },
        error: function () {
                alert("BAD PUT DATA didn't Success, SomeThing Wrong!!!");
            },
        })
}

function NewFileUploader($buttom, row_id, table_name){
    var buttom_id = $buttom.attr('id');
    var file_type = $buttom.attr('file_type');

    var uploader = new plupload.Uploader({
        runtimes: 'html5',
        browse_button: buttom_id,
        url: '/rcm/new_file_upload/',
        multi_selection: true,
        max_file_size : '100mb',
        multipart: true,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        },
        multipart_params : {
            csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
            row_id: row_id,
            table_name: table_name,
            file_type: file_type
        },
        init:{
            FilesAdded:function(up, files){
                var file_num = files.length;
                if (confirm('確定上傳這' + file_num + '個檔案?，按下確定後，上傳進度將顯示在下方，尚未結束前請勿關閉視窗!!!')){
                    // up.settings.multipart_params.sop_id = sop_id;
                    // up.settings.multipart_params.file_type = file_type;
                    var record_id = $buttom.attr('record_id');
                    for (i=0;i<file_num;i++){
                        var html = '';
                        html += '<li id="li_projectfile_' + files[i].id + '"><a id="file_link_' + files[i].id + '" href="">';
                        html += files[i].name + '</a>';
                        html += '<img class="deleteRow pointer ImageButtonHover"';
                        html += 'src="/static/project/image/plan_delete.png" width="20" table_name="projectfile"';
                        html += 'row_id="{{ file.id }}" row_name="' + files[i].name + '"';
                        html += 'id="file_img_' + files[i].id + '" module_name="rcm" remove_target="li_projectfile_{{ file.id }}" title="刪除檔案">';
                        html += '<div class="progress progress-striped active" id="bar_' + files[i].id + '" style="width: 200px;"><div class="progress-bar progress-bar-warning" id="file_percent_' + files[i].id + '" style="width: 0%"></div></div></li>'
                        $('#waitting_for_upload_' + record_id).append(html);
                    }
                    up.start();
                }else{
                    return false
                }
            },
            FileUploaded:function(up, file, res){
                var json = $.parseJSON(res.response);
                var record_id = $buttom.attr('record_id');
                $('#file_link_' + file.id).attr('href', '/rcm/download_file/' + row_id + '/ProjectFile/' + json['file_id'] + '/')
                $('#file_img_' + file.id).attr('row_id', json['file_id']);
                $('#file_img_' + file.id).attr('remove_target', 'li_projectfile_' + json['file_id']);
                $('#li_projectfile_' + file.id).attr('id', 'li_projectfile_' + json['file_id']);
                $('#bar_' + file.id).remove();
                var data = {
                    csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
                    file_add: json['file_id']
                }
                $.ajax({
                    url: '/rcm/api/v1/testrecord/' + record_id + '/',
                    type: 'PUT',
                    data: JSON.stringify(data),
                    contentType: 'application/json',
                    dataType: 'json',
                    success: function (json, text, xhr) {
                        // alert('Good');
                    },
                    error: function() {
                        // alert('FUCK');
                    }
                })
                $(".deleteRow").unbind("click");
                $(".deleteRow").click(deleteRow);
            },
            UploadProgress:function(up, file) {
                $('#file_percent_' + file.id).attr('style', 'width: ' + file.percent + "%");
                $('#file_percent_' + file.id).html(file.percent + "%");
            }
        }
    });
    uploader.init();
}

function deleteRow(){
    var $obj = $(this);
    var module_name = $obj.attr('module_name');
    var table_name = $obj.attr('table_name');
    var remove_target = $obj.attr('remove_target'); //刪除完畢後要移除的物件
    var hide_target = $obj.attr('hide_target'); //刪除完畢後要隱藏的物件
    var next_url = $obj.attr('next_url'); //刪除完畢後頁面轉移的連結
    var row_id = $obj.attr('row_id');
    var message = $obj.attr('message');
    var row_name = $obj.attr('row_name');
    if (!message){
        message = '您確定要刪除『 '+row_name+' 』嗎?';
    }
    var data = {csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN};
    if (confirm(message)){
        $.ajax({
            url: '/' + module_name + '/api/v1/' + table_name + '/' + row_id + '/',
            type: 'DELETE',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',
            success: function (json, text, xhr) {
                if (remove_target != '' && remove_target != undefined) {
                    $('#' + remove_target).remove();
                }
                if (next_url != '' && next_url != undefined){
                    alert(next_url);
                    window.location = next_url;
                }
                if (hide_target != '' && hide_target != undefined){
                    $('#' + hide_target).hide();
                }
            },
            error: REST_ERROR
        })
    } else {
        return false;
    }
}

$(document).ready(function(){
    CSRFMIDDLEWARETOKEN = $('input[name=csrfmiddlewaretoken]').val();
    $('.ClickShowInfo').click(ClickShowInfo);
    $('.BlurUpdateInfo').blur(BlurUpdateInfo);
    $('.BlurUpdateInfo').keydown(function(event) {
        var $obj = $(this);
        if (!$obj.is("textarea") && event.which == 13){
            $obj.blur();
        }
    });

    $('#update_priority_up').click(update_priority);
    $('#update_priority_down').click(update_priority);
    $('#update_priority_outdent').click(update_priority);
    $('#update_priority_indent').click(update_priority);
    $('#delete_item').click(delete_item);
    $('#create_same_dir').click(create_item);
    $('#create_sub_dir').click(create_item);
    $('#create_item').click(create_item);
    $('.transform_page_type').click(transform_page_type);

    $('.arrow_keys_to_detect').keydown(arrow_keys_to_detect); // 讓input可以用上下左右鍵來快速移動

    $.datepicker.regional['zh-TW'] = {
        clearText: '清除', clearStatus: '清除已選日期',
        closeText: '關閉', closeStatus: '取消選擇',
        prevText: '<上一月', prevStatus: '顯示上個月',
        nextText: '下一月>', nextStatus: '顯示下個月',
        currentText: '今天', currentStatus: '顯示本月',
        monthNames: ['一月','二月','三月','四月','五月','六月',
        '七月','八月','九月','十月','十一月','十二月'],
        monthNamesShort: ['一月','二月','三月','四月','五月','六月',
        '七月','八月','九月','十月','十一月','十二月'],
        monthStatus: '選擇月份', yearStatus: '選擇年份',
        weekHeader: '周', weekStatus: '',
        dayNames: ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'],
        dayNamesShort: ['周日','周一','周二','周三','周四','周五','周六'],
        dayNamesMin: ['日','一','二','三','四','五','六'],
        dayStatus: '設定每周第一天', dateStatus: '選擇 m月 d日, DD',
        dateFormat: 'yy-mm-dd', firstDay: 0, 
        initStatus: '請選擇日期', isRTL: false
    };
    $.datepicker.setDefaults($.datepicker.regional['zh-TW']);

    $(".datepicker").datepicker({
        changeMonth: true,
        changeYear: true,
        onClose: BlurUpdateInfo
    });

    $(document).ajaxStart(function(){
        var $img = $('#loading');
        var screenTop = $(document).scrollTop();
        var browserHeight = getBrowserHeight();
        $img.fadeIn();
    }).ajaxStop(function(){
        var $img = $('#loading');
        $img.fadeOut();
    });
});
