var md5password = function(password) {
    password = password.toLowerCase();
    var first_str = password.substring(0,1);
    var last_str = password.substring(password.length-1, password.length);
    return $.md5(first_str + last_str + '+' + password);
}

var askNewNumber = function() {
    $.ajax({ url:"/common/ann/", type: "GET", data:{IE: Math.random()},
            dataType:"json", success:function(json){
        var verifycode_id = json['verifycode_id'];
        var $img = $('#id_verify_image');
        $img.attr('src', '');
        setTimeout("updateNewNumber("+verifycode_id+")", 2000);
    }});
    return false;
}

var updateNewNumber = function(verifycode_id) {
    var $img = $('#id_verify_image');
    var $input = $('#id_verifycode_id');
    $input.val(verifycode_id);
    $img.attr('src', '/common/vi/'+verifycode_id+'.png');
}

function deleteEmailListUser(){
    var $obj = $(this);
    var user_name = $obj.attr('user_name');
    var row_id = $obj.attr('row_id');
    var message = '您確定要刪除聯絡名單『 '+user_name+' 』嗎?';
    if (confirm(message)){
        $.ajax({ url:"/u/ajax/", type: "POST", data:{submit: "deleteEmailListUser", 
            row_id: row_id}, dataType:"json", success:function(data){
            if(data["status"]){
                $('#tr_EmailList_'+row_id).remove();
            } else {
                alert(data['message']);
            }
        }});
    } else {
        return false;
    }
}

function addEmailListUser(){
    $.ajax({ url:"/u/ajax/", type: "POST", data:{submit: "addEmailListUser"
        }, dataType:"json", success:function(data){
        if(data["status"]){
            $(data['html']).insertBefore($('#insertEmailListUserPlace'));
            $('.deleteEmailListUser').click(deleteEmailListUser);
            $('.checkBoxNeedEmail').click(checkBoxNeedEmail);
            $('.ClickShowInfo').click(ClickShowInfo);
            $('.BlurUpdateInfo').blur(BlurUpdateInfo);
        } else {
            alert(data['message']);
        }
    }});
}

function checkBoxNeedEmail(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    $.ajax({ url:"/u/ajax/", type: "POST", data:{submit: "checkBoxNeedEmail",
        row_id: row_id}, dataType:"json", success:function(data){
        if(data["status"]){
        } else {
            alert(data['message']);
        }
    }});
}

function ClickShowInfo(){
    var $obj = $(this);
    var field_name = $obj.attr('field_name');
    var row_id = $obj.attr('row_id');
    $('#show_part_'+field_name+"_"+row_id).hide();
    $('#edit_part_'+field_name+"_"+row_id).show().focus();
}

function BlurUpdateInfo(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var field_name = $obj.attr('name');
    var table_name = $obj.attr('table_name');
    var value = $obj.attr('value');
    var old_value = $obj.attr('old_value');
    if (field_name=='place' && !value){
        return false;
    }
    if (value!=old_value){
        $.ajax({ url:"/u/ajax/", type: "POST", data:{submit: "BlurUpdateInfo",
            row_id: row_id, field_name: field_name, table_name: table_name,
            value: value
        }, dataType:"json", success:function(data){
            if(data["status"]){
                $('#edit_part_'+field_name+"_"+row_id).attr('value', data['return_value']);
                $('#edit_part_'+field_name+"_"+row_id).attr('old_value', data['return_value']);
                $('#show_part_'+field_name+"_"+row_id).html(data['return_value_ch']);
            } else {
                $('#edit_part_'+field_name+"_"+row_id).attr('value', value);
                alert(data['message']);
            }
        }});
    }
    $('#show_part_'+field_name+"_"+row_id).show();
    $('#edit_part_'+field_name+"_"+row_id).hide();
}

$(document).ready(function(){
    if ($('#menu').length >= 1) {
        var url = $('#menu').attr('value');
        var html = '';
        $.ajax({
        	url: '/u/getmenu/',
        	type: 'POST',
        	data: {url: url},
        	dataType: 'json',
        	success: function(json, status) {
        		html += json['menu'];
        		$('#menu').empty().append(html);
        	}
        });
    }

    $('.deleteEmailListUser').click(deleteEmailListUser);
    $('#addEmailListUser').click(addEmailListUser);
    $('.checkBoxNeedEmail').click(checkBoxNeedEmail);
    $('.ClickShowInfo').click(ClickShowInfo);
    $('.BlurUpdateInfo').blur(BlurUpdateInfo);

    $('#id_askNewNumber').click(askNewNumber);
    $('#id_askNewNumber').click();

    $('#login').click(function() {
        var username = $.needExist('id_username', '帳號');
        var password = $.needExist('id_password', '密碼');
        var verifycode_id = $.needExist('id_verifycode_id', '驗證圖片編號');
        var verify = $.needExist('id_verify', '圖片數字');
        if (username && password && verify) {
            $('#message').html(' 驗證帳號/密碼中..... ');
            
            $.ajax({ url:"/u/", type: "POST", data:{submit: "login", username: username,
	        	password: md5password(password), verifycode_id: verifycode_id, verify: verify},
	            dataType:"json", success: function(json){
                if (json['status'] == true) {
                    $('#message').html(' 登入中..... ').highlightFade();
                    if (json['next']){
                        alert(json['message']);
                        var location = json['next'];
                    } else {
                        var next = $('#next').text();
                        if (next == ''){
                            var location = '/fishuser/user_profile/';
                        } else {
                            var location = next;
                        }
                    }
                    $.ajax({
                        url: '/alertcheck/control/',
                        data: {submit: 'clearOverLoginLimitWarningMessage'},
                        dataType: 'json',
                        success: function(json){
                            window.location = location;
                        },
                        error: function(json){
                            window.location = location;
                        }
                    });
                } else {
                    $('#message').html(' '+json['message']+' ').highlightFade();
                    $('#id_verify').val('');
                    askNewNumber();
                }
        	}});
        }
        return false;
    });

    $('#editPassword').click(function(){
        var password = $.needExist('id_password', '新密碼');
        var password1 = $.needTheSame('id_password', 'id_password1', '密碼不一致');
        if (! password || ! password1) {
            return false;
        }
        var password1 = $.checkPasswordFormat('id_password1', '密碼格式不正確');
        if (password && password1) {
            $('#message').html(' 修改密碼中..... ');
            $.ajax({ url:"/u/eps/", type: "POST", data:{submit: "editPassword", password: md5password(password1)},
                    dataType:"json", success:function(json){
                	if (json['status'] != true) {
                        $('#message').html(' '+json['message']+' ').highlightFade();
                    } else {
                        alert('密碼修改成功，建議重新登入系統');
                        $('#message').html(' 回<a href="/u/vp/">個人帳戶</a>..... ').highlightFade();
                        window.location = '/u/vp/';
                    }
            }});
        }
        return false;
    });

    $('#editProfile').click(function(){
        $('#message').html('');
        var last_name = $.needExist('id_last_name', '姓');
        var first_name = $.needExist('id_first_name', '名字');
        var email = $.checkEmailFormat('id_email', 'ＥＭＡＩＬ格式不正確');
        var title = $('#id_title').val();
        var phone = $('#id_phone').val();
        var fax = $('#id_fax').val();

        if (last_name && first_name && email) {
        	$.ajax({ url:"/u/ep/", type: "POST", data:{submit: "editProfile", 
        		last_name: last_name, first_name: first_name, email: email, title: title,
        		phone: phone, fax: fax
        		}, 
        		dataType:"json", success:function(json){
    			if (json['status'] != true) {
                    $('#message').html(' '+json['message']+' ').highlightFade();
                } else {
                    alert('基本資料修改成功');
                    $('#message').html(' 回<a href="/u/vp/">個人帳戶</a>..... ').highlightFade();
                    window.location = '/u/vp/';
                }
            }});
        }
        return false;
    });

    $('#creatUser').click(function(){
        $('#message').html('');
        var username = $.needExist('id_username', '帳號');
        var password = $.checkPasswordFormat('id_password', '密碼');
        var city_title = $('#city_title').val();
        var last_name = $.needExist('id_last_name', '姓');
        var first_name = $.needExist('id_first_name', '名字');
        var email = $.checkEmailFormat('id_email', 'ＥＭＡＩＬ格式不正確');
        var title = $('#id_title').val();
        var phone = $('#id_phone').val();
        var fax = $('#id_fax').val();
        var group = $('#id_group').val();
        var unit = $('#id_unit').val();
        var is_active = $('#id_is_active').val();
        if (username && last_name && first_name && email) {
        	$.ajax({ url:"/u/account/creatuser/", type: "POST", data:{submit: "creatUser", 
        		username: username, last_name: last_name,
                first_name: first_name, email: email, title: title,
                phone: phone, fax: fax, group: group, city_title: city_title,
                unit: unit, is_active: is_active, password: md5password(password)
        		}, 
        		dataType:"json", success:function(json){
    			if (json['status'] != true) {
                    $('#message').html(' '+json['message']+' ').highlightFade();
                } else {
                    alert('新增帳號『'+json['username']+'』成功');
                    $('#message').html(' 回<a href="/u/account/">帳戶列表</a>..... ').highlightFade();
                    window.location = '/u/account/';
                }
            }});
        }
        return false;
    });

    $('#editUser').click(function(){
        $('#message').html('');
        var password = $('#id_password').val();
        if (password != '') {
            var password = $.checkPasswordFormat('id_password', '密碼格式不正確');
            var password = md5password(password);
        } else {
            var password = '';
        }
        var last_name = $.needExist('id_last_name', '姓');
        var first_name = $.needExist('id_first_name', '名字');
        var email = $.checkEmailFormat('id_email', 'ＥＭＡＩＬ格式不正確');
        var title = $('#id_title').val();
        var phone = $('#id_phone').val();
        var fax = $('#id_fax').val();
        var group = $('#id_group').val();
        var unit = $('#id_unit').val();
        var edituser_id = $('#id_edituser_id').attr('value');
        var is_active = $('#id_is_active').val();
        if (last_name && first_name && email) {
        	$.ajax({ url: '/u/account/edituser/'+edituser_id+'/', type: "POST", data:{submit: "editUser",
        		last_name: last_name,
                first_name: first_name, email: email, title: title,
                phone: phone, fax: fax, group: group,
                unit: unit, is_active: is_active, password: password},
                dataType:"json", success:function(json){
                	if (json['status'] != true) {
                        $('#message').html(' '+json['message']+' ').highlightFade();
                    } else {
                        alert('修改成功');
                        $('#message').html(' 回<a href="/u/account/">帳戶列表</a>..... ').highlightFade();
                        window.location = '/u/account/';
                    }
            }});
        }
        return false;
    });

    $('#registerUser').click(function(){
        $('#message').html('');
        var username = $.checkUsernameFormat('id_username', '帳號格式不正確');
        var password = username;
        var last_name = $.needExist('id_last_name', '姓');
        var first_name = $.needExist('id_first_name', '名字');
        var email = $.checkEmailFormat('id_email', 'ＥＭＡＩＬ格式不正確');
        var title = $('#id_title').val();
        var phone = $('#id_phone').val();
        var fax = $('#id_fax').val();
        if (username && last_name && first_name && email) {
        	$.ajax({ url: '/u/reguser/', type: "POST", data:{submit: "registerUser",
        		username:username, last_name: last_name,
                first_name: first_name, email: email, title: title,
                phone: phone, fax: fax,
                password: md5password(password)},
                dataType:"json", success:function(json){
                	if (json['status'] != true) {
                        $('#message').html(' '+json['message']+' ').highlightFade();
                    } else {
                        alert('申請成功，請使用申請帳號登入系統');
                        alert('第一次登入，密碼預設與您的帳號一樣');
                        $('#message').html(' 回<a href="/u/">登入頁面</a>..... ').highlightFade();
                        window.location = '/u/';
                    }
            }});
        }
        return false;
    });

    $('.updateStuffToUser').click(function(){
        var username = $(this).attr('username');
        if (!username) {
            var username = $('#updateStuffToUser').attr('value');
        }
        var user_fullname = $(this).attr('user_fullname');
		if (username) {
            var message = '確定轉換到 '+username+ '('+user_fullname+') 的帳戶嗎？';
            if(confirm(message)) {
            	$.ajax({ url: '/u/ustu/', type: "POST", data:{submit: "updateStuffToUser",
            		username: username, csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN},
                    dataType:"json", success:function(json){
                    	if (json['status'] != true) {
                            alert(json['message']);
                        } else {
                            alert('轉換成功');
                            var next = '/u/';
                            window.location = next;
                        }
                }});
            }
	    }
        return false;
    });
    
    $('#CencelLoginEmail').click(function(){
        var $obj = $(this);
        var value = $obj.attr('value');
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "CencelLoginEmail", value: value},
                dataType:"json", success:function(data){
            if (data['status'] == true){
                alert(data['msg']);
                $('#CencelLoginEmail').attr('value', data['return_value'])
            }
        }});
    });

    $.datepicker.setDefaults({showOn: 'both', buttonImageOnly: true, dateFormat: 'yy-mm-dd',
    buttonImage: '/media/jquery-plugins/calender.png', buttonText: ''});

    $('.date_field').each(function() {
    	$(this).datepicker();
    });
});
