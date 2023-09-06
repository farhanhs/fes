var int_check = /^-?[0-9]*$/;
var float_check = /^[+|-]?\d*\.?\d*$/;
var date_check = /^(([1-9]\d{0,3}|0)\-\d{2}\-\d{2})|(([1-9]\d{0,3}|0)\.\d{2}\.\d{2})|(([1-9]\d{0,3}|0)\/\d{2}\/\d{2})$/;
var email_check = /^[a-z0-9][-a-z0-9\.]*@([a-z0-9-]+\.)+[a-z]+$/;

//密碼進行md5編碼
var md5password = function(password) {
    password = password.toLowerCase();
    var first_str = password.substring(0,1);
    var last_str = password.substring(password.length-1, password.length);
    return $.md5(first_str + last_str + '+' + password);
}

//密碼格式確認
jQuery.checkPasswordFormat = function(id_tag, message) {
    // input 欄位驗證
    var value = $('#'+id_tag).val();
    if (value.length < 8) {
        alert('密碼長度少於 8 個');
        return false;
    } else if (/^\d+$/.exec(value)) {
        alert('不可以全部設數字');
        return false;
    } else if (/^[a-zA-Z]+$/.exec(value)) {
        alert('不可以全部設英文字母');
        return false;
    } else if (/^[a-zA-Z0-9]+$/.exec(value)) {
        return value;
    } else {
        alert(message);
        return false;
    }
}

//EMAIL格式確認
jQuery.checkEmailFormat = function(id_tag, message) {
    // input 欄位驗證
    var value = $('#'+id_tag).val();
    value = value.replace(/\ /gi, '');
    if (/^[a-z0-9][-a-z0-9\.]*@([a-z0-9-]+\.)+[a-z]+$/i.exec(value)) {
        return value.toLowerCase();
    } else {
        alert(message);
        return false;
    }
}

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

//用來轉換成為千分位表示的數字用的
function TransformThousands(num) {
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

//用來移除千分位表示的數字用的
function remove_TransformThousands(num) {
    var num = num.ReplaceAll(',', '');
    return num;
}

//如果是數字欄位什麼都沒輸入即為0
function num_input_null_is_zero(){
    var $obj = $(this);
    if (!$obj.val()){
        $obj.val('0');
    }
}

//轉換input千分位符號使用
function inputcomma() {
    var $obj = $(this);
    var value = $obj.val();
    $obj.val(TransformThousands(value));
}

//移除input千分位符號使用
function remove_inputcomma() { 
    var $obj = $(this);
    var value = $obj.val();
    $obj.val(remove_TransformThousands(value));
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

//公司統一編號格試驗證
jQuery.checkCompanyNoFormat = function(id) {
    var value = $('#'+id).val();
    function valid(n) {
       return (n%10 == 0)?true:false;
    }
    function cal(n) {
       var sum=0;
       while (n!=0) {
          sum += (n % 10);
          n = (n - n%10) / 10;  // 取整數
         }
       return sum;
    }
    function nochk(novalue) {
       var tmp = new String("12121241");
       var sum = 0;
       for (i=0; i< 8; i++) {
         s1 = parseInt(novalue.substr(i,1));
         s2 = parseInt(tmp.substr(i,1));
         sum += cal(s1*s2);
       }
       if (!valid(sum)) {
          if (novalue.substr(6,1)=="7") return(valid(sum+1));
       }
       return(valid(sum));
    }
    var no = /^[0-9]{8}$/.exec(value);
    if (no == null){
        alert('統一編號須為 8 碼數字，您所填寫的則是「'+value+'」');
        return false;
    } else if (nochk(value) == false) {
        alert(no + ' 此為不合法的統一編號，請確認!');
        return false;
    }
    return value
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
 
//送資料
function BlurUpdateInfo(){
    //整理欄位資訊
    var $obj = $(this);
    var do_nothing = $obj.attr('do_nothing');
    if (do_nothing){
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
    if (value==old_value) {
        $('#show_part_'+field_name+"_"+row_id).show();
        $('#edit_part_'+field_name+"_"+row_id).hide();
        return false;
    }

    if (value){
        if (value.indexOf('</') > -1 || value.indexOf('\\') > -1){
            $obj.val(old_value);
            alert('輸入欄位不可包含特殊字元，如『</』、『\\』');
            return false;
        }
    };

    //判斷是否為選單(ForeignKey 欄位)
    var is_select = $obj.attr('is_select');
    var listname_field_name = 'listname_'+field_name;


    if (!value && ($obj.hasClass('hasDatepicker') || is_select == 'true')){
        value = null;
    }

    if (!value && (field_type=='int' || field_type=='float')){
        value = 0;
    }
    //檢查各種格式是否正確
    if ((class_name.indexOf('needExist')) > -1 && !value){
        if (!$obj.attr('field_ch_name')){
            var message = field_name + '不可為空值！';
        } else {
            var message = $obj.attr('field_ch_name') + '不可為空值！';
        }
        var message = field_name + '不可為空值！';
        alert(message);
        $('#edit_part_'+field_name+"_"+row_id).attr('value', old_value);
        return false;
    };
    if (field_type=='int' && value){
        value = value.ReplaceAll(',', '');
        if(!(int_check.test(value))){
            var message = field_name + '須為整數！';
            alert(message);
            return false;
        }
    };
    if (field_type=='float' && value){
        value = value.ReplaceAll(',', '');
        if(!(float_check.test(value))){
            var message = field_name + '須為數字！wdwd';
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
    var url = '/'+module_name+'/api/v2/'+table_name+'/'+row_id+'/';

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
                            $obj.find('option[value="' + value + '"]').attr('selected', 'selected')
                            $obj.attr('old_value', value);
                            if (!json[listname_field_name]){
                                json[listname_field_name] = '';
                            }
                            $('#show_part_'+field_name+"_"+row_id).html(json[listname_field_name]);
                        } else {
                            if (!json[field_name]){
                                json[field_name] = '';
                            }
                            if (field_type=='float'||field_type=='int'){
                                json[field_name] = parseFloat(json[field_name]);
                            };

                            $obj.val(json[field_name]);
                            $obj.attr('old_value', json[field_name]);
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
                    error: function (data) {
                        alert(data.responseText);
                    }
                })
            },
            error: function (data) {
                $obj.val(old_value);
                if (data.responseText){
                    alert(data.responseText);
                } else {
                    alert('操作失敗，可能系統忙碌中，請稍候重試一次。');
                }
            },
        })
    };
    //將顯示物件切換回來
    $('#show_part_'+field_name+"_"+row_id).show();
    $('#edit_part_'+field_name+"_"+row_id).hide();
}

function deleteRow(){
    var $obj = $(this);
    var module_name = $obj.attr('module_name');
    var table_name = $obj.attr('table_name');
    var remove_target = $obj.attr('remove_target'); //刪除完畢後要移除的物件
    var hide_target = $obj.attr('hide_target'); //刪除完畢後要隱藏的物件
    var next_url = $obj.attr('next_url'); //刪除完畢後頁面轉移的連結
    var do_change_action = $obj.attr('do_change_action'); //刪除完畢後什麼物件要執行.change()的動作
    var modal_hide = $obj.attr('modal_hide'); // 隱藏彈出的dialog
    var row_id = $obj.attr('row_id');
    var message = $obj.attr('message');
    var row_name = $obj.attr('row_name');
    if (!message){
        message = '您確定要刪除『 '+row_name+' 』嗎?';
    }
    var data = {csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN};
    if (confirm(message)){
        $.ajax({
            url: '/' + module_name + '/api/v2/' + table_name + '/' + row_id + '/',
            type: 'DELETE',
            data: JSON.stringify(data),
            contentType: 'application/json',
            dataType: 'json',
            success: function (json, text, xhr) {
                if (remove_target != '' && remove_target != undefined) {
                    $('#' + remove_target).remove();
                    $('.' + remove_target).remove();
                }
                if (next_url != '' && next_url != undefined){
                    window.location = next_url;
                }
                if (hide_target != '' && hide_target != undefined){
                    $('#' + hide_target).hide();
                }
                if (do_change_action != '' && do_change_action != undefined){
                    $(do_change_action).change();
                }
                if (modal_hide != '' &&　modal_hide != undefined){
                    $(modal_hide).modal('hide');
                }
            },
            error: function (data) {
                if (data.responseText){
                    alert(data.responseText);
                } else {
                    alert('操作失敗，可能系統忙碌中，請稍候重試一次。');
                }
            },
        })
    } else {
        return false;
    }
}

function reset_password(){
    var $obj = $(this);
    var user_id = $obj.attr('user_id');
    var password = $('#password_' + user_id).val();
    var no_need_re_password = $obj.attr('no_need_re_password');
    var next_url = $obj.attr('next_url')
    if (no_need_re_password == 'true'){
        var re_password = password;
    } else {
        var re_password = $('#re_password_' + user_id).val();
    }
    if (password != re_password){
        alert('您輸入的密碼不一致，請檢查您輸入的資訊!!');
        return false;
    }
    var password = $.checkPasswordFormat('password_' + user_id, '密碼格式不正確');

    $.ajax({
        url: '/u/reset_password/',
        type: "POST",
        data: {
            csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN, 
            submit: 'reset_password',
            password: md5password(password)},
        dataType: "json",
        success: function(json) {
            if (json['status']) {
                $('#password_' + user_id).attr('value', '');
                $('#re_password_' + user_id).attr('value', '');
                alert('密碼修改成功，下次登入請使用新密碼!!');
                window.location = next_url
            } else {
                alert(json['message']);
            }
        }
    });
}

function account_reset_password(){
    var $obj = $(this);
    var user_id = $obj.attr('user_id');
    var password = $('#password_' + user_id).val();
    var password = $.checkPasswordFormat('password_' + user_id, '密碼格式不正確');

    $.ajax({
        url: '/u/account_reset_password/',
        type: "POST",
        data: {
            csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN, 
            submit: 'reset_password',
            user_id: user_id,
            password: md5password(password)},
        dataType: "json",
        success: function(json) {
            if (json['status']) {
                $('#password_' + user_id).attr('value', '');
                alert('密碼修改成功，下次登入請使用新密碼!!');
            } else {
                alert(json['message']);
            }
        }
    });
}

function resultChangePage(){
    var $obj = $(this);
    var all_page = $obj.attr('all_page');
    var page = $obj.attr('page');
    for (var i=1; i<all_page; i++){
        if (page==i){
            $('.page' + i).show();
        } else {
            $('.page' + i).hide();
        }
    }
}

function editUserInfo(){
    var $obj = $(this);
    var user_id = $obj.attr('row_id');
    $.ajax({
        url: '/fishuser/api/v2/user/' + user_id + '/',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: function (json, text, xhr) {
            $('#DivUserInfoTable').show();

            $('#UserInfoTable').html($('#HideUserInfo').tmpl(json));

            $('#edit_part_unit_' + json['id']).val('/fishuser/api/v2/unit/' + json['unit_id'] + '/');
            $('#edit_part_unit_' + json['id']).attr('old_value', '/fishuser/api/v2/unit/' + json['unit_id'] + '/');

            if (json['is_active']){
                $('#edit_part_is_active_' + json['id']).val('true');
            } else {
                $('#edit_part_is_active_' + json['id']).val('false');
            }
            
            
            var groups = json['groups'];
            var group_html = '';
            for (i=0; i<groups.length; i++){
                group_html += '<div id="user_groups_' + groups[i][0] + '">' + groups[i][1];
                group_html += '<img user_id="' + json['id'] + '" value="' + groups[i][0] + '"';
                group_html += 'active="remove"';
                group_html += 'class="add_or_remove_user_group" src="/media/images/delete.png" width="20" title="移除群組">';
                group_html += '</div>';
            }
            group_html += '<div id="insertUserGroupPlace"></div>';
            $('#user_groups_list_' + json['id']).html(group_html);
            for (i=0; i<groups.length; i++){
                if ('註冊者_註冊者' == groups[i][1]){
                    $('#EditUserTableUnitTr_' + json['id']).remove();
                    $('#EditUserTableGroupTr_' + json['id']).remove();
                }
            };

            $('.add_or_remove_user_group').unbind('click');
            $('.add_or_remove_user_group').click(add_or_remove_user_group);
            $('.account_reset_password').unbind('click');
            $('.account_reset_password').click(account_reset_password);
            $('.ShowAddGroupDialog').unbind('click');
            $('.ShowAddGroupDialog').click(ShowAddGroupDialog);
            $('.ClickShowInfo').unbind('click');
            $('.ClickShowInfo').click(ClickShowInfo);
            $('.BlurUpdateInfo').unbind('blur');
            $('.BlurUpdateInfo').blur(BlurUpdateInfo);
            $('.BlurUpdateInfo').keypress(function(event) {
                var $obj = $(this);
                if (!$obj.is("textarea") && event.which == 13){
                    $obj.blur();
                }
            });
            $('html, body').animate({ scrollTop: 0 }, 'fast');
            // window.location = '#DivUserInfoTable';
        },
        error: REST_ERROR
    })
}

function updateStuffToUser(){
    var username = $(this).attr('username');
    if (!username) {
        var username = $('#updateStuffToUser').attr('value');
    }
    var user_fullname = $(this).attr('user_fullname');
    if (username) {
        var message = '確定轉換到 '+username+ '('+user_fullname+') 的帳戶嗎？';
        if(confirm(message)) {
            $.ajax({ url: '/u/ustu/', type: "POST", data:{
                submit: "updateStuffToUser",
                username: username, 
                csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN
            },
                dataType:"json", success:function(json){
                    if (json['status'] != true) {
                        alert(json['message']);
                    } else {
                        alert('轉換成功');
                        window.location = '/';
                    }
            }});
        }
    }
    return false;
}

function add_or_remove_user_group(){
    var $obj = $(this);
    var user_id = $obj.attr('user_id');
    var active = $obj.attr('active');
    if (active == 'remove'){
        var group_id = $obj.attr('value');
        if (!confirm('確定要移除群組嗎')){
            return false;
        }
    } else {
        var group_id = $('#new_group').val();
        if (!group_id){
            alert('請選擇群組!!!');
            return false;
        }
    }
    $.ajax({ 
        url:"/fishuser/add_or_remove_user_group/", 
        type: "POST", 
        data:{csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN, user_id: user_id, group_id: group_id, active: active}, 
        dataType:"json", 
        success:function(json){
            if (json['status']==true){
                if (active=='remove'){
                    $('#user_groups_' + group_id).remove();
                } else {
                    var group_html = '<div id="user_groups_' + json['group_id'] + '">' + json['group_name'];
                    group_html += '<img user_id="' + user_id + '" value="' + json['group_id'] + '"';
                    group_html += 'active="remove"';
                    group_html += 'class="add_or_remove_user_group" src="/media/images/delete.png" width="20" title="移除群組">';
                    group_html += '</div>';
                    $(group_html).insertBefore($('#insertUserGroupPlace'));
                    $('.add_or_remove_user_group').unbind("click");
                    $('.add_or_remove_user_group').click(add_or_remove_user_group);
                    $dialog.remove();
                }
            } else {
                alert('BAD');
            }
        }
    })
}

function ShowAddGroupDialog(){
    var $obj = $(this);
    var user_id = $obj.attr('user_id');
    var group_html = $('#group').html();
    var html = '<div class="flora" style="overflow: auto;"><table>'
    html += '請選擇群組';
    html += '<select id="new_group">';
    html += group_html + '</select>　　';
    html += '<input class="add_or_remove_user_group" active="add" user_id="' + user_id + '" value="新增群組" type="button">';
    html += '</div>';
    $dialog = $(html);
    $dialog.dialog({
        title: '請選擇群組',
        width: 500,
        height: 200,
        buttons: {
            '關閉視窗': function(){
                $dialog.remove();
            }
        }
    });
    $dialog.dialog('open');
    $('.add_or_remove_user_group').click(add_or_remove_user_group);
}

function creatUser(){
    $('#message').html('');
    var username = $.needExist('id_username', '帳號');
    var password = $.checkPasswordFormat('id_password', '密碼');
    var city_title = $('#city_title').val();
    var last_name = $.needExist('id_last_name', '姓');
    var first_name = $.needExist('id_first_name', '名字');
    var email = $.checkEmailFormat('id_email', 'Email格式不正確');
    var title = $('#id_title').val();
    var phone = $('#id_phone').val();
    var fax = $('#id_fax').val();
    var group = $('#id_group').val();
    var unit = $('#id_unit').val();
    var is_active = $('#id_is_active').val();
    if (username && last_name && first_name && email) {
        $.ajax({
            url:"/fishuser/account_create/",
            type: "POST",
            data:{submit: "creatUser", 
            username: username, last_name: last_name,
            first_name: first_name, email: email, title: title,
            phone: phone, fax: fax, group: group, city_title: city_title,
            unit: unit, is_active: is_active, password: md5password(password)
            },
            dataType:"json",
            beforeSend: function(XHR) {
                XHR.setRequestHeader('X-CSRFToken', $('input[name="csrfmiddlewaretoken"]').val());
            },
            success:function(json){
            if (json['status'] != true) {
                $('#message').html(' '+json['message']+' ');
            } else {
                alert('新增帳號『'+json['username']+'』成功');
                $('#message').html(' 回<a href="/fishuser/account_search/">帳戶列表</a>..... ');
                window.location = '/fishuser/account_search/';
            }}
        });
    }
    return false;
}

function create_email_list_user(){
    var need_email = $('#new_need_email').val();
    var place = $('#new_place').val();
    var name = $('#new_name').val();
    var departments = $('#new_departments').val();
    var title = $('#new_title').val();
    var tel = $('#new_tel').val();
    var phone = $('#new_phone').val();
    var fax = $('#new_fax').val();
    var email = $('#new_email').val();
    var memo = $('#new_memo').val();

    var data = {
        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
        need_email: need_email,
        place: place,
        name: name,
        departments: departments,
        title: title,
        tel: tel, 
        phone: phone,
        fax: fax,
        email: email,
        memo: memo
    };

    $.ajax({
        url: '/fishuser/api/v2/emaillist/',
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json',
        success: function (json, text, xhr) {
            location.reload();
        },
        error: function () {
        },
    })
}


$(document).ready(function(){
    CSRFMIDDLEWARETOKEN = $('input[name=csrfmiddlewaretoken]').val();
    $('body').on('click', '.ClickShowInfo', ClickShowInfo);
    $('body').on('blur', '.BlurUpdateInfo', BlurUpdateInfo);
    $('body').on('keypress', '.BlurUpdateInfo', function(event) {
        var $obj = $(this);
        if (!$obj.is("textarea") && event.which == 13){
            $obj.blur();
        }
    });
    $('.BlurUpdateInfo').keypress();

    $('.deleteRow').click(deleteRow);

    $('.reset_password').click(reset_password);
    $('.editUserInfo').click(editUserInfo);
    $('#creatUser').click(creatUser);
    $('#create_email_list_user').click(create_email_list_user);

    $('body').on('blur','.num_input_null_is_zero',num_input_null_is_zero);//如果是數字欄位什麼都沒輸入即為0
    $('body').on('blur','.inputcomma',inputcomma); // input 改變後的數字變換千分位
    $('body').on('click','.inputcomma',remove_inputcomma);// input 點擊時要先移除千分位符號
    $('body').on('keypress','.float',function(eve) {
        if ((eve.which != 46 || $(this).val().indexOf('.') != -1) && ([45,0,8].indexOf(eve.which)==-1 && (eve.which < 48 || eve.which > 57)) || (eve.which == 46 && $(this).caret().start == 0) ) {
            eve.preventDefault();
        }
        // this part is when left part of number is deleted and leaves a . in the leftmost position. For example, 33.25, then 33 is deleted
        $('.float').keyup(function(eve) {
            if($(this).val().indexOf('.') == 0) {
                $(this).val($(this).val().substring(1));
            }
        });
    });

    $('body').on('keypress','.integer',function(eve) {
        if ((eve.which != 46 || $(this).val().indexOf('.') != -1) && ([45,0,8].indexOf(eve.which)==-1 && (eve.which < 48 || eve.which > 57)) || (eve.which == 46) ) {
            eve.preventDefault();
        }
    });

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

    $('[data-toggle="tooltip"]').tooltip();
    
    $(document).ajaxStart(function(){
        var $img = $('#loading');
        var screenTop = $(document).scrollTop();
        var browserHeight = getBrowserHeight();
        $img.css({
            position: 'absolute',
            top: (screenTop+browserHeight/2) + 'px', left: '50%'
        });
        $("body").css('opacity', 0.4);
        $img.css('z-index', 10000).show();
    }).ajaxStop(function(){
        var $img = $('#loading');
        $("body").css('opacity', 1);
        $img.hide();
    });
    $('textarea').elastic();
});
