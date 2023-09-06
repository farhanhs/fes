
var importProject = function(){
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var project_name = $obj.attr('project_name');
    var user_id = $obj.attr('user_id');
    var message = '您確定要匯入『'+project_name+'』此件標案進行管理嗎，匯入後您將會成為負責主辦工程師';
    if (confirm(message)) {
    	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "importProject", 
    		project_id: project_id, user_id: user_id
    		}, dataType:"json", success:function(json){
    			if (json['status'] != true){
                    alert(json['message']);
                } else {
                    alert('匯入成功，您已經可以在『我的工程』頁面瀏覽此件工程資訊');
                    $obj.fadeOut();
                    var html = '';
                    html += '<div class="flora" style="overflow: auto"><h2><br><span class="style1">'+json['project']['name']+'</span><br>';
                    html += '<table class="style0" style="border-collapse: collapse" border="1" cellpadding="2" cellspacing="2">';
                    html += '    <tr>';
                    html += '        <th bgcolor="#92D3B5">開工日期</th>';
                    html += '        <td>';
                    html += '            <input id="start_date" class="updateFRCMProject chooseDate" name="start_date" project_id="'+json['project']['id']+'" type="text" maxlength="10" size="15" value="'+json['project']['start_date']+'"/>';
                    html += '        </td>';
                    html += '    </tr>';
                    html += '    <tr>';
                    html += '        <th bgcolor="#92D3B5">監造方式</th>';
                    html += '        <td>';
                    html += '            <select class="updateFRCMProject" name="frcm_inspector_type" project_id="'+json['project']['id']+'">';
                    for (var i=0; i<json['inspector_type_id'].length; i++) {
                        html += '                <option value="'+json['inspector_type_id'][i]+'">'+json['inspector_type_value'][i]+'</option>';
                    }
                    html += '            </select>';
                    html += '        </td>';
                    html += '    </tr>';
                    html += '    <tr>';
                    html += '        <th bgcolor="#92D3B5">工期計算方式</th>';
                    html += '        <td colspan="3">';
                    html += '            <select class="updateFRCMProject" name="frcm_duration_type" project_id="'+json['project']['id']+'">';
                    for (var i=0; i<json['duration_type_id'].length; i++) {
                        html += '                <option value="'+json['duration_type_id'][i]+'">'+json['duration_type_value'][i]+'</option>';
                    }
                    html += '            </select>';
                    html += '            <div id="frcm_duration">';
                    html += '            工期：<input class="updateFRCMProject" name="frcm_duration" project_id="'+json['project']['id']+'" type="text" maxlength="10" size="10" value="0"/>天';
                    html += '            </div>';
                    html += '            <div id="frcm_duration_limit" style="display: none;">';
                    html += '            完工日期：<input class="updateFRCMProject chooseDate" name="frcm_duration_limit" project_id="'+json['project']['id']+'" type="text" maxlength="10" size="10" value=""/>';
                    html += '            </div>';
                    html += '        </td>';
                    html += '    </tr>';
                    html += '    <tr>';
                    html += '        <th bgcolor="#92D3B5">監造帳號是否啟用</th>';
                    html += '        <td>';
                    html += '            <select id="inspector_open" class="updateFRCMProject" name="inspector_open" project_id="'+json['project']['id']+'">';
                    html += '                <option value="open" selected="selected">啟用</option>';
                    html += '                <option value="close">關閉</option>';
                    html += '            </select>';
                    html += '        </td>';
                    html += '    </tr>';
                    html += '    <tr>';
                    html += '        <th bgcolor="#92D3B5">營造廠商是否啟用</th>';
                    html += '        <td>';
                    html += '            <select id="contractor_open" class="updateFRCMProject" name="contractor_open" project_id="'+json['project']['id']+'">';
                    html += '                <option value="open" selected="selected">啟用</option>';
                    html += '                <option value="close">關閉</option>';
                    html += '            </select>';
                    html += '        </td>';
                    html += '    </tr>';
                    html += '</table></h2></div>';
                    $dialog = $(html);
                    $dialog.dialog({
                        title: '工程案基本資料設定頁面',
                        width: 430,
                        height: 350,
                        buttons: {
                            '設定完畢關閉本視窗': function(){
                                $dialog.dialog('close');
                            }
                        }
                    });
                    
                    $dialog.find('.updateFRCMProject').change(updateFRCMProject);
                    $dialog.find('.chooseDate').each(function(){
                        $(this).datepicker();
                    });
                    $dialog.dialog('open');
                }
        }});
    }
}

var updateFRCMProject = function(){
    var $obj = $(this);
    var field_name = $obj.attr('name');
    var value = $obj.attr('value');
    var project_id = $obj.attr('project_id');
    if (field_name=='inspector_open') {
        alert('注意：此設定將會影響『監造廠商帳號』是否可以使用此系統!!');
    } else if (field_name=='contractor_open') {
        alert('注意：此設定將會影響『營造廠商帳號』是否可以使用此系統!!');
    }
    var message = '您確定要修改資訊嗎?';
    if (confirm(message)) {
    	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "updateFRCMProject", 
    		project_id: project_id, field_name: field_name, value: value
    		}, dataType:"json", success:function(json){
    			if (json['status'] != true){
                    alert(json['message']);
                } else {
                    alert('更新成功');
                    if (field_name=='frcm_duration_type'){
                        if (json['message']=='限期完工(日曆天每日施工)') {
                            $('#frcm_duration').hide()
                            $('#frcm_duration_limit').show()
                            alert('請填寫限期完工日期');
                        } else {
                            $('#frcm_duration').show()
                            $('#frcm_duration_limit').hide()
                            alert('請填寫工期');
                        }
                    } else if (field_name=='frcm_inspector_type'){
                        if (json['message']=='自辦監造(自動關閉監造帳號)'){
                            $('#inspector_open').attr('value', 'close')
                        }
                    }
                }
        }});
    }
}

var getProject = function(){
    var $obj = $(this);
    var code = $('#code').attr('value');
    if (!code) {
        alert('您尚未填寫認證碼!!');
    }
    var unit_no = $.checkCompanyNoFormat('unit_no', '公司統編');

    if (code && unit_no) {
    	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "getProject", 
    		code: code, unit_no: unit_no
    		}, dataType:"json", success:function(json){
    			if (json['status'] != true){
                    alert(json['message']);
                } else {
                    alert('認領成功，您認領的工程為『'+json['project_name']+'』');
                    alert('您的身分為『'+json['group']+'』，您已經可以在『我的工程』分頁中進行動作');
                    $('#code').attr('value', '')
                    $('#unit_no').attr('value', '')
                }
        }});
    }
}

var askToShareProject = function(){
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var project_name = $obj.attr('project_name');
    var user_id = $obj.attr('user_id');
    var message = '您確定要向負責人申請『'+project_name+'』此件標案進行『共同管理』嗎?';

    if (confirm(message)) {
    	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "askToShareProject", 
    		project_id: project_id, user_id: user_id
    		}, dataType:"json", success:function(json){
    			if (json['status'] != true){
                    alert(json['message']);
                } else {
                    alert('申請已送出，待此工程案負責主辦工程師，於工程基本頁面上按下允許後，即可開始管理');
                    $obj.fadeOut();
                }
        }});
    }
}

var regretToShareProject = function(){
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var project_name = $obj.attr('project_name');
    var user_id = $obj.attr('user_id');
    var message = '您確定要 取消 申請『共同管理』嗎?';

    if (confirm(message)) {
    	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "regretToShareProject", 
    		project_id: project_id, user_id: user_id
    		}, dataType:"json", success:function(json){
    			if (json['status'] != true){
                    alert(json['message']);
                } else {
                    alert('已 取消 請求共管');
                    $('#tr_'+project_id).fadeOut();
                }
        }});
    }
}

var answerAskShare = function(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var value = $obj.attr('value');
    if (value == 'yes'){
        var message = '您確定 "允許" 此件申請嗎? 當您允許後，此人將成為協同主辦工程師，享有編輯基本資訊的權限';
    } else {
        var message = '您確定 "拒絕" 此件申請嗎?';
    }
    if (confirm(message)) {
    	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "answerAskShare", 
    		row_id: row_id, value: value
    		}, dataType:"json", success:function(json){
    			if (json['status'] != true){
                    alert(json['message']);
                } else {
                    alert(json['message']);
                    $('#askShare_'+row_id).fadeOut();
                }
        }});
    }
}

var sendBackProject = function(){
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var message = '您確定要退還此件工程案嗎? 退還後您將失去管理工程案的權限';
    if (confirm(message)) {
    	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "sendBackProject", 
    		project_id: project_id
    		}, dataType:"json", success:function(json){
    			if (json['status'] != true){
                    alert(json['message']);
                } else {
                    alert('退還成功');
                    window.location = '/frcm/';
                }
        }});
    }
}

var transferEngineer = function(){
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var active = $obj.attr('active');
    var user_id = '';
    if (active == 'transfer'){
        var message = '最終確定轉讓 ?';
        var user_id = $obj.attr('user_id');
        if (!confirm(message)){
            return false;
        }
    }
	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "transferEngineer", 
		project_id: project_id, user_id: user_id, active: active
		}, dataType:"json", success:function(json){
			if (json['status'] != true){
	            alert(json['message']);
	        } else {
	            if (active == 'get_list'){
	                var html = '<div class="flora" style="overflow: auto"><h2>您欲將此工程的負責主辦身分轉讓給<br><br>';
	                for (var u=0; u<json['users'].length; u++){
	                    html += '<a class="transferEngineer" active="transfer" user_id="'+json['users'][u]['id']+'" project_id="'+project_id+'">';
	                    html += json['users'][u]['title']+'___'+json['users'][u]['name'];
	                    html += '</a><br>';
	                }
	                html += '<br><br>請直接點選上列您欲轉換的使用者<br>注意：一但轉換後您將轉為"協同主辦工程師"。</h2></div>';
	                $dialog = $(html);
	                $dialog.dialog({
	                    title: '工程案基本資料設定頁面',
	                    width: 500,
	                    height: 300,
	                    buttons: {
	                        '取消動作關閉本視窗': function(){
	                            $dialog.dialog('close');
	                        }
	                    }
	                });
	                $dialog.find('.transferEngineer').click(transferEngineer);
	                $dialog.dialog('open');
	            } else if (active == 'transfer'){
	                if (json['status'] != true){
	                    alert(json['message']);
	                } else {
	                    alert('轉讓成功，您已經成為 "協同主辦工程師" ');
	                    $dialog.dialog('close');
	                    var html = '<a border="2" class="sendBackProject" project_id="'+project_id+'"><img src="/media/frcm/image/sendback.png" height="100" width="166" title="退還工程案"></a>';
	                    html = $(html);
	                    html.insertAfter($('.transferEngineer'));
	                    $('.transferEngineer').fadeOut();
	                    $('.sendBackProject').click(sendBackProject);
	                }
	                
	            }
	        }
    }});
}

var editProjectInfo = function(){
    var $obj = $(this);
    var target_id = $obj.attr('id');
    $('.show_' + target_id).hide();
    $('.edit_' + target_id)
                    .fadeIn()
                    .focus();
}

function TransformThousands(num) {
//用來轉換成為千分位表示的數字用的
    var date_check=/^(([1-9]\d{0,3}|0)\-\d{2}\-\d{2})|(([1-9]\d{0,3}|0)\.\d{2}\.\d{2})|(([1-9]\d{0,3}|0)\/\d{2}\/\d{2})$/;
    if (date_check.test(num)){
        return num;
    }
    num = num + "";
    var re = /(-?\d+)(\d{3})/
    while (re.test(num)) {
        num = num.replace(re,"$1,$2")
    }
    return num;
}

var changeFile = function(){
    var $obj = $(this);
    var type = $obj.attr('type');
    var row_id = $obj.attr('row_id');
    if (type=='show'){
        $('.showFile_'+row_id).hide();
        $('.editFile_'+row_id).show();
        $obj.attr('type', 'edit')
    } else {
        $('.showFile_'+row_id).show();
        $('.editFile_'+row_id).hide();
        $obj.attr('type', 'show')
    }
}

var deleteFile = function(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var name = $obj.attr('neme');
    var msg = '您確定要刪除『'+name+'』檔案嗎？';
    if (confirm(msg)){
    	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "deleteFile", 
    		row_id: row_id
    		}, dataType:"json", success:function(json){
    			if (json['status']==true){
                    alert('刪除成功');
                    $('#File_tr_'+row_id).remove();
                } else {
                    alert(json['message']);
                }
        }});
    }
}

var editFile = function(){
    var $obj = $(this);
    var temp = $obj.attr('id').split('_');
    var field_name = temp[1];
    var field_id = temp[2];
    var value = $obj.attr('value');
    var old_value = $obj.attr('old_value');
    if (value == old_value){
        return false;
    }
    $.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "editFile", 
    	value: value, field_name: field_name, field_id: field_id
		}, dataType:"json", success:function(json){
			if (json['status']==true){
	            $obj.attr('value', value)
	            $obj.attr('old_value', value)
	            $('#showFile_'+ field_name +'_'+field_id).html(json['value'].replace(/\n/gi, '<br>'));
	        } else {
	            alert(json['message']);
	        }
    }});
}


var changeCityFile = function(){
    var $obj = $(this);
    var type = $obj.attr('type');
    var row_id = $obj.attr('row_id');
    if (type=='show'){
        $('.showFile_'+row_id).hide();
        $('.editCityFile_'+row_id).show();
        $obj.attr('type', 'edit')
    } else {
        $('.showFile_'+row_id).show();
        $('.editCityFile_'+row_id).hide();
        $obj.attr('type', 'show')
    }
}

var deleteCityFile = function(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var name = $obj.attr('neme');
    var msg = '您確定要刪除『'+name+'』檔案嗎？';
    if (confirm(msg)){
    	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "deleteCityFile", 
    		row_id: row_id
    		}, dataType:"json", success:function(json){
    			if (json['status']==true){
                    alert('刪除成功');
                    $('#File_tr_'+row_id).remove();
                } else {
                    alert(json['message']);
                }
        }});
    }
}

var editCityFile = function(){
    var $obj = $(this);
    var temp = $obj.attr('id').split('_');
    var field_name = temp[1];
    var field_id = temp[2];
    var value = $obj.attr('value');
    var old_value = $obj.attr('old_value');
    if (value == old_value){
        return false;
    }
    $.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "editCityFile", 
    	value: value, field_name: field_name, field_id: field_id
		}, dataType:"json", success:function(json){
			if (json['status']==true){
	            $obj.attr('value', value)
	            $obj.attr('old_value', value)
	            $('#showFile_'+ field_name +'_'+field_id).html(json['value'].replace(/\n/gi, '<br>'));
	        } else {
	            alert(json['message']);
	        }
    }});
}

var Show_ChaseTable = function(){
    var $obj = $(this);
    var action = $obj.attr('action');
    if (action=='Show'){
        $('#ChaseTable').fadeIn();
        $obj.attr('action', 'Hide');
    } else {
        $('#ChaseTable').fadeOut();
        $obj.attr('action', 'Show');
    }
    

}

var setChaseComplete = function(){
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var chase_id = $obj.attr('chase_id');
    
    $.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "setChaseComplete", 
    	project_id: project_id, chase_id: chase_id
		}, dataType:"json", success:function(json){
			if (json['status']==true){
	            if (json['complete']){
	                $obj.html('取消申請，我尚未填完!!');
	                alert('已通知填寫完成，通知後您可繼續進行修改');
	            } else {
	                $obj.html('我已填寫完畢!!');
	                alert('已取消申請');
	            }
	        } else {
	            alert(json['msg']);
	        }
    }});
}

var Show_Chase_Info = function(){
    var $obj = $(this);
    var chase_id = $obj.attr('chase_id');
    var field_name = $obj.attr('field_name');
    $('#Show_Chase_Info_'+field_name+'_'+chase_id).hide();
    $('#Edit_Chase_Info_'+field_name+'_'+chase_id).show().focus();
}

var Hide_Chase_Info = function(){
    var $obj = $(this);
    var chase_id = $obj.attr('chase_id');
    var field_name = $obj.attr('field_name');
    var table_name = $obj.attr('table_name');
    var value = $obj.attr('value');
    var old_value = $obj.attr('old_value');
    var input_type = $obj.attr('input_type');
    if (value != old_value){
        if (input_type=='float' && !(num_check.test(value)) && value!=''){
            alert('請填入數字');
            $obj.attr('value', old_value)
        } else if (input_type=='date' && !(date_check.test(value)) && value!=''){
            alert('請填入日期格式');
            $obj.attr('value', old_value)
        } else {
        	$.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "updateChaseInfo", 
        		chase_id: chase_id, field_name: field_name, table_name: table_name, value: value
        		}, dataType:"json", success:function(json){
        			if (json['status']==true){
                        var return_value = json['return_value'];
                        $obj.attr('value', return_value)
                        $obj.attr('old_value', return_value)
                        if (input_type=='float'){
                            $("#Show_Chase_Info_"+field_name+"_"+chase_id).html(TransformThousands(return_value));
                        } else {
                            $("#Show_Chase_Info_"+field_name+"_"+chase_id).html(return_value.replace(/\n/gi, '<br>'));
                        }
                    } else {
                        alert(json['msg']);
                        $obj.attr('value', old_value);
                    }
            }});
        }
    }
    $('#Show_Chase_Info_'+field_name+'_'+chase_id).show();
    $('#Edit_Chase_Info_'+field_name+'_'+chase_id).hide();
}

var updateChaseTotalMoney = function(){
    var $obj = $(this);
    var chase_id = $obj.attr('chase_id');
    var value = $obj.attr('choose_value');
    $.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "updateChaseTotalMoney", 
		chase_id: chase_id, value: value
		}, dataType:"json", success:function(json){
			if (json['status']==true){
	            var return_value = json['return_value'];
	            $("#total_money_value").html(TransformThousands(return_value));
	            if (value=='useTotalMoney'){
	                alert('此欄位現在與頁面下方之"標案資訊"部分同步，若有更動，須更動完成後再按一次重新同步');
	            }
	        }
    }});
}

var setChaseProjectClose = function(){
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var chase_id = $obj.attr('chase_id');
    var clase = $obj.attr('close');
    $.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "setChaseProjectClose", 
    	clase: clase, project_id: project_id, chase_id: chase_id
		}, dataType:"json", success:function(json){
			if (json['status']==true){
	            if (json['close']==true){
	                alert('已通知漁業署"本工程已完工"，等待確認中，感謝您的配合');
	                $obj.attr('close', 'True')
	                $obj.html('取消通知本工程已結案');
	            } else {
	                alert('已取消通知');
	                $obj.attr('close', 'False')
	                $obj.html('通知本工程已結案，不須繼續追蹤進度');
	            }
	        } else {
	            alert(json['msg']);
	        }
    }});
}

var makeFRCMCountyChaseExcel = function(){
    var $obj = $(this);
    var user_id = $obj.attr('user_id');
    var type = $obj.attr('print_type');
    $.ajax({ url:"/frcm/readjson/", type: "POST", data:{submit: "makeFRCMCountyChaseExcel", 
    	user_id: user_id, type: type
		}, dataType:"json", success:function(json){
			if (json['status']!=true){
	            var html = json["html"];
	            $dialog = $(html);
	            $dialog.dialog({
	                title: "尚未填寫完畢工程案",
	                width: 600,
	                height: 500,
	                buttons: {
	                    "關閉本視窗": function(){
	                        $dialog.dialog("close");
	                    }
	                }
	            });
	            $dialog.dialog("open");
	        } else {
	            window.open(json['url']);
	        }
    }});
}

var alertMSG = function(){
    var $obj = $(this);
    var msg = $obj.attr('title');
    alert(msg);
}

$(document).ready(function(){
    $('#Show_ChaseTable').click(Show_ChaseTable);
    $('#setChaseComplete').click(setChaseComplete);
    $('.Show_Chase_Info').click(Show_Chase_Info);
    $('.Hide_Chase_Info').blur(Hide_Chase_Info);
    $('.updateChaseTotalMoney').click(updateChaseTotalMoney);
    $('#setChaseProjectClose').click(setChaseProjectClose);
    $('.makeFRCMCountyChaseExcel').click(makeFRCMCountyChaseExcel);

    $('.importProject').click(importProject);
    $('.updateFRCMProject').change(updateFRCMProject);
    $('#getProject').click(getProject);
    $('.askToShareProject').click(askToShareProject);
    $('.regretToShareProject').click(regretToShareProject);
    $('.answerAskShare').click(answerAskShare);
    $('.sendBackProject').click(sendBackProject);
    $('.transferEngineer').click(transferEngineer);
    $('.editable').click(editProjectInfo);
    $('.changeFile').click(changeFile);
    $('.editFile').change(editFile);
    $('.deleteFile').click(deleteFile);
    $('.changeCityFile').click(changeCityFile);
    $('.editCityFile').change(editCityFile);
    $('.deleteCityFile').click(deleteCityFile);
    $('.alertMSG').click(alertMSG);

    $(".chooseDate").datepicker({
        buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png",
        dateFormat: "yy-mm-dd", beforeShow: function(){$(this).show();},onClose: editProjectInfo
    });
    $(".id_date").datepicker({
        buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png",
        dateFormat: "yy-mm-dd", beforeShow: function(){$(this).show();},onClose: editProjectInfo
    });

    $(".chooseChaseDate").datepicker({
        buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png",
        dateFormat: "yy-mm-dd", beforeShow: function(){$(this).show();},onClose: Show_Chase_Info
    });

});
