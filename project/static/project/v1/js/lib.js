var date_check=/^(([1-9]\d{0,3}|0)\-\d{2}\-\d{2})|(([1-9]\d{0,3}|0)\.\d{2}\.\d{2})|(([1-9]\d{0,3}|0)\/\d{2}\/\d{2})$/;
var num_check=/^[0-9]*$/;
var float_check=/^[1-9]d*.d*|0.d*[1-9]d*$/;

var checkRequisite = function(input){
    var $obj = input.target?$(this):$(input);//如果有 input.target 則表示為 Jquery 所觸發之事件
    if ($obj.val() == ''){
        $obj.css({border: "2px solid #A5B4B4", background: "#ffea45"});
        $('.submit').attr('disabled','disabled');
        $('#caution').show();
    } else {
        $obj.css({border: "2px solid #A5B4B4", background: "#C3FFF0"});
    }
    var all_reg = $('.requisite');
    var able = true;
    for(var i=0;i<all_reg.length;i++){
        if (all_reg[i]['value'] == ''){
            able = false
        }
    }
    if (able){
        $('.submit').removeAttr("disabled");
        $('#caution').hide();
    }
}

var checkInteger = function(){
    var $obj = $(this);
    if(!(num_check.test($obj.val()))){
        $obj.attr('value','');
        if ($obj.hasClass('requisite')){
            $obj.css({border: "2px solid #A5B4B4", background: "#ffea45"});
            $('.submit').attr('disabled','disabled');
            $('#caution').show();
        }
        alert('此欄位須為整數！');
    }
}

var checkFloat = function(){
    var $obj = $(this);
    var ov = $obj.attr('value');
    if(!(float_check.test($obj.val())) & !(num_check.test($obj.val()))){
        $obj.attr('value','');
        if ($obj.hasClass('requisite')){
            $obj.css({border: "2px solid #A5B4B4", background: "#ffea45"});
            $('.submit').attr('disabled','disabled');
            $('#caution').show();
        }
        alert('此欄位須為數字！');
    }
}

var checkDate = function(){
    var $obj = $(this);
    var ov = $obj.attr('value');
    if(!(date_check.test($obj.val()))){
        $obj.attr('value','');
        if ($obj.hasClass('requisite')){
            $obj.css({border: "2px solid #A5B4B4", background: "#ffea45"});
            $('.submit').attr('disabled','disabled');
            $('#caution').show();
        }
        alert('此欄位須為日期格式！');
    }
}


var addProject = function(){
    try{
        var name = $.needExist('name', '工作名稱');
        var bid_no = $('#bid_no').val();
        if(bid_no==''){
            bid_no = ''
        }
        var no = $('#no').val();
        var project_sub_type = $.needExist('project_sub_type', '計畫編號');
        var year = $.needExist('year', '年度');
        var VouchStatus = $('#status option:selected')
        if (VouchStatus.text() != '待審查'){
            var vouch_date = $('#vouch_date').val();
        } else if (VouchStatus.text() == '待審查'){
            var vouch_date = 'NotVouch';
        }
        var location = $('#location').val();
        var vouch_no = $('#vouch_no').val();
        var place = $.needExist('place', '縣市');
        var budget_type = $.needExist('budget_type', '預算別');
        var unit = $.needExist('unit', '執行機關');
        var undertake_type = $.needExist('undertake_type', '承辦方式');
        var up_plan = $.needExist('plan', '上層計畫');
        var status = $.needExist('status', '執行狀態');
        var self_contacter = $('#self_contacter').val();
        var self_contacter_phone = $('#self_contacter_phone').val();
        var self_contacter_email = $('#self_contacter_email').val();
        if (self_contacter_email){
            var self_contacter_email = $.checkEmailFormat('self_contacter_email', 'Email 格式不正確');
        }
        var self_charge = $('#self_charge').val();
        var local_contacter = $('#local_contacter').val();
        var local_contacter_phone = $('#local_contacter_phone').val();
        var local_contacter_email = $('#local_contacter_email').val();
        if (local_contacter_email){
            var local_contacter_email = $.checkEmailFormat('local_contacter_email', 'Email 格式不正確');
        }
        var local_charge = $('#local_charge').val();
        var contractor_contacter = $('#contractor_contacter').val();
        var contractor_contacter_phone = $('#contractor_contacter_phone').val();
        var contractor_contacter_email = $('#contractor_contacter_email').val();
        if (contractor_contacter_email){
            var contractor_contacter_email = $.checkEmailFormat('contractor_contacter_email', 'Email 格式不正確');
        }
        var contractor_charge = $('#contractor_charge').val();
        var project_memo = $('#project_memo').attr('value');
        alert(project_memo);
        var x_coord = $('#x_coord').val();
        var y_coord = $('#y_coord').val();
    } catch(er){
        return false;
    }

    var port = $('#port').val();
    var port_num = Number($('#addMoreFishingPort').attr('num'));
    var more_port = '';
    for (var i=0;i<port_num;i++){
        more_port += $('#port_'+String(i)).attr('value') + '_';
    }
    var format = true
    var date_check=/^(([1-9]\d{0,3}|0)\-\d{2}\-\d{2})|(([1-9]\d{0,3}|0)\.\d{2}\.\d{2})|(([1-9]\d{0,3}|0)\/\d{2}\/\d{2})$/;
    var num_check=/^[0-9]*$/;
    if(!(num_check.test(x_coord))){
        var message = 'X座標格式錯誤！';
        format = false;
        alert(message);
    }
    if(!(num_check.test(y_coord))){
        var message = 'Y座標格式錯誤！';
        format = false;
        alert(message);
    }
    if (!(name && year && place && unit && undertake_type && up_plan && project_sub_type && status )){
        var message = '請將資訊填寫完整！';
        format = false;
        alert(message);
    }
    if (format) {
    	$.ajax({ url:"/project/addproject/", type: "POST", data:{submit: "addProject", 
            name: name, no: no, x_coord: x_coord, y_coord: y_coord,
            bid_no: bid_no, year: year, vouch_date: vouch_date, vouch_no: vouch_no,
            project_sub_type: project_sub_type,
            place: place, unit: unit, port: port, budget_type: budget_type,
            undertake_type: undertake_type, plan: up_plan, status: status, location: location,
            self_contacter: self_contacter, self_contacter_phone: self_contacter_phone, self_charge: self_charge, self_contacter_email: self_contacter_email,
            local_contacter: local_contacter, local_contacter_phone: local_contacter_phone, local_charge: local_charge, local_contacter_email: local_contacter_email,
            contractor_contacter: contractor_contacter, contractor_contacter_phone: contractor_contacter_phone, contractor_charge: contractor_charge, contractor_contacter_email: contractor_contacter_email,
            project_memo: project_memo, more_port: more_port
    		}, dataType:"json", success:function(json){
    			if (json['status'] != true){
                    alert(json['message']);
                } else {
                    var message = '新增成功，是否繼續新增工程?';
                    if (confirm(message)){
                        window.location = '/project/addproject/';
                        window.open('/project/basic/' + json['project_id']);
                    } else {
                        window.location = '/project/search/';
                        window.open('/project/basic/' + json['project_id']);
                    }
                }
        }});
    }
    return false;
}



var updatePlanInfo = function(){
    var $obj = $(this);
    var plan_id = $obj.attr('plan_id');
    var old_plan_name = $('.view_plan_name_'+plan_id).attr('value');
    var old_plan_host = $('.view_plan_host_'+plan_id).attr('value');
    var old_plan_no = $('.view_plan_no_'+plan_id).attr('value');
    var old_plan_budget = $('.view_plan_budget_'+plan_id).attr('vns');
    var old_plan_note = $('.view_plan_note_'+plan_id).attr('value');
    if ($obj.attr('value') == 'want_edit'){
        $obj.attr('value', 'want_save')
        $('.view_plan_name_'+plan_id).hide();
        $('.view_plan_host_'+plan_id).hide();
        $('.view_plan_no_'+plan_id).hide();
        $('.view_plan_budget_'+plan_id).hide();
        $('.view_plan_note_'+plan_id).hide();
        $('.edit_plan_name_'+plan_id).fadeIn();
        $('.edit_plan_host_'+plan_id).fadeIn();
        $('.edit_plan_no_'+plan_id).fadeIn();
        $('.edit_plan_budget_'+plan_id).fadeIn();
        $('.edit_plan_note_'+plan_id).fadeIn();
        
    } else {
        var new_plan_name = $('.edit_plan_name_'+plan_id).attr('value');
        var new_plan_host = $('.edit_plan_host_'+plan_id).attr('value');
        var new_plan_no = $('.edit_plan_no_'+plan_id).attr('value');
        var new_plan_budget = $('.edit_plan_budget_'+plan_id).attr('value');
        var new_plan_note = $('.edit_plan_note_'+plan_id).attr('value');
        var change = false;
        if (new_plan_name != old_plan_name && old_plan_name != 'None'){
            change = true;
        }
        if (new_plan_host != old_plan_host){
            change = true;
        }
        if (new_plan_no != old_plan_no && old_plan_no != 'None'){
            change = true;
        }
        if (new_plan_budget != old_plan_budget && old_plan_budget != 'None'){
            change = true;
        }
        if (new_plan_note != old_plan_note && old_plan_note != 'None'){
            change = true;
        }
        if (change){
            var message = '你確定要修改計畫資訊嗎?';
            if (confirm(message)){
            	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updatePlanInfo", 
            		plan_id: plan_id, plan_name: new_plan_name, plan_host: new_plan_host,
                    plan_no: new_plan_no, plan_budget: new_plan_budget, plan_note: new_plan_note
            		}, dataType:"json", success:function(json){
            			if (json['status'] != true){
                            alert(json['message']);
                        } else {
                            alert('修改完成');
                            $('.edit_plan_name_'+plan_id).attr('value', json['plan_name'])
                            $('.view_plan_name_'+plan_id).attr('value', json['plan_name'])

                            if(json['plan_host'] == '----'){
                                $('.edit_plan_host_'+plan_id).attr('value', '')
                            } else {
                                $('.edit_plan_host_'+plan_id).attr('value', json['plan_host'])
                            }
                            $('.view_plan_host_'+plan_id).attr('value', json['plan_host'])
                            if(json['plan_no'] == '----'){
                                $('.edit_plan_no_'+plan_id).attr('value', '')
                            } else {
                                $('.edit_plan_no_'+plan_id).attr('value', json['plan_no'])
                            }
                            $('.view_plan_no_'+plan_id).attr('value', json['plan_no'])
                            if(json['plan_budget'] == '----'){
                                $('.edit_plan_budget_'+plan_id).attr('value', '')
                                $('.edit_plan_budget_'+plan_id).attr('orbn', '')
                            } else {
                                $('.edit_plan_budget_'+plan_id).attr('value', json['plan_budget'])
                                $('.edit_plan_budget_'+plan_id).attr('orbn', json['plan_budget'])
                            }
                            $('.view_plan_budget_'+plan_id).attr('value', json['plan_budget'])
                            if(json['plan_note'] == '----'){
                                $('.edit_plan_note_'+plan_id).attr('value', '')
                            } else {
                                $('.edit_plan_note_'+plan_id).attr('value', json['plan_note'])
                            }
                            $('.view_plan_note_'+plan_id).attr('value', json['plan_note'])
                            $('.view_plan_name_'+plan_id).html(json['plan_name']);
                            $('.view_plan_host_'+plan_id).html(json['plan_host']);
                            $('.view_plan_no_'+plan_id).html(json['plan_no']);
                            $('.view_plan_budget_'+plan_id).html(TransformThousands(json['plan_budget']));
                            $('.view_plan_note_'+plan_id).html(json['plan_note'].replace(/\n/gi, '<br>'));
                        }
                }});
            } else {
                $('.edit_plan_name_'+plan_id).attr('value', old_plan_name)
                $('.edit_plan_note_'+plan_id).attr('value', old_plan_note)
            }
        }
        $obj.attr('value', 'want_edit')
        $('.edit_plan_name_'+plan_id).hide();
        $('.edit_plan_host_'+plan_id).hide();
        $('.edit_plan_no_'+plan_id).hide();
        $('.edit_plan_budget_'+plan_id).hide();
        $('.edit_plan_note_'+plan_id).hide();
        $('.view_plan_name_'+plan_id).fadeIn();
        $('.view_plan_host_'+plan_id).fadeIn();
        $('.view_plan_no_'+plan_id).fadeIn();
        $('.view_plan_budget_'+plan_id).fadeIn();
        $('.view_plan_note_'+plan_id).fadeIn();
    }
    return false;
}

var setDefaultProject = function(){
    var $obj = $(this);
    var project_id = $obj.attr('value');
    var item = $('.checkbox_'+project_id);
    var checked = item.attr('checked');
    var check = item.attr('check');
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "setDefaultProject", 
    	project_id: project_id
		}, dataType:"json", success:function(json){
			if (json['status'] != true){
	            alert(json['message']);
	        } else {
	            if (check == 'check') {
	                $('#setDefaultProject_'+project_id).html('');
	                item.attr('check', '');
	            } else {
	                $('#setDefaultProject_'+project_id).html('<span class="style2">已追蹤</span>');
	                item.attr('check', 'check');
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

var updateProjectInfo = function(){
    var $project = $('.target_project');
    var $obj = $(this);
    var target_id = $obj.attr('id');
    var type = $obj.attr('type');
    var old_Info = $obj.attr('old_value');
    var new_Info = $obj.attr('value');
    var project_id = $project.attr('id');
//    var data = $obj.attr('type');
    var change = false;
    if (new_Info != old_Info){
            change = true;
    }
    if (change){
        var format = true;
        if ($obj.hasClass('integer')){
            var num_check=/^[0-9]*$/;
            if(new_Info == ''){
                var message = '不可為空值！';
                format = false;
            }
            if(!(num_check.test(new_Info))){
                var message = '金額格式錯誤！';
                format = false;
            }
        }
        if ($obj.hasClass('nullinteger')){
            var num_check=/^[0-9]*$/;
            if(!(num_check.test(new_Info))){
                var message = '金額格式錯誤！';
                format = false;
            }
        }
        if ($obj.hasClass('float')){
            var num_check=/^[0-9]*$/;
            var float_check=/^[1-9]d*.d*|0.d*[1-9]d*$/;
            if(new_Info == ''){
                format = true;
            } else if (!(float_check.test(new_Info)) && !(num_check.test(new_Info))){
                var message = '請輸入數字！';
                format = false;
            }
        }
        if ($obj.hasClass('percent')){
            var num_check=/^[0-9]*$/;
            var float_check=/^[1-9]d*.d*|0.d*[1-9]d*$/;
            if(new_Info == ''){
                format = true;
            } else if (!(float_check.test(new_Info)) && !(num_check.test(new_Info))){
                var message = '請輸入數字！';
                format = false;
            }
        }
        if ($obj.hasClass('coord')){
            var num_check=/^[0-9]*$/;
            if(!(num_check.test(new_Info))){
                var message = '座標為整數格式！';
                format = false;
            }
        }
        if ($obj.hasClass('chooseDate')){
            var date_check=/^(([1-9]\d{0,3}|0)\-\d{2}\-\d{2})|(([1-9]\d{0,3}|0)\.\d{2}\.\d{2})|(([1-9]\d{0,3}|0)\/\d{2}\/\d{2})$/;
            if(new_Info==''){
                format=true;
            }else if(!(date_check.test(new_Info))){
                var message = '日期格式錯誤！'
                format=false;
            }
        }
        if ($obj.hasClass('email')){
            var email_check=/^[a-z0-9][-a-z0-9\.]*@([a-z0-9-]+\.)+[a-z]+$/
            if(!(email_check.test(new_Info))){
                var message = 'Email 格式錯誤！'
                format=false;
            }
        }
        if ($obj.hasClass('need')){
            if(new_Info==''){
                var message = '此欄位為必填!';
                format = false;
            }
        }

        

        if ($('.target_project').attr('name') == 'ProjectBase'){
            if ($('.edit_name').val()==''){
                format=false;
                var message = '工作名稱不可為空值！';
            }
            if ($obj.hasClass('budget')){
                var dn = $obj.attr('dn');
                var field = $obj.attr('item');
                if (format){
                    var message = '你確定要修改此項工程基本資料嗎?';
                    if (confirm(message)){
                    	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updateBudgetInfo", 
                    		project_id: project_id, entry: field, new_info: new_Info, old_info: old_Info, dn: dn
                    		}, dataType:"json", success:function(json){
                    			if (json['status'] != true){
                                    $('.edit_' + target_id).attr('value', old_Info)
                                    alert(json['message']);
                                } else {
                                    if (type == 'select-one'){
                                        $('.edit_' + target_id).attr('value', new_Info)
                                        $('.edit_' + target_id).attr('old_value', new_Info)
                                        $('.show_' + target_id).html(json['return_name']);
                                    } else {
                                        $('.edit_' + target_id).attr('value', new_Info)
                                        $('.edit_' + target_id).attr('old_value', new_Info)
                                        $('.show_' + target_id).html(json['return_name'].replace(/\n/gi, '<br>'));
                                    }
                                    if ($obj.hasClass('indc')){
                                        var year = $obj.attr('year');
                                        var capital_sum = '0';
                                        var regular_sum = '0';
                                        var capital_money = Number($('.edit_capital_money_' + year).attr('value'));
                                        var capital_coordination = Number($('.edit_capital_coordination_' + year).attr('value'));
                                        var regular_money = Number($('.edit_regular_money_' + year).attr('value'));
                                        var regular_coordination = Number($('.edit_regular_coordination_' + year).attr('value'));
                                        capital_sum = capital_money + capital_coordination;
                                        regular_sum = regular_money + regular_coordination;
                                        $('#capital_sum_' + year).html(TransformThousands(capital_sum));
                                        $('#regular_sum_' + year).html(TransformThousands(regular_sum));
                                    }
                                    if ($obj.hasClass('indca')){
                                        var year = $obj.attr('year');
                                        var capital_a_sum = '0';
                                        var regular_a_sum = '0';
                                        var capital_project_use_money = Number($('.edit_capital_project_use_money_' + year).attr('value'));
                                        var capital_bid_surplus = Number($('.edit_capital_bid_surplus_' + year).attr('value'));
                                        var capital_co_adj = Number($('.edit_capital_co_adj_' + year).attr('value'));
                                        var regular_project_use_money = Number($('.edit_regular_project_use_money_' + year).attr('value'));
                                        var regular_bid_surplus = Number($('.edit_regular_bid_surplus_' + year).attr('value'));
                                        var regular_co_adj = Number($('.edit_regular_co_adj_' + year).attr('value'));

                                        capital_a_sum = capital_project_use_money + capital_bid_surplus + capital_co_adj;
                                        regular_a_sum = regular_project_use_money + regular_bid_surplus + regular_co_adj;
                                        $('#capital_adjust_sum_' + year).html(TransformThousands(capital_a_sum));
                                        $('#regular_adjust_sum_' + year).html(TransformThousands(regular_a_sum));
                                    }
                                }
                        }});
                    } else {
                        $('.edit_' + target_id).attr('value', old_Info)
                    }
                } else {
                    $('.edit_' + target_id).attr('value', old_Info)
                    $('.edit_' + target_id).attr('old_value', old_Info)
                    alert(message);
                }
            } else {
                if (format){
                    var message = '你確定要修改此項工程基本資料嗎?';
                    if (confirm(message)){
                        if(target_id == 'place'){
                            $('.show_x_coord').html('');
                            $('.show_y_coord').html('');
                            $('.edit_x_coord').attr('value','');
                            $('.edit_y_coord').attr('value','');
                            $('.edit_x_coord').attr('old_value','');
                            $('.edit_y_coord').attr('old_value','');
                        }
                        if($obj.hasClass('select_port')){
			    var item = $obj.attr('id');
                            var x = $('#' + item + ' option:selected').attr('twdx');
                            var y = $('#' + item + ' option:selected').attr('twdy');
                            if(x==''&&y==''){
                                $('.show_x_coord').html('');
                                $('.show_y_coord').html('');
                            } else {
                                $('.show_x_coord').html(x);
                                $('.show_y_coord').html(y);
                            }
                            $('.edit_x_coord').attr('value',x);
                            $('.edit_y_coord').attr('value',y);
                            $('.edit_x_coord').attr('old_value',x);
                            $('.edit_y_coord').attr('old_value',y);
                        }
                        $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updateProjectInfo", 
                        	project_id: project_id, entry: target_id, new_info: new_Info, old_info: old_Info, newx:x, newy:y
                    		}, dataType:"json", success:function(json){
                    			if (json['status'] != true){
                                    $('.edit_' + target_id).attr('value', old_Info);
                                    alert(json['message']);
                                } else {
                                    if (type == 'select-one'){
                                        $('.edit_' + target_id).attr('value', new_Info);
                                        $('.edit_' + target_id).attr('old_value', new_Info);
                                        $('.show_' + target_id).html(json['return_name']);
                                        if(target_id=='budget_type'){
                                            $('.rs_BudgetType').html(json['return_name']);
                                            if(json['return_name']=='公務預算'){
                                                $('.rs_BudgetType_bk').attr('bgcolor','#C3E1F0');
                                            }else{
                                                $('.rs_BudgetType_bk').attr('bgcolor','#E1B4F0');
                                            }
                                        }
                                        if(target_id=='year'){
                                            var dlt = Number(new_Info) - Number(old_Info);
                                            var year_tag = $('.year_tag');
                                            for(var i=0;i<year_tag.length;i++) {
                                                var ny = Number($(year_tag[i]).html()) + dlt;
                                                $(year_tag[i]).html(ny);
                                            }
                                        }
                                    } else {
                                        $('.edit_' + target_id).attr('value', new_Info);
                                        $('.edit_' + target_id).attr('old_value', new_Info);
                                        $('.show_' + target_id).html(json['return_name'].replace(/\n/gi, '<br>'));
                                    }
//                                    if (target_id=='undertake_type'){
//                                        var undertake_type = $obj.attr('value');
//                                        $.receiveJSON('/project/readjson/', {'submit': 'checkUndertakeType',
//                                        'undertake_type': undertake_type},
//                                        function(json){
//                                            if (json['status']!=true){
//                                                $('.show_local_charge').hide();
//                                                $('.show_local_contacter').hide();
//                                                $('.show_local_contacter_phone').hide();
//                                                $('.show_local_contacter_email').hide();
//                                            } else {
//                                                $('.show_local_charge').show();
//                                                $('.show_local_contacter').show();
//                                                $('.show_local_contacter_phone').show();
//                                                $('.show_local_contacter_email').show();
//                                            }
//                                        });
//                                    }
                                }
                        }});
                    } else {
                        $('.edit_' + target_id).attr('value', old_Info)
                    }
                } else {
                    $('.edit_' + target_id).attr('value', old_Info)
                    $('.edit_' + target_id).attr('old_value', old_Info)
                    alert(message);
                }
            }

        } else if ($('#pagemark').attr('page') == 'search'){
            var $obj = $(this);
            var project_id = $obj.attr('project_id');
            var field = $obj.attr('field');
            if (format){
                var message = '確定修改此項工程基本資料?';
                if (confirm(message)){
                	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "quickupdate", 
                		project_id: project_id, field: field, new_info: new_Info, old_Info: old_Info
                		}, dataType:"json", success:function(json){
                			if (json['status'] != true){
                                $('.edit_' + target_id).attr('value', old_Info)
                                alert(json['message']);
                            } else {
                                if (type == 'select-one'){
                                    $('.edit_' + target_id).attr('value', new_Info)
                                    $('.edit_' + target_id).attr('old_value', new_Info)
                                    $('.show_' + target_id).html(json['return_name']);
                                } else {
                                    $('.edit_' + target_id).attr('value', new_Info)
                                    $('.edit_' + target_id).attr('old_value', new_Info)
                                    $('.show_' + target_id).html(TransformThousands(json['return_name']).replace(/\n/gi, '<br>'));
                                }
                            }
                    }});
                } else {
                    $('.edit_' + target_id).attr('value', old_Info)
                }
            } else {
                $('.edit_' + target_id).attr('value', old_Info)
                $('.edit_' + target_id).attr('old_value', old_Info)
                alert(message);
            }

        } else if ($('.target_project').attr('name') == 'Bidinfo'){
            if (format) {
            	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "uBidinfo", 
            		project_id: project_id, entry: target_id, new_info: new_Info, old_Info: old_Info
            		}, dataType:"json", success:function(json){
            			if (json['status'] != true){
                            $('#error_message').html(json['project_info']);
                            alert(json['message']);
                        } else {
                            if (type == 'select-one'){
                                $('.edit_' + target_id).attr('value', new_Info)
                                $('.edit_' + target_id).attr('old_value', new_Info)
                                $('.show_' + target_id).html(json['return_name']);
                            } else {
                                $('.edit_' + target_id).attr('value', new_Info)
                                $('.edit_' + target_id).attr('old_value', new_Info)
                                if (json['spic_rz'] == true){
                                    new_Info = 0;
                                }
                                if (target_id == 'allot_rate'){
                                    if(new_Info == ''){
                                        new_Info = '----';
                                        
                                    }
                                    $('.show_' + target_id).html(new_Info);
                                } else {
                                    $('.show_' + target_id).html(TransformThousands(new_Info).replace(/\n/gi, '<br>'));
                                }
                            }
                        }
                }});
                var design_bid = $('.edit_design_bid').attr('value');
                var inspect_bid = $('.edit_inspect_bid').attr('value');
                var construction_bid = $('.edit_construction_bid').attr('value');
                var pollution = $('.edit_pollution').attr('value');
                var manage = $('.edit_manage').attr('value');
                var other_defray = $('.edit_other_defray').attr('value');
                var total = Number(design_bid) + Number(inspect_bid) + Number(construction_bid) + Number(pollution) + Number(manage) + Number(other_defray);
                total.toFixed(3);
                $('.edit_total').attr('value', total);
                if(total == 0){
                    total = '由上述項目加總';
                }
                $('.edit_total').html(TransformThousands(total));
            } else {
                $('.edit_' + target_id).attr('value', old_Info);
                $('.edit_' + target_id).attr('old_value', old_Info);
                if (target_id == 'design_bid' || target_id == 'inspect_bid' || target_id == 'construction_bid' || target_id == 'pollution' || target_id == 'manage' || target_id == 'other_defray'){
                    old_Info = 0;
                }
                if (target_id == 'allot_rate'){
                    old_Info = '----';
                }
                $('.show_' + target_id).html(TransformThousands(old_Info));
                alert(message);
            }

        } else if ($('.target_project').attr('name') == 'Milestone'){
            if (format){
            	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updateProjectInfo", 
            		project_id: project_id, entry: target_id, new_info: new_Info, old_Info: old_Info
            		}, dataType:"json", success:function(json){
            			if (json['status'] != true){
                            alert(json['message']);
                        } else {
                            if (type == 'select-one'){
                                $('.edit_' + target_id).attr('value', new_Info)
                                $('.edit_' + target_id).attr('old_value', new_Info)
                                $('.show_' + target_id).html(json['return_name']);
                            } else {
                                $('.edit_' + target_id).attr('value', new_Info)
                                $('.edit_' + target_id).attr('old_value', new_Info)
                                $('.show_' + target_id).html(json['return_name']);
                            }
                        }
                }});
            } else {
                $('.edit_' + target_id).attr('value', old_Info)
                $('.edit_' + target_id).attr('old_value', old_Info)
                $('.show_' + target_id).html(old_Info);
                alert(message);
            }

        } else if ($('.target_project').attr('name') == 'Fund'){
            if (format) {
                var rn = $obj.attr('rn');
                var rd = $obj.attr('rd');
                var entry = $obj.attr('field');
                $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updateFundInfo", 
                	rn: rn, rd: rd, entry: entry, new_info: new_Info
            		}, dataType:"json", success:function(json){
            			if (json['status'] != true){
                            alert(json['msg']);
                            $('.edit_' + target_id).attr('value', old_Info);
                            $('.edit_' + target_id).attr('old_value', old_Info);
                        } else {
                            if (type == 'select-one'){
                                $('.edit_' + target_id).attr('value', new_Info)
                                $('.edit_' + target_id).attr('old_value', new_Info)
                                $('.show_' + target_id).html(json['return_name']);
                            } else {
                                $('.edit_' + target_id).attr('value', new_Info)
                                $('.edit_' + target_id).attr('old_value', new_Info)
                                $('.show_' + target_id).html(TransformThousands(json['return_name']).replace(/\n/gi, '<br>'));
                            }
                            if(entry=='record_date'){
                                $('#delete_' + rn).attr('date', new_Info)
                            }
                            var $item = $('#record_' + rn );
                            $item.insertAfter($('#record_' + json['insert']));
                            for(i=0;i<json['id_list'].length;i++){
                                for(j=0;j<json['key_list'].length;j++){
                                    $('#s_' + json['key_list'][j] + '_' + json['id_list'][i]).html(TransformThousands(json['new_info'][json['id_list'][i]][json['key_list'][j]]));
                                }
                            }
                            $item.highlightFade('#99CCFF');
                        }
                }});
            } else {
                $('.edit_' + target_id).attr('value', old_Info)
                $('.edit_' + target_id).attr('old_value', old_Info)
                $('.show_' + target_id).html(TransformThousands(old_Info));
                alert(message);
            }

        } else if ($('.target_project').attr('name') == 'FundRecode'){
            if (format) {
                var dn = $('.target_project').attr('dn')
                $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updateFundRecode", 
                	project_id: project_id, new_info: new_Info, dn: dn, name: $obj.attr('id')
            		}, dataType:"json", success:function(json){
            			if (json['status'] != true){
                            alert(json['message']);
                            $('.edit_' + target_id).attr('value', old_Info);
                            $('.edit_' + target_id).attr('old_value', old_Info);
                        } else {
                            if ($obj.attr('id') == 'record_time'){
                                $('.edit_' + target_id).attr('value', new_Info);
                                $('.edit_' + target_id).attr('old_value', new_Info);
                                $('.show_' + target_id).html(new_Info);
                                $('#record_' + dn).html('<font color="#ff0000">' + json['title'] + '</font>');
                            } else {
                                $('.edit_' + target_id).attr('value', new_Info);
                                $('.edit_' + target_id).attr('old_value', new_Info);
                                $('#record_' + dn).html('<font color="#ff0000">' + json['title'] + '</font>');
                                $('.show_' + target_id).html(TransformThousands(json['return_name']).replace(/\n/gi, '<br>'));
                            }
                        }
                }});
            } else {
                $('.edit_' + target_id).attr('value', old_Info)
                $('.edit_' + target_id).attr('old_value', old_Info)
                $('.show_' + target_id).html(TransformThousands(old_Info));
                alert(message);
            }

        } else if ($('.target_project').attr('name') == 'Progress'){
            if (format) {
            	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updateProgress", 
            		project_id: project_id, entry: target_id, new_info: new_Info, dn: $obj.attr('dn'),
                    name: $obj.attr('name'), type: type
            		}, dataType:"json", success:function(json){
            			if (json['status'] != true){
                            alert(json['message']);
                            $('.edit_' + target_id).attr('value', old_Info);
                            $('.edit_' + target_id).attr('old_value', old_Info);
                        } else {
                            if (type == 'select-one'){
                                $('.edit_' + target_id).attr('value', new_Info)
                                $('.edit_' + target_id).attr('old_value', new_Info)
                                $('.show_' + target_id).html(json['return_name']);
                            } else {
                                $('.edit_' + target_id).attr('value', new_Info)
                                $('.edit_' + target_id).attr('old_value', new_Info)
                                $('.show_' + target_id).html(TransformThousands(json['return_name']).replace(/\n/gi, '<br>'));
                            }
                        }
                        if(json['col'] == 'Progress'){
                            progress_id = $obj.attr('dn');
                            progress_type = $obj.attr('dt');
                            $item = $('#' + progress_type + '_progress_' + progress_id );
                            $item.insertAfter($('#' + progress_type + '_progress_' + json['insert']));
                            $item.highlightFade('#99CCFF');
                        } else if(json['col'] == 'Appropriate'){
                            appropriate_id = $obj.attr('dn');
                            $item = $('#appropriate_' + appropriate_id );
                            $item.insertAfter($('#appropriate_' + json['insert']));
                            $item.highlightFade('#99CCFF');
                        }
                }});
            } else {
                $('.edit_' + target_id).attr('value', old_Info);
                $('.edit_' + target_id).attr('old_value', old_Info);
                if(old_Info=='' && $obj.hasClass('chooseDate')){
                    old_Info = '';
                } else if (old_Info==''){
                    old_Info = '----';
                }
                $('.show_' + target_id).html(old_Info);
                alert(message);
            }
        }
    }
    
    if ( target_id == 'name' ){
        $('#title').html(new_Info + ' 工程資訊');
    }
    $('.show_' + target_id).fadeIn();
    $('.edit_' + target_id).hide();
}

var cProjectNo = function(){
    var create = false;
    var $plan = $('#id_plan option:selected');
    var $year = $('#id_year');
    var $undertake = $('#id_undertake_type option:selected');

    if ( $plan.attr('value') != ''){
        create = true;
    }
    if (create){
        var project_no = '';
        var year_code = '';
        var plan_code = '';
        var project_serial = $plan.attr('serial');
        var project_serial_code = '';
        var undertake_code = $undertake.attr('text')[0];

        if ($year.attr('value').length == 2){
            year_code = '0' + $year.attr('value');
        } else {
            year_code = $year.attr('value');
        }
        if ($plan.attr('level') == $plan.attr('max_level')){
            plan_code = $plan.attr('up_code') + '-' + $plan.attr('code');
        } else {
            plan_code = $plan.attr('code') + '-000';
        }
        if (project_serial == 'None'){
            project_serial_code = '001';
        } else {
            new_project_serial = Number(project_serial) +1;
            if (new_project_serial < 10){
                project_serial_code = '00' + new_project_serial;
            } else if (new_project_serial < 100){
                project_serial_code = '0' + new_project_serial;
            } else {
                project_serial_code = new_project_serial;
            }
        }
        project_no = year_code + '-' + plan_code + '-' + project_serial_code + '-' + undertake_code;
        $('#id_no').attr('value', project_no);
        $('#show_no').html(project_no);
    }
}

var clearSearchInfo = function(){
    var url = $(this).attr('url');
    window.location = url;
}

var clearSearchAdvanceInfo = function(){
    window.location='/project/search/advanced/';
}

var clearBudgetSearchAdvanceInfo = function(){
    window.location='/project/rebudget/advanced/';
}

var clearBudgetInfo = function(){
    window.location='/project/rebudget/';
}

var makeStatistics = function(){
    var $obj = $(this);
    var select_year = $('#select_year').attr('value');
    if (select_year == '所有') {
        select_year = '0';
    }
    var select_unit = $('#select_unit').attr('value');
    if (!select_unit) {
        select_unit = '0';
    }
    var select_fishingport = $('#select_fishingport').attr('value');
    if (!select_fishingport) {
        select_fishingport = '0';
    }
    var befure_select_unit = $('#befure_select_unit').attr('befure_select_unit');
    if (befure_select_unit!=select_unit) {
        select_fishingport = '0';
    }
    var select_undertake_type = $('#select_undertake_type').attr('value');
    if (!select_undertake_type) {
        select_undertake_type = '0';
    }
    
    var type = $obj.attr('table_type');
    if (!type) {
        type = $('#type_id').attr('select_type');
    }
    window.location='/project/makestatistics/'
                    +'select_year:'+select_year
                    +'/type_id:'+type
                    +'/select_unit:'+select_unit
                    +'/select_undertake_type:'+select_undertake_type
                    +'/select_fishingport:'+select_fishingport
                    ;
}

var makeDownloadFile = function(){
    var $obj = $(this);
    var type = $obj.attr('value');
    if (type == '') {
         window.location='/project/makedownloadfile/';
    } else {
        window.location='/project/makedownloadfile/' + type + '/';
    }
}

var makeStatisticsProjects = function(){
    var $obj = $(this);
    var plan_id = $obj.attr('plan_id');
    if (!plan_id) {var plan_id = ''}
    var unit_id = $obj.attr('unit_id');
    if (!unit_id) {var unit_id = ''}
    var include_sub = $obj.attr('include_sub');
    if (!include_sub) {var include_sub = ''}
    var select_year = $obj.attr('select_year');
    if (!select_year) {var select_year = ''}
    var status_id = $obj.attr('status_id');
    if (!status_id) {var status_id = ''}
    var true_rate = $obj.attr('true_rate');
    if (!true_rate) {var true_rate = ''}
    var start_month = $obj.attr('start_month');
    if (!start_month) {var start_month = ''}
    var from_money = $obj.attr('from_money');
    if (!from_money) {var from_money = ''}
    var to_money = $obj.attr('to_money');
    if (!to_money) {var to_money = ''}
    var select_fishingport = $obj.attr('select_fishingport');
    if (!select_fishingport) {var select_fishingport = ''}
    var select_undertake_type = $obj.attr('select_undertake_type');
    if (!select_undertake_type) {var select_undertake_type = ''}
    
    $.ajax({ url:"/project/makestatisticsprojects/", type: "POST", data:{
    	plan_id: plan_id, unit_id: unit_id, include_sub: include_sub,
        select_year: select_year, status_id: status_id, true_rate: true_rate,
        start_month: start_month, from_money: from_money, to_money: to_money,
        select_fishingport: select_fishingport, select_undertake_type: select_undertake_type,
        name: $obj.attr('name'), type: type
		}, dataType:"json", success:function(json){
			var html = '<div class="flora" style="overflow: auto"><h2><table border="1" style="border-collapse: collapse">';
	        html += '<tr bgcolor="#CC99FF">';
	        html += '<td align="center" width="25"></td>';
	        html += '<td align="center" >年度</td>';
	        html += '<td align="center" >標案編號</td>';
	        html += '<td align="center" >工作名稱</td>';
	        html += '<td align="center" >計畫名稱</td>';
	        html += '<td align="center" >執行機關</td>';
	        html += '<td align="center" >工程狀態</td>';
	        html += '<td align="center" >縣市</td>';
	        html += '</tr>';

	        for (var i=0; i<json['projects'].length; i++){
	            html += '<tr bgcolor="#FFFFFF">';
	            html += '<td align="center">'+(i+1)+'</td>';
	            html += '<td align="center">'+json['projects'][i]['year']+'</td>';
	            html += '<td align="center"><a href="/project/reproject/'+json['projects'][i]['id']+'/" target="_blank">hdhdf'+json['projects'][i]['bid_no']+'</a></td>';
	            html += '<td align="center">'+json['projects'][i]['name']+'</td>';
	            html += '<td align="center">'+json['projects'][i]['plan']+'</td>';
	            html += '<td align="center">'+json['projects'][i]['unit']+'</td>';
	            html += '<td align="center">'+json['projects'][i]['status']+'</td>';
	            html += '<td align="center">'+json['projects'][i]['place']+'</td>';
	            html += '</tr>';
	        }
	        html += '</table></h2></div>';
	        $dialog = $(html);
	        $dialog.dialog({
	            title: '符合您條件的工程案',
	            width: 900,
	            height: 500,
	            buttons: {
	                '關閉本視窗': function(){
	                    $dialog.dialog('close');
	                }
	            }
	        });
	        $dialog.dialog('open');
    }});
}

var switchFR = function(){
    var $obj = $(this);
    if ($obj.attr('id') == 'show_fund_info'){
        $('#show_fund_info').addClass('active');
        $('#show_reserve_info').removeClass('active');
        $('#show_delete_ty_info').removeClass('active');
        $('#fund_info').show();
        $('#make_record').show();
        $('#reserve_info').hide();
        $('#delete_ty_info').hide();
    } else if ($obj.attr('id') == 'show_reserve_info'){
        $('#show_reserve_info').addClass('active');
        $('#show_fund_info').removeClass('active');
        $('#show_delete_ty_info').removeClass('active');
        $('#reserve_info').show();
        $('#fund_info').hide();
        $('#make_record').hide();
        $('#delete_ty_info').hide();
    } else if ($obj.attr('id') == 'show_delete_ty_info'){
        $('#show_delete_ty_info').addClass('active');
        $('#show_fund_info').removeClass('active');
        $('#show_reserve_info').removeClass('active');
        $('#delete_ty_info').show();
        $('#fund_info').hide();
        $('#make_record').hide();
        $('#reserve_info').hide();
    }
}

var switchCountType = function(){
    var $obj = $(this);
    var project = $('.target_project').attr('id');
    var count_type = $('input[name=count_type][@checked]').val();
    if ( count_type=='auto' ){
        message = '本署負擔及地方實支數將採比例計算，將會改變手動填寫的值，請確定是否改為自動計算？'
    } else if ( count_type=='write' ){
        message = '本署負擔及地方實支數將採手動填寫，將不再依比例自動計算，請確定是否改為手動填寫？'
    }
    if (confirm(message)) {
        if ( count_type=='auto' ){
            $('.show_auto').show();
            $('.show_write').hide();
            $('.switch_color').attr('bgcolor', "#FFCC33");
        } else if ( count_type=='write' ){
            $('.show_auto').hide();
            $('.show_write').show();
            $('.switch_color').attr('bgcolor', "#FFFF99");
        }
        $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "switchCountType", 
        	project: project, count_type: count_type
        	}, dataType:"json", success:function(json){
        }});
    } else {
        if ( count_type=='auto' ){
            $('#auto').attr('checked','');
            $('#write').attr('checked','checked');
        } else if ( count_type=='write' ){
            $('#auto').attr('checked','checked');
            $('#write').attr('checked','');
    }
    }

    return false;
}

var uploadPhoto = function(){
    if (!$('#file').attr('value')){
        alert('您尚未選擇檔案');
        return false;
    }
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var name = $('#name').attr('value');
    var memo = $('#memo').attr('value');
    if (!confirm('確定上傳 '+$('#file').attr('value')+' ?')){
        obj.value = '';
        return false;
    }
    $.ajaxFileUpload({
        url:'/project/photo/'+project_id+'/?name='+name+'&memo='+memo,
        async: true,
        fileElementId: 'file',
        dataType: 'json',
        success: function (json) {
            $('#name').attr('value', '')
            $('#memo').attr('value', '')
            $('#file').attr('value', '')
            var html = '';
            html += '<table id="PhotoTable_'+json['INFO']['id']+'">';
            html += '<tr><td align="center">第　'+json['count']+'　張</td></tr>';
            html += '<tr><td><table border="1" style="border-collapse: collapse"><tr>';
            html += '<td width="100" bgcolor="#FFFF99">相片名稱：</td>';
            html += '<td width="220" INFO="name_'+json['INFO']['id']+'" class="updatePhotoInfo_Show">';
            html += '<input id="Edit_name_'+json['INFO']['id']+'" class="updatePhotoInfo_Edit" style="display: none;"';
            html += 'photo_id="'+json['INFO']['id']+'" type="text" name="name" size="28"';
            html += 'old_value="'+json['INFO']['name']+'"';
            html += 'value="'+json['INFO']['name']+'">';
            html += '<a id="Show_name_'+json['INFO']['id']+'">'+json['INFO']['name']+'</a></td>';
            html += '<td width="100" bgcolor="#FFFF99">上傳時間：</td>';
            html += '<td>'+json['INFO']['uploadtime']+'</td>';
            html += '<td><img class="deleteProjectPhoto" project_id="'+json['INFO']['project_id']+'" photo_id="'+json['INFO']['id']+'" src="/media/images/delete.png" title="刪除相片"></td>';
            html += '</tr><tr><td bgcolor="#FFFF99" valign="top">備註：</td>';
            html += '<td colspan="4" INFO="memo_'+json['INFO']['id']+'" class="updatePhotoInfo_Show">';
            html += '<textarea id="Edit_memo_'+json['INFO']['id']+'" class="updatePhotoInfo_Edit"';
            html += 'style="display: none;" photo_id="'+json['INFO']['id']+'" cols="60" rows="3" name="memo"';
            html += 'old_value="'+json['INFO']['memo']+'">'+json['INFO']['memo']+'</textarea>';
            html += '<a id="Show_memo_'+json['INFO']['id']+'">'+json['INFO']['memo'].replace(/\n/gi, '<br>')+'</a></td></tr>';
            html += '<tr ><td colspan="5"><img height="480" width="640" src="/'+json['INFO']['url']+'" title="'+json['INFO']['name']+'"></td></tr>';
            html += '</table></td></tr></table><br>';
            html = $(html);
            html.insertAfter($('#PhotoTable_'+json['insert_place']));
            $('#PhotoCount').html(json['count']);
            $('.deleteProjectPhoto').click(deleteProjectPhoto);
            $('.updatePhotoInfo_Show').click(updatePhotoInfo_Show);
            $('.updatePhotoInfo_Edit').blur(updatePhotoInfo_Edit);
            alert('上傳成功');
        },
        error: function (json) {
            alert('上傳失敗');
        }
    });
    return false;
}

var deleteProjectPhoto = function(){
    if (!confirm('確定"永久"刪除此相片嗎?')){
        return false;
    }
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var photo_id = $obj.attr('photo_id');
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "deleteProjectPhoto", 
    	project: project, count_type: count_type
    	}, dataType:"json", success:function(json){
    		if (json['status']==true){
                $('#PhotoTable_'+photo_id).fadeOut();
                $('#PhotoCount').html(json['count']);
            } else {
                alert(json['message']);
            }
    }});
    return false;
}

var updatePhotoInfo_Show = function(){
    var $obj = $(this);
    var temp = $obj.attr('INFO').split('_');
    var field_name = temp[0];
    var photo_id = temp[1];
    $('#Show_'+field_name+'_'+photo_id).hide();
    $('#Edit_'+field_name+'_'+photo_id).fadeIn().focus();
    return false;
}

var updatePhotoInfo_Edit = function(){
    var $obj = $(this);
    var value = $obj.attr('value');
    var old_value = $obj.attr('old_value');
    var field_name = $obj.attr('name');
    var photo_id = $obj.attr('photo_id');
    var show = $('#Show_'+field_name+'_'+photo_id);
    var edit = $('#Edit_'+field_name+'_'+photo_id);
    if (value == old_value){
        show.fadeIn();
        edit.hide();
        return false;
    } else {
        if (confirm('確定要修改資訊嗎 ?')){
        	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updatePhotoInfo_Edit", 
        		value: value, field_name: field_name, photo_id: photo_id
        		}, dataType:"json", success:function(json){
        			if (json['status']==true){
                        edit.attr('value', value)
                        edit.attr('old_value', value)
                        show.html(value.replace(/\n/gi, '<br>'));
                        show.fadeIn();
                        edit.hide();
                    } else {
                        alert(json['message']);
                    }
        	}});
        } else {
            edit.attr('value', old_value)
        }
    }
    return false;
}

var makeStatistics_Include_sub = function(){
    $('.makeStatistics_Include_sub').hide();
    $('.makeStatistics_not_Include_sub').fadeIn();
    return false;
}

var makeStatistics_not_Include_sub = function(){
    $('.makeStatistics_Include_sub').fadeIn();
    $('.makeStatistics_not_Include_sub').hide();
    return false;
}

var checkVouch = function(){
    var status = $('#status option:selected')
    if (status.text() != '待審查'){
        $('.vouch_down').show();
        $('.vouch_yet').hide();
    } else if (status.text() == '待審查'){
        $('.vouch_down').hide();
        $('.vouch_yet').show();
    }
    return false;
}

var checkUndertake = function(){
    var undertake = $('#undertake_type option:selected')
    if (undertake.text() != '自辦'){
        $('.undertak_other').show();
        $('.undertak_self').hide();
    } else if (undertake.text() == '自辦'){
        $('.undertak_other').hide();
        $('.undertak_self').show();
    }
    return false;
}


var ShowandHidePlan = function(){
    var $obj = $(this);
    var lv = $obj.attr('value');
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "ShowandHidePlan", 
    	lv: lv
    	}, dataType:"json", success:function(json){
    		if (json['status']==true){
                $('#lv_controler_1').attr('height', '30').attr('width', '30').attr('border', "0")
                $('#lv_controler_2').attr('height', '30').attr('width', '30').attr('border', "0")
                $('#lv_controler_3').attr('height', '30').attr('width', '30').attr('border', "0")
                $('#lv_controler_4').attr('height', '30').attr('width', '30').attr('border', "0")
                $('#lv_controler_all').attr('height', '30').attr('width', '30').attr('border', "0")

                for (var i=0; i<json['show_plans'].length; i++){
                    $('#tr_'+json['show_plans'][i]).show();
                    $('#img_'+json['show_plans'][i]).attr('showorhide','show');
                }
                for (var i=0; i<json['hide_plans'].length;i++){
                    $('#tr_'+json['hide_plans'][i]).hide();
                    $('#img_'+json['hide_plans'][i]).attr('showorhide','hide');
                }

                
                $('#lv_controler_'+lv).attr('height', '50').attr('width', '50').attr('border', "1").attr('style', "border-collapse: collapse")

            } else {
                alert(json['message']);
            }
    }});
    return false;
}

var showandHideSubPlan = function(){
    var value = $(this).attr('value');
    if($(this).attr('showorhide') == 'show'){
        hideSubPlan(value);
        $(this).attr('showorhide','hide')
    }else{
        showSubPlan(value);
        $(this).attr('showorhide','show')
    }
}

var  showSubPlan = function(value){
	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "ShowSubPlan", 
		id: value
		}, dataType:"json", success:function(json){
			for (var i=0; i<json['show_subplans'].length; i++){
                $('#tr_'+json['show_subplans'][i]).show();
            };
	}});
}

var  hideSubPlan = function(value){
	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "HideSubPlan", 
		id: value
		}, dataType:"json", success:function(json){
	        for (var i=0; i<json['hide_subplans'].length; i++){
	            $('#tr_'+json['hide_subplans'][i]).hide();
	            $('#img_'+json['hide_subplans'][i]).attr('showorhide','hide');
	            };
	}});
}
var getFishingPort = function(){
    var $obj = $(this);

    $('#x_coord').attr('value', '');
    $('#y_coord').attr('value', '');
    if( $obj.attr('value')){
        var place = $obj.attr('value');
        $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "getFishingPort", 
        	place: place
    		}, dataType:"json", success:function(json){
    			if (json['status']==true){
                    $('#FishingPort').html(json['contents']);
                    $('.getcoord').change(getCoord);
                } else {
                    alert('');
                }
    	}});
    } else {
        var contents = ''
        contents += '<select id="port">'
        contents += '<option value="">--非港區--</option>'
        contents += '</select>'
        $('#FishingPort').html(contents)
    }

    return false;
}


var changeFishingPort = function(){
    var $obj = $(this);
    var place = $obj.attr('value');
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "changeFishingPort", 
    	place: place
		}, dataType:"json", success:function(json){
			if (json['status']==true){
	            $('.FishingPort').html(json['contents'])
	            $('.editable').click(editProjectInfo);
	            $('.update_edited').blur(updateProjectInfo);
	            $('.redaction').click(redactionProjectInfo);
	            $('.updateRedaction').blur(updateProjectRedaction);
	        } else {
	            alert('');
	        }
	}});


    return false;
}


//var makeFundRecord = function(){
//    var project = $('.target_project').attr('id');
//    var year = $('.target_project').attr('year');
//    var self_budget = $('.edit_self_budget').attr('value');
//    var local_budget = $('.edit_local_budget').attr('value');
//    var self_payout = $('.edit_self_payout').attr('value');
//    var local_payout = $('.edit_local_payout').attr('value');
//    var self_load = $('.edit_self_load').attr('value');
//    var self_past_budget = $('#self_past_budget').attr('value');
//    var local_past_budget = $('#local_past_budget').attr('value');
//    var payment = $('#payment').attr('value');
//    var self_unpay = $('#self_unpay').attr('value');
//    var local_unpay = $('#local_unpay').attr('value');
//    var self_surplus = $('#self_surplus').attr('value');
//    var local_surplus = $('#local_surplus').attr('value');
//
//    $.receiveJSON('/project/readjson/', {'submit': 'makeFundRecord',
//    'project': project, 'year': year, 'self_budget': self_budget, 'local_budget': local_budget,
//    'self_payout': self_payout, 'local_payout': local_payout, 'self_load': self_load,
//    'self_past_budget': self_past_budget, 'local_past_budget': local_past_budget,
//    'payment': payment, 'self_unpay': self_unpay, 'local_unpay': local_unpay,
//    'self_surplus': self_surplus, 'local_surplus': local_surplus},
//    function(json){
//        if (json['status']==true){
//            $dialog = $(json['contents']);
//            $dialog.dialog({
//                title: '金額資訊記錄設定',
//                width: 370,
//                height: 360,
//                buttons: {
//                    '設定完成關閉視窗': function(){
//                        $dialog.dialog('close');
//                        var message = '儲存成功，請至會計歷程檢視資料。';
//                        alert(message);
//                    }
//                }
//            })
//            $('.fundrecord_set').change(updateFundRecordSet);
//        } else {
//            alert('');
//        }
//    });
//    return false;
//}


var changeYearList = function(){
    var project = $('.target_project').attr('id');
    var year = $(this).val();
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "changeYearList", 
    	project: project, year: year
		}, dataType:"json", success:function(json){
			if (json['status']==true){
	            $('#fundrecord_year_table').html(json['contents']);
	            $('#fundrecord_table').hide()
	            $('#delete_button').hide()
	        } else {
	            alert('');
	        }
	}});
    return false;
}


//var deleteFundRecord = function(){
//    var project = $('.target_project').attr('id');
//    var year = $(this).val();
//    var dn = $('.target_project').attr('dn');
//    var message = '確定刪除記錄？'
//    if (confirm(message)){
//        $.receiveJSON('/project/readjson/', {'submit': 'deleteFundRecord',
//        'project': project, 'year': year, 'dn': dn},
//        function(json){
//            if (json['status']==true){
//                window.location = '/project/refundhistory/' + project;
//            } else {
//                alert('');
//            }
//        });
//    }
//
//    return false;
//}


//var updateFundRecordSet = function(){
//    var $obj = $(this);
//    var record = $obj.attr('dn');
//    var target = $obj.attr('id');
//    var value = $obj.val();
//
//
//    $.receiveJSON('/project/readjson/', {'submit': 'updateFundRecordSet',
//    'record': record, 'target': target, 'value': value},
//    function(json){
//    });
//
//    return false;
//}

var makeWorkExcel = function(){
    var $obj = $(this);
    var file_type = $obj.attr('file_type');
    
    if (file_type=='plan_progress'){
        var plans = '';
        var all_checkbox = $('input');
        for (var i=0 ;i<all_checkbox.length;i++){
            if ($(all_checkbox[i]).attr('type')=='checkbox'&&$(all_checkbox[i]).attr('checked')){
                plans += $(all_checkbox[i]).attr('value')+',';
            }
        }
        if (plans == ''){
            alert('請選擇計畫');
            return false;
        } else {
            var select_year = $('#select_year').attr('value');
            var select_month = $('#select_month').attr('value');
            var random = Math.random();
            window.location = '/project/makedownloadfile/'+file_type+'/?submit=makeWorkExcel&plans='+plans+'&select_year='+select_year+'&select_month='+select_month+'&random='+random+'&get_or_post=GET';
        }
    }
    $('#makeWorkExcel_mag').fadeIn();
    $('#makeWorkExcel_mag').fadeOut(8000);
}

var editBudget = function(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var field_name = $obj.attr('field_name');
    $('#show_'+field_name+'_'+row_id).hide();
    $('#edit_'+field_name+'_'+row_id).fadeIn();
    $('#edit_'+field_name+'_'+row_id).focus();
}

var setPlanToWorkExcel = function(){
    var $obj = $(this);
    var plan_id = $obj.attr('value');
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "setPlanToWorkExcel", 
    	plan_id: plan_id
		}, dataType:"json", success:function(json){
			if (json['status']==true){
	            for (var i=0; i<json['plans'].length;i++){
	                if ($obj.attr('checked')){
	                    $('.checkbox_'+json['plans'][i]).attr('checked', 'checked')
	                    $('#setPlanToWorkExcel_'+json['plans'][i]).attr('bgcolor', '#66FF66')
	                    if (i!=0) {
	                        $('.checkbox_'+json['plans'][i]).hide();
	                    }
	                } else {
	                    $('.checkbox_'+json['plans'][i]).attr('checked', '')
	                    $('#setPlanToWorkExcel_'+json['plans'][i]).attr('bgcolor', '')
	                    if (i!=0) {
	                        $('.checkbox_'+json['plans'][i]).show();
	                    }
	                }
	            }
	        } else {
	            alert(json['message']);
	        }
	}});
}


var showPoppingMemu = function(){
    var tar = $('#PoppingMemu');
    tar.css({
    'list-style-type': 'none',
    'position': 'absolute',
    'left': ($('#ShowPoppingMemu').position()['left'])+'px',
    'top': ($('#ShowPoppingMemu').position()['top']+23)+'px',
    'z-index': '200',
    'background-color': '#EFF6FA'
    });
    tar.show();
    tar.mouseout(hidePoppingMemu);
}

var hidePoppingMemu = function(){
    var tar = $('#PoppingMemu');
    tar.hide();
    
}

var FixPoppingMemu = function(){
    var $obj = $(this);
    var id = $obj.attr('id');
    var PoppingMemu = $('#PoppingMemu');
    var ShowPoppingMemu = $('#ShowPoppingMemu');
    if(id=='down'){
        PoppingMemu.removeClass('show_hided_table');
        ShowPoppingMemu.removeClass('show_hided_table');
//        ShowPoppingMemu.mouseout();
        $('#down').hide();
        $('#up').show();
        var tar = $('#PoppingMemu');
        tar.css({
        'list-style-type': 'none',
        'position': 'absolute',
        'left': ($('#ShowPoppingMemu').position()['left'])+'px',
        'top': ($('#ShowPoppingMemu').position()['top']+23)+'px',
        'z-index': '200',
        'background-color': '#EFF6FA'
        });
        tar.show();
        
    } else if(id=='up'){
        PoppingMemu.addClass('show_hided_table');
        ShowPoppingMemu.addClass('show_hided_table');
        $('#up').hide();
        $('#down').show();
        $('#PoppingMemu').hide();
    }
}

var hideInfoCol = function(){
    var $obj = $(this);
    var tar = $obj.attr('tar');

    $('#showed_' + tar).hide();
    $('#hidedn_' + tar).show();
    $('#hide_' + tar).hide();
    $('#show_' + tar).show();

    $('#' + tar).fadeOut();
    $('.' + tar).fadeOut();

}

var showInfoCol = function(){
    var $obj = $(this);
    var tar = $obj.attr('tar');

    $('#hidedn_' + tar).hide();
    $('#showed_' + tar).show();
    $('#show_' + tar).hide();
    $('#hide_' + tar).show();

    $('#' + tar).fadeIn();
    $('.' + tar).fadeIn();
    $('.' + tar).highlightFade('#99CCFF');

}

var transInfoCol = function(){
    var $obj = $(this);
    var id = $obj.attr('id');
    if(id=='Show'){
        $('.intable').show();
        $('.showTable').hide();
        $('.hideTable').show();
        $('.hidedn_img').hide();
        $('.showed_img').show();
    } else if(id=='Hide') {
        $('.intable').hide();
        $('.showTable').show();
        $('.hideTable').hide();
        $('.showed_img').hide();
        $('.hidedn_img').show();
    }
}

var searchPlanProjects = function(){
    var $obj = $(this);
    var id = $obj.attr('plan_id');
    random = Math.random();
    window.location = '/project/search/?submit=submit&sortBy=year&plan=' + id + '&project_sub_type=1&random='+random+'&get_or_post=GET';
}

var createPlanProjects = function(){
    var $obj = $(this);
    var id = $obj.attr('plan_id');
    window.location = '/project/addproject/plan_id:' + id + '/';
}

var updateProjectInfoByKeyup = function(event){
    var $obj = $(this);
    if (event.keyCode == 13){ //13 就是 [Enter] 的碼
        if ($obj.attr('type') == 'textarea'){
            return false;
        } else {
            $(this).blur();
        }
    }
}

var quickEdit = function(){
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var item = $obj.attr('item');
    $('.show_' + project_id + '_' + item).hide();
    $('.edit_' + project_id + '_' + item)
                    .fadeIn()
                    .focus();
}


function round2(value,num){
    return Math.round(value * Math.pow(10,num)) / Math.pow(10,num);
}

var recountPercent = function(){
    var self_budget = Number($('.edit_self_budget').attr('value'));
    var local_budget = Number($('.edit_local_budget').attr('value'));
    var self_percent = '0.0'
    var local_percent = '0.0'
    if(self_budget + local_budget != 0){
        self_percent = round2((self_budget*100 / (self_budget + local_budget)),2)
        local_percent = round2((local_budget*100 / (self_budget + local_budget)),2)
    }
    $('#self_percent').html(self_percent);
    $('#local_percent').html(local_percent);

    return false;
}

var makeChart = function(){
    var $obj = $(this);
    var tp = $obj.attr('tp');
    var table = $obj.attr('table');
    if (tp == 'makepie'){
        var title = '圓餅圖'
    } else if (tp == 'makeBar'){
        var title = '桿狀圖'
    } else if (tp == 'makePlot'){
        var title = '折線圖'
    }

    html = '<div class="flora" style="overflow: auto"><table>'
    html += '<img src="/project/';
    html += tp;
    html += '/';
    html += table;
    html += '/" title="" style="margin: 15px; float: left;" width="600">';
    html += '</table></div>';
    $dialog = $(html);
    $dialog.dialog({
        title: title,
        width: 670,
        height: 730,
        buttons: {
            '關閉本視窗': function(){
                $dialog.dialog('close');
            }
        }
    });
    $dialog.css({'z-index': '2000'});
    $dialog.dialog('open');
}


var getCoord = function(){
    var x = $('#port option:selected').attr('twdx');
    var y = $('#port option:selected').attr('twdy');
    $('#x_coord').attr('value', x);
    $('#y_coord').attr('value', y);
}


var updateCoord = function(){
    var x = $('#port option:selected').attr('twdx');
    var y = $('#port option:selected').attr('twdy');
    $('.show_x_coord').html(x);
    $('.show_y_coord').html(y);
}


var sumBar = function(){
    var $obj = $(this);
    var ct = $obj.attr('id');
    if(ct=='showSum'){
        $('#SumTable').fadeIn();
        $('#showSum').hide();
        $('#hideSum').show();
    } else {
        $('#SumTable').fadeOut();
        $('#hideSum').hide();
        $('#showSum').show();
    }
}


var balanceBudget = function(){
    
    var $obj = $(this);
    var bt = $obj.attr('bt');
    var limit = Number($obj.attr('value'));
    var now = Number($('#now_' + bt).attr('nv'));
    var balance = TransformThousands(limit - now);
    if(balance==0){
        balance = '';
    }
    $('#ans_' + bt).html(balance);
}


var jsGetChart = function(){
    var $obj = $(this);
    var tp = $obj.attr('tp');
    var tf = $obj.attr('tf');
    var mark = $obj.attr('mark');
    var tar = $obj.attr('tar');
    var tag = $('.tag');
    var num = $('.' + tar);

    var tag_list = '';
    for(var i=0;i<tag.length;i++) {
        tag_list += '+';
        tag_list += $(tag[i]).attr('tag');
    }
    var num_list = '';
    for(var i=0;i<num.length;i++) {
        num_list += '+';
        num_list += $(num[i]).attr('num');
    }
    
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "jsGetChart", 
    	mark: mark, tag_list: tag_list, num_list: num_list, tar: tar, tp: tp, tf: tf
		}, dataType:"json", success:function(json){
			if (json['status']==true){
	            html = '<div class="flora" style="overflow: auto"><table>';
	            html += '<img src="/project/';
	            html += tp;
	            html += '/';
	            html += json['chart_cache_name'];
	            html += '/" title="" style="margin: 15px; float: left;" width="600">';
	            html += '</table></div>';
	            $dialog = $(html);
	            $dialog.dialog({
	                title: mark,
	                width: 670,
	                height: 730,
	                buttons: {
	                    '關閉本視窗': function(){
	                        $dialog.dialog('close');
	                    }
	                }
	            });
	            $dialog.css({'z-index': '2000'});
	            $dialog.dialog('open');

	        } else {
	            alert('此計畫無工程資料！');
	        }
	}});
}


var showProjectMemo = function(){
    var $obj = $(this);
    var memo = $obj.attr('memo');
    var mark = $obj.attr('mark');
    html = '<div class="flora" style="overflow: auto"><table><tr><td>';
    html += memo;
    html += '</td></tr></table></div>';
    $dialog = $(html);
    $dialog.dialog({
        title: mark + '備註事項',
        width: 750,
        height: 300,
        buttons: {
            '關閉本視窗': function(){
                $dialog.dialog('close');
            }
        }
    });
    $dialog.css({'z-index': '2000'});
    $dialog.dialog('open');

}

var selectYearByChage = function(){
    var $obj = $(this);
    var year = $obj.attr('value');
    var month = $('#select_month');
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "selectYearByChage", 
    	year: year
		}, dataType:"json", success:function(json){
			month.html(json['html']);
	}});
}


var deleteProject = function(){
    var $obj = $(this);
    var project_id = $obj.attr('p_id');
    var project_name = $obj.attr('p_name');
    var message = '您是否確定刪除『' + project_name + '』工程';
    if (confirm(message)){
    	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "deleteProject", 
    		project_id: project_id
    		}, dataType:"json", success:function(json){
    			if (json['status']==true){
                    $('#tr_project_'+project_id).remove();
                    alert('刪除成功，若要救回此工程請至『工程回收區』搜尋!!');
                } else {
                    alert(json['message']);
                }
    	}});
    }
}


var recoverProject = function(){
    var $obj = $(this);
    var project_id = $obj.attr('p_id');
    var project_name = $obj.attr('p_name');
    var message = '您是否確復原『' + project_name + '』工程';
    if (confirm(message)){
    	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "recoverProject", 
    		project_id: project_id
    		}, dataType:"json", success:function(json){
    			if (json['status']==true){
                    $('#tr_project_'+project_id).remove();
                    alert('復原成功，請回 搜尋管考工程 頁面搜尋!!');
                } else {
                    alert(json['message']);
                }
    	}});
    }
}


var addMoreFishingPort = function(){
    var $obj = $(this);
    var num = Number($obj.attr('num'));
    var inedit = $obj.attr('inedit');
    var project_id = $obj.attr('project_id');
    $obj.attr('num', String(num+1));
    
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "addMoreFishingPort", 
    	num: num, inedit: inedit, project_id: project_id
		}, dataType:"json", success:function(json){
			if (json['status']==true){
	            $(json['html']).insertBefore($('#insertPortPlace'));
	            $('#place_' + String(num)).change(getMoreFishingPortInList);
	            $('.editable').click(editProjectInfo);
	            $('.update_edited').blur(updateProjectInfo);
	            $('.deleteFishingPort').click(deleteFishingPort);
	            $('.redaction').click(redactionProjectInfo);
	            $('.updateRedaction').blur(updateProjectRedaction);
	        } else {
	            alert(json['message']);
	        }
	}});
    $('.edit_' + target).hide();
}


var getMoreFishingPortInList = function(){
    var $obj = $(this);
    var num = $obj.attr('id').split('_')[1];
    if( $obj.attr('value')){
        var place = $obj.attr('value');
        $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "getFishingPort", 
        	place: place, num: num
    		}, dataType:"json", success:function(json){
    			if (json['status']==true){
                    $('#FishingPort_' + num).html(json['contents']);
                    $('.deleteFishingPort').click(deleteFishingPort);
                } else {
                    alert(json['message']);
                    html = $(html);
                    var item = $('#' + json['plan_id'] + '_' +json['insert']);
                    html.insertAfter(item);
                    $('.editable').click(editProjectInfo);
                    $('.update_planbudget').blur(updatePlanBudget);
                    $('.deletePlanBudget').click(deletePlanBudget);
                    alert('已新增紀錄');
                }
    	}});
    } else {
        var contents = ''
        contents += '<select id="port_' + num + '">'
        contents += '<option value="">--非港區--</option>'
        contents += '</select>'
        $('#FishingPort' + num).html(contents)
    }
    return false;
}


var deleteFishingPort = function(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var inedit = $obj.attr('inedit');
    if(inedit){
    	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "deleteFishingPort", 
    		row_id: row_id
    		}, dataType:"json", success:function(json){
    			if (json['status']==true){
                    $('#tr_fishingport_' + row_id).remove();
                } else {
                    alert(json['message']);
                }
    	}});
    } else {
        $('#br_' + row_id).remove();
        $('#place_' + row_id).remove();
        $('#FishingPort_' + row_id).remove();
        $('#delete_Port_' + row_id).remove();
    }
    return false;
}


var checkBN = function(){
    var $obj = $(this);
    var bn = $obj.attr('value');
    var orbn = $obj.attr('orbn');
    if ((!float_check.test(bn)) && (bn != '')){
        $obj.attr('value', orbn);
        alert('請填入數字!');
    }
}


var updatePlanBudget = function(){
    var $obj = $(this);
    var planbudget = $obj.attr('planbudget');
    var field = $obj.attr('field');
    var old_Info = $obj.attr('old_value');
    var new_Info = $obj.attr('value');
    var target = $obj.attr('id');
    var type = $obj.attr('type');
    var change = false;
    var format = true;
    if (new_Info != old_Info){
        change = true;
    }
    if (change){
        if ($obj.hasClass('float')){
            var float_check=/^[1-9]d*.d*|0.d*[1-9]d*$/;
            if (!(float_check.test(new_Info)) && new_Info != ''){
                format = false;
                var message = '請輸入數字！';
            }
        }
        if (format){
        	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updatePlanBudget", 
        		planbudget: planbudget, field: field, new_info: new_Info, old_info: old_Info
        		}, dataType:"json", success:function(json){
        			if (json['status'] != true){
                        $('.edit_' + target).attr('value', old_Info);
                        alert(json['message']);
                    } else {
                        if (type == 'select-one'){
                            $('.edit_' + target).attr('value', new_Info);
                            $('.edit_' + target).attr('old_value', new_Info);
                            $('.show_' + target).html(json['return_name']);
                        } else {
                            $('.edit_' + target).attr('value', new_Info)
                            $('.edit_' + target).attr('old_value', new_Info)
                            $('.show_' + target).html(TransformThousands(json['return_name']).replace(/\n/gi, '<br>'));
                        }
                        $('#total_' + planbudget).html(TransformThousands(json['total']));
                        $('#capital_total_' + planbudget).html(TransformThousands(json['ctotal']));
                        $('#regular_total_' + planbudget).html(TransformThousands(json['rtotal']));
                        var $item = $('#' + json['plan'] + '_' + planbudget );
                        $item.insertAfter($('#' + json['plan'] + '_' + json['insert'] ));
                        $item.highlightFade('#99CCFF');
                    }
        	}});
        } else {
            $('.edit_' + target).attr('value', old_Info);
            alert(message);
        }
    }else {
        $('.edit_' + target).attr('value', old_Info);
        $('.edit_' + target).attr('old_value', old_Info);
    }
    $('.show_' + target).fadeIn();
    $('.edit_' + target).hide();
}


var addPlanBudget = function(){
    var $obj = $(this);
    var plan = $obj.attr('plan');
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "addPlanBudget", 
    	plan: plan
		}, dataType:"json", success:function(json){
			if (json['status'] != true){
            } else {
                var html = json['content'];
                html = $(html);
                var item = $('#' + json['plan_id'] + '_' +json['insert']);
                html.insertAfter(item);
                $('.editable').click(editProjectInfo);
                $('.update_planbudget').blur(updatePlanBudget);
                $('.deletePlanBudget').click(deletePlanBudget);
                alert('已新增紀錄');
            }
	}});
    return false;
}


var deletePlanBudget = function(){
    var $obj = $(this);
    var pb = $obj.attr('dn');
    var message = '確定刪除此紀錄？';
    if(confirm(message)) {
    	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "deletePlanBudget", 
    		pb: pb
    		}, dataType:"json", success:function(json){
    			if (json['status'] != true){
                    alert(json['message']);
                } else {
                    var $item = $('#' + json['plan'] + '_' + pb);
                    $item.remove();
                }
    	}});
    }
    return false;
}


var switchDisplay = function(){
    var $obj = $(this);
    var tables = $('.BudgetsTable');
    if ($obj.hasClass('sall')){
        $obj.hide();
        $('.hall').show();
        tables.fadeIn();
        $('.hidden').hide();
        $('.showed').show();
    } else if ($obj.hasClass('hall')){
        $obj.hide();
        $('.sall').show();
        tables.fadeOut();
        $('.showed').hide();
        $('.hidden').show();
    }
}


var singleSwitch = function(){
    var $obj = $(this);
    var plan = $obj.attr('plan');
    if ($obj.hasClass('showed')){
        $('.showed_' + plan).hide();
        $('.hidden_' + plan).show();
        $('.table_' + plan).fadeOut();
    } else if ($obj.hasClass('hidden')){
        $('.hidden_' + plan).hide();
        $('.showed_' + plan).show();
        $('.table_' + plan).fadeIn();
    }
}


var addProjectFund = function(){
    var $obj = $(this);
    var project = $obj.attr('project');
    var year = $obj.attr('year');
    $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "addProjectFund", 
    	project: project, year: year
		}, dataType:"json", success:function(json){
			if (json['status'] != true){
            } else {
                var html = json['content'];
                html = $(html);
                var item = $('#record_' + json['insert']);
                html.insertAfter(item);
                $('.editable').click(editProjectInfo);
                $('.update_edited').blur(updateProjectInfo);
                $('.redaction').click(redactionProjectInfo);
                $('.updateRedaction').blur(updateProjectRedaction);
                $('.deleteProjectFund').click(deleteProjectFund);
                $('.hightlightFundrecord').mouseover(hightlightFundrecord);
                $('.hightlightFundrecord').mouseout(unhightlightFundrecord);
                $('.chooseDate').each(function() {
                    $(this).datepicker();
                });
                $('.date_field').each(function() {
                    $(this).datepicker();
                });
                $('#id_date').datepicker();
                alert('已新增紀錄');
            }
	}});
    return false;
}


var deleteProjectFund = function(){
    var $obj = $(this);
    var rn = $obj.attr('rn');
    var date = $obj.attr('date');
    if(date == ''){
        var msg = '確定刪除此紀錄？';
    } else {
        var msg = '確定刪除' + date + '之紀錄？';
    }
    if(confirm(msg)) {
    	$.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "deleteProjectFund", 
        	project: project, year: year
    		}, dataType:"json", success:function(json){
    			if (json['status'] != true){
                    alert(json['message']);
                } else {
                    for(i=0;i<json['id_list'].length;i++){
                        for(j=0;j<json['key_list'].length;j++){
                            $('#s_' + json['key_list'][j] + '_' + json['id_list'][i]).html(TransformThousands(json['new_info'][json['id_list'][i]][json['key_list'][j]]));
                        }
                    }
                    var $item = $('#record_' + rn);
                    $item.remove();
                }
    	}});
    }
    return false;
}

var hightlightFundrecord = function(){
    var $obj = $(this);
    var id = $obj.attr('id').split('_')[1];
    var $item = $('#record_' + id);
    $item.attr('bgcolor', '#F0C3F0')
}

var unhightlightFundrecord = function(){
    var $obj = $(this);
    var id = $obj.attr('id').split('_')[1];
    var $item = $('#record_' + id);
    $item.attr('bgcolor', '')
}


var redactionProjectInfo = function(){
    var $obj = $(this);
    var target_id = $obj.attr('id');
    $('.show_' + target_id).hide();
    $('.edit_' + target_id)
                    .fadeIn()
                    .focus();
}

var updateProjectRedaction = function(){
    var $obj = $(this);
    var $project = $(".target_project");
    var project_id = $project.attr('id');
    var type = $obj.attr('type');
    var field = $obj.attr("editing");
    var category = $obj.attr("category");
    var old_Info = $obj.attr('old_value');
    var new_Info = $obj.attr('value');
    var change = false;
    if (new_Info != old_Info){
            change = true;
    }
    if (change){
        var format = true;
        if ($obj.hasClass('integer')){
            var num_check=/^[0-9]*$/;
            if(new_Info == ''){
                var message = '不可為空值！';
                format = false;
            }
            if(!(num_check.test(new_Info))){
                var message = '金額格式錯誤！';
                format = false;
            }
        }
        if ($obj.hasClass('nullinteger')){
            var num_check=/^[0-9]*$/;
            if(!(num_check.test(new_Info))){
                var message = '金額格式錯誤！';
                format = false;
            }
        }
        if ($obj.hasClass('float')){
            var num_check=/^[0-9]*$/;
            var float_check=/^[1-9]d*.d*|0.d*[1-9]d*$/;
            if(new_Info == ''){
                format = true;
            } else if (!(float_check.test(new_Info)) && !(num_check.test(new_Info))){
                var message = '請輸入數字！';
                format = false;
            }
        }
        if ($obj.hasClass('percent')){
            var num_check=/^[0-9]*$/;
            var float_check=/^[1-9]d*.d*|0.d*[1-9]d*$/;
            if(new_Info == ''){
                format = true;
            } else if (!(float_check.test(new_Info)) && !(num_check.test(new_Info))){
                var message = '請輸入數字！';
                format = false;
            }
        }
        if ($obj.hasClass('coord')){
            var num_check=/^[0-9]*$/;
            if(!(num_check.test(new_Info))){
                var message = '座標為整數格式！';
                format = false;
            }
        }
        if ($obj.hasClass('chooseDate')){
            var date_check=/^(([1-9]\d{0,3}|0)\-\d{2}\-\d{2})|(([1-9]\d{0,3}|0)\.\d{2}\.\d{2})|(([1-9]\d{0,3}|0)\/\d{2}\/\d{2})$/;
            if(new_Info==''){
                format=true;
            }else if(!(date_check.test(new_Info))){
                var message = '日期格式錯誤！'
                format=false;
            }
        }
        if ($obj.hasClass('email')){
            var email_check=/^[a-z0-9][-a-z0-9\.]*@([a-z0-9-]+\.)+[a-z]+$/
            if(!(email_check.test(new_Info))){
                var message = 'Email 格式錯誤！'
                format=false;
            }
        }

        if (category == 'ProjectBase'){
            if ($('.edit_name').val()==''){
                format=false;
                var message = '工作名稱不可為空值！';
            }
            if (format){
                var message = '你確定要修改此項工程基本資料嗎?';
//                if (confirm(message)){
                if(field == 'place'){
                    $('.show_x_coord').html('');
                    $('.show_y_coord').html('');
                    $('.edit_x_coord').attr('value','');
                    $('.edit_y_coord').attr('value','');
                    $('.edit_x_coord').attr('old_value','');
                    $('.edit_y_coord').attr('old_value','');
                }
                if($obj.hasClass('select_port')){
                    var item = $obj.attr('editing');
                    var x = $('#select_' + item + ' option:selected').attr('twdx');
                    var y = $('#select_' + item + ' option:selected').attr('twdy');
                    if(x==''&&y==''){
                        $('.show_x_coord').html('');
                        $('.show_y_coord').html('');
                    } else {
                        $('.show_x_coord').html(x);
                        $('.show_y_coord').html(y);
                    }
                    $('.edit_x_coord').attr('value',x);
                    $('.edit_y_coord').attr('value',y);
                    $('.edit_x_coord').attr('old_value',x);
                    $('.edit_y_coord').attr('old_value',y);
                }
                $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updateProjectInfo", 'project_id': project_id, 'entry': field, 'new_info': new_Info, 'old_info': old_Info, 'newx':x, 'newy':y}, dataType:"json", success:function(data){
                    if (data['status'] != true){

                        $('.edit_' + field).attr('value', old_Info);
                        alert(data['message']);
                    } else {
                        if (type == 'select-one'){
                            $('.edit_' + field).attr('value', new_Info);
                            $('.edit_' + field).attr('old_value', new_Info);
                            $('.show_' + field).html(data['return_name']);
                            if(field=='budget_type'){
                                $('.rs_BudgetType').html(data['return_name']);
                                if(data['return_name']=='公務預算'){
                                    $('.rs_BudgetType_bk').attr('bgcolor','#C3E1F0');
                                }else{
                                    $('.rs_BudgetType_bk').attr('bgcolor','#E1B4F0');
                                }
                            }
                            if(field=='year'){
                                var dlt = Number(new_Info) - Number(old_Info);
                                var year_tag = $('.year_tag');
                                for(var i=0;i<year_tag.length;i++) {
                                    var ny = Number($(year_tag[i]).html()) + dlt;
                                    $(year_tag[i]).html(ny);
                                }
                            }
                            if(field=='plan'){
                                $("#plan_no").html(data["return_extr"]);
                            }
                            if(field=='project_type' || field=='place' ){
                                $("#sub_location_area").html($('<table><span id="insertSubLocation"></span></table>'));
                            }
                            if(field=='project_type'){
                                $("#project_sub_type").html($(data["return_extr"]));
                                $("#type_other").hide();
                                $('.redaction').click(redactionProjectInfo);
                                $('.updateRedaction').blur(updateProjectRedaction);
                            }
                            if(field=='project_sub_type'){
                                if(data["return_extr"]){
                                    $("#type_other").show();
                                }else{
                                    $("#type_other").hide();
                                }
                            }
                        } else {
                            $('.edit_' + field).attr('value', new_Info);
                            $('.edit_' + field).attr('old_value', new_Info);
                            $('.show_' + field).html(data['return_name'].replace(/\n/gi, '<br>'));
                        }
                    }
                }});
//                } else {
//                    $('.edit_' + field).attr('value', old_Info)
//                }
            } else {
                $('.edit_' + field).attr('value', old_Info)
                $('.edit_' + field).attr('old_value', old_Info)
                alert(message);
            }
        } else if (category == 'ProjectBid'){
            if (format) {
                if (field == 'pcc_no'){
                    $("#PCCSYNCINFO").hide();
                    $("#SYNCMESSAGE").show();
                }
                $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "uBidinfo", 'project_id': project_id, 'entry': field, 'new_info': new_Info, 'old_Info': old_Info}, dataType:"json", success:function(data){
                    if (data['status'] != true){
                        $('#error_message').html(data['project_info']);
                        alert(data['message']);
                        $('.edit_' + field).attr('value', old_Info);
                        $("#SYNCMESSAGE").hide();
                        $("#PCCSYNCINFO").show();
                    } else {
                        if (type == 'select-one'){
                            $('.edit_' + field).attr('value', new_Info);
                            $('.edit_' + field).attr('old_value', new_Info);
                            $('.show_' + field).html(data['return_name']);
                        } else {
                            $('.edit_' + field).attr('value', data['return_name']);
                            $('.edit_' + field).attr('old_value', data['return_name']);
                            if (field == 'allot_rate'){
                                $('.show_' + field).html(data['return_name']);
                                $('.show_' + field).attr("value", data['return_name']);
                            }else if(field == 'no'){
                                if(data['return_name']==""){
                                    $("#getAccoutingDataButton").hide();
                                    $("#AccoutingDataNote").show();
                                }else{
                                    $("#AccoutingDataNote").hide();
                                    $("#getAccoutingDataButton").show();
                                }
                                $('.show_' + field).html(data['return_name']);
                                $('.show_' + field).attr("value", data['return_name']);
                            }else if (field == 'pcc_no'){
                                $('.show_' + field).html(data['return_name']);
                                if(data['return_name']!=""){
                                    var message = "由標案管理系統中比對符合的工程為『" + data['extr'] + "』，請確認是否正確？";
                                    if (!confirm(message)){
                                        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "uBidinfo", 'project_id': project_id, 'entry': field, 'new_info': '', 'old_Info': ''}, dataType:"json", success:function(data){
                                            $('.edit_' + field).attr('value', data['return_name']);
                                            $('.edit_' + field).attr('old_value', data['return_name']);
                                            $('.show_' + field).attr("value", data['return_name']);
                                            $('.show_' + field).html(data['return_name']);
                                            $("#SYNCMESSAGE").hide();
                                            $("#PCCSYNCINFO").show();
                                        }});
                                    }else{
                                        $("#sync_pcc_project").show();
                                        $("#show_pcc_project").show();
                                        $("#NOINFO").hide();
                                        $("#PCCSYNCINFO").hide();
                                        $("#SYNCMESSAGE").show();
                                        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "syncPCCData", pcc_no: data['return_name']}, dataType:"json", success:function(data){
                                            if(data["status"]){
                                                $("#SYNCMESSAGE").hide();
                                                $("#PCCSYNCINFO").show();
                                            }else{
                                                alert("更新失敗！請檢查編號是否正確或是否有權限！");
                                                $("#SYNCMESSAGE").hide();
                                                $("#PCCSYNCINFO").show();
                                            }
                                        }});
                                    }
                                } else {
                                    $("#sync_pcc_project").hide();
                                    $("#show_pcc_project").hide();
                                    $("#NOINFO").show();
                                    $("#SYNCMESSAGE").hide();
                                    $("#PCCSYNCINFO").show();
                                }
                            } else if(data["contract_total"]!='init') {
                                $(".show_" + field).html(TransformThousands(data["return_name"]).replace(/\n/gi, '<br>'));
                                $("#total_cost_contract").html(TransformThousands(data["contract_total"]));
                            } else if(data["settlement_total"]!='init') {
                                $(".show_" + field).html(TransformThousands(data["return_name"]).replace(/\n/gi, '<br>'));
                                $("#total_cost_settlement").html(TransformThousands(data["settlement_total"]));
                            } else {
                                $(".show_" + field).html(data["return_name"].replace(/\n/gi, '<br>'));
                            }
                        }
                    }
                }});
            } else {
                $('.edit_' + field).attr('value', old_Info);
                $('.edit_' + field).attr('old_value', old_Info);
                $('.show_' + field).html(old_Info);
                alert(message);
            }
        } else if (category == 'Milestone'){
            if (format){
                $.ajax({ url:"/project/readjson/", type: "POST", data:{submit: "updateProjectInfo", 'project_id': project_id, 'entry': field, 'new_info': new_Info, 'old_Info': old_Info}, dataType:"json", success:function(data){
                    if (data['status'] != true){
                        alert(data['message']);
                    } else {
                        if (type == 'select-one'){
                            $('.edit_' + field).attr('value', new_Info)
                            $('.edit_' + field).attr('old_value', new_Info)
                            $('.show_' + field).html(data['return_name']);
                        } else {
                            $('.edit_' + field).attr('value', new_Info)
                            $('.edit_' + field).attr('old_value', new_Info)
                            $('.show_' + field).html(data['return_name']);
                        }
                    }
                }});
            } else {
                $('.edit_' + field).attr('value', old_Info)
                $('.edit_' + field).attr('old_value', old_Info)
                $('.show_' + field).html(old_Info);
                alert(message);
            }
        } else if (category == 'Fund'){
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "uFund", 'project_id': project_id, 'entry': field, 'new_Info': new_Info, 'old_Info': old_Info}, dataType:"json", success:function(data){
                if (data['status'] != true){
                    alert(data['message']);
                } else {
                    $('.edit_' + field).attr('value', new_Info);
                    $('.edit_' + field).attr('old_value', new_Info);
                    $('.show_' + field).html(TransformThousands(data['return_name']).replace(/\n/gi, '<br>'));
					$('#TotalProjectBudget').html(TransformThousands(data['new_total']));
					$('#SelfLoad').html(TransformThousands(data['new_self']));
					$('#localMatchFund').html(TransformThousands(data['new_local']));
                }
            }});
        } else if (category == 'Appropriate'){
            var row = $obj.attr('row');
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "uAppropriate", 'project_id': project_id, 'entry': field, 'new_Info': new_Info, 'old_Info': old_Info, 'row': row}, dataType:"json", success:function(data){
                if (data['status'] != true){
                    alert(data['message']);
                } else {
                    $('.edit_' + field).attr('value', new_Info)
                    $('.edit_' + field).attr('old_value', new_Info)
                    $('.show_' + field).html(TransformThousands(data['return_name']).replace(/\n/gi, '<br>'));
                }
            }});
        } else if (category == 'Allocation'){
            var row = $obj.attr('row');
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "uAllocation", 'project_id': project_id, 'entry': field, 'new_Info': new_Info, 'old_Info': old_Info, 'row': row}, dataType:"json", success:function(data){
                if (data['status'] != true){
                    alert(data['message']);
                } else {
                    $('.edit_' + field).attr('value', new_Info)
                    $('.edit_' + field).attr('old_value', new_Info)
                    $('.show_' + field).html(TransformThousands(data['return_name']).replace(/\n/gi, '<br>'));
                }
            }});
        } else if (category == 'FundRecord'){
            var row = $obj.attr('row');
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "uFundRecord", 'project_id': project_id, 'entry': field, 'new_Info': new_Info, 'old_Info': old_Info, 'row': row}, dataType:"json", success:function(data){
                if (data['status'] != true){
                    alert(data['message']);
                } else {
                    $('.edit_' + field).attr('value', new_Info)
                    $('.edit_' + field).attr('old_value', new_Info)
                    $('.show_' + field).html(TransformThousands(data['return_name']));
                }
            }});
        } else if (category == "ReserveInfo"){
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "uReserveInfo", 'project_id': project_id, 'entry': field, 'new_Info': new_Info, 'old_Info': old_Info}, dataType:"json", success:function(data){
                if (data['status'] != true){
                    alert(data['message']);
                } else {
                    $('.edit_' + field).attr('value', data['return_name'])
                    $('.edit_' + field).attr('old_value', data['return_name'])
                    if(data["num"]){
                        $(".show_" + field).html(TransformThousands(data["return_name"]));
                    }else{
                        $(".show_" + field).html(data["return_name"].replace(/\n/gi, '<br>'));
                    }
                    
                }
            }});
        } else if (category == 'Progress'){
            if (format) {
                $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "uProgress", 'project_id': project_id, 'entry': field, 'new_info': new_Info, 'row': $obj.attr('row')}, dataType:"json", success:function(data){
                    if (data['status'] != true){
                        alert(data['message']);
                        $('.edit_' + field).attr('value', old_Info);
                        $('.edit_' + field).attr('old_value', old_Info);
                    } else {
                        if (type == 'select-one'){
                            $('.edit_' + field).attr('value', new_Info)
                            $('.edit_' + field).attr('old_value', new_Info)
                            $('.show_' + field).html(data['return_name']);
                        } else {
                            $('.edit_' + field).attr('value', data['return_name'])
                            $('.edit_' + field).attr('old_value', data['return_name'])
                            $('.show_' + field).html(TransformThousands(data['return_name']).replace(/\n/gi, '<br>'));
                        }
                    }
                }});
            } else {
                $('.edit_' + field).attr('value', old_Info);
                $('.edit_' + field).attr('old_value', old_Info);
                $('.show_' + field).html(old_Info);
                alert(message);
            }
        } else if (category == 'Budget'){
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "uBudget", 'project_id': project_id, 'entry': field, 'new_Info': new_Info, 'old_Info': old_Info}, dataType:"json", success:function(data){
                if (data['status'] != true){
                    alert(data['message']);
                } else {
                    if (type == 'select-one'){
                        $('.edit_' + field).attr('value', new_Info)
                        $('.edit_' + field).attr('old_value', new_Info)
                        $('.show_' + field).html(data['return_name']);
                    } else {
                        $('.edit_' + field).attr('value', new_Info)
                        $('.edit_' + field).attr('old_value', new_Info)
                        $('.show_' + field).html(TransformThousands(data['return_name']));
                    }
                }
            }});
        }
    }

    if ( field == 'name' ){
        $('#title').html(new_Info + ' 工程資訊');
        $('#project_title').html(new_Info);
    }
    $('.show_' + field).fadeIn();
    $('.edit_' + field).hide();
}


var editAttention = function(){
    var html = '<div class="flora" style="overflow: auto"><table><tr><td>';
    html += '</td></tr></table><div style="display: none;" id="wantSortPlan"></div></div>';
    $dialog = $(html);
    $dialog.dialog({
        title: '階層選擇視窗',
        width: 600,
        height: 500,
        buttons: {
            '關閉本視窗': function(){
                $dialog.dialog('close');
            }
        }
    });
    $dialog.dialog('open');
}

function selectExportCustomReport () {
    var $select = $(this);
    if ($select.val() == ''){
        $('.uExportCustomReportDialog').text('');
    } else if ($select.val() != '_create'){
        $('.uExportCustomReportDialog').text('(編輯 '+$select.find(':selected').text()+' 的欄位)');
        $('.deleteExportCustomReport').text('(刪除此報表)');
    } else {
        $('.uExportCustomReportDialog').text('');
        var $dialog = $('#id_create_export_custom_report');
        $dialog.dialog({
            title: '新增報表',
            buttons: {
                '新增': function () {
                    var name = $('#id_export_custom_report_name').val();
                    if(!name){
                        alert('報表名稱必填');
                        return false;
                    }
                    $(this).dialog('close');
                    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "cExportCustomReport", 
                    	name: name
                		}, dataType:"json", success:function(json){
                			if(json['status'] == false){
                                alert(json['message']);
                                var $dialog = $('#id_create_export_custom_report');
                                $dialog.dialog('open');
                            } else {
                                var html = '<option id="exportCustomReportOption_' + json['exportcustomreport_id'] + '" value="'+json['exportcustomreport_id']+'">'+name+'</option>';
                                $select.append($(html));
                                $select.val(json['exportcustomreport_id']);
                                $('.uExportCustomReportDialog').text('(編輯 '+name+' 的欄位)');
                                $('.deleteExportCustomReport').text('(刪除此報表)');
                            }
                	}});
                },
                '關閉本視窗': function() {
                    $(this).dialog('close');
                }
            },
            width: 350
        }).dialog('open').show();
    }
}

function selectRecordProjectProfile () {
    var $select = $(this);
    var closeDialog = function () {
        $select.val('');
        $(this).dialog('close');
    }
    if ($select.val() == '') {
    } else if ($select.val() == '_create'){
        var $dialog = $('#id_create_record_project_profile');
        $dialog.dialog({
            title: '新增紀錄',
            buttons: {
                '新增': function () {
                    var name = $('#id_record_project_profile_name').val();
                    if(!name){
                        alert('紀錄名稱必填');
                        return false;
                    }
                    $(this).dialog('close');
                    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "cRecordProjectProfile", 
                    	name: name
                		}, dataType:"json", success:function(json){
                			if(json['status'] == false){
                                alert(json['message']);
                                var $dialog = $('#id_create_record_project_profile');
                                $dialog.dialog('open');
                            } else {
                                var html = '<option value="'+json['recordprojectprofile_id']+'">'+name+'</option>';
                                $select.append($(html));
                                $('#id_record_project_profiles').append($(html));
                                $select.val(json['recordprojectprofile_id']);
                                $('#id_record_project_profile_name').val('');
                                $('#id_now_record_project_profile_name').text(name);
                            }
                	}});
                },
                '關閉本視窗': closeDialog
            },
            width: 350
        }).dialog('open').show();
    } else {
    	$.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "rProjectsInRecordProjectProfile", 
    		record_project_profile_id: $select.val()
    		}, dataType:"json", success:function(json){
    			if (false == json['status']) {
                    alert(json['message']);
                } else {
                    $('input.recordProjects').each(function(){
                        var $input = $(this);
                        $input.attr('checked', '');
                        for (var i=0; i<json['project_ids'].length; i++){
                            if(json['project_ids'][i] == Number($input.attr('project_id'))){
                                $input.attr('checked', 'checked');
                                break;
                            }
                        }
                    });
                    $('#id_now_record_project_profile_name').text($select.find(':selected').text());
                }
    	}});
    }
    $('input.recordThisPageProjects').attr('checked', '');
    $('input.recordAllProjects').attr('checked', '');
}

function recordAllProjects () {
    var $select = $('#id_select_record_project_profile');
    var record_project_profile_id = $select.val();
    if (!record_project_profile_id || record_project_profile_id == '_create') {
        alert('未選擇「工程案紀錄」');
        return false;
    }
    var $checkbox = $(this);
    var checked = $checkbox.attr('checked');
    $('#id_body').css('opacity', 0.25);
    $('img#loading').css('z-index', 10000).show();
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "recordAllProjects", 
    	checked: checked, record_project_profile_id: record_project_profile_id,
        querystring: $checkbox.attr('querystring')
    	}, dataType:"json", success:function(json){
    		if (json['status'] == false) {
                alert(json['message']);
            } else {
                $('input.recordProjects').each(function(){
                    var $input = $(this);
                    if (checked) {
                        $input.attr('checked', 'checked');
                    } else {
                        $input.attr('checked', '');
                    }
                    $input.parent().highlightFade();
                });
            }
    		$('#id_body').css('opacity', 1);
            $('img#loading').hide();
    }});
}

function recordThisPageProjects () {
    var $select = $('#id_select_record_project_profile');
    var record_project_profile_id = $select.val();
    if (!record_project_profile_id || record_project_profile_id == '_create') {
        alert('未選擇「工程案紀錄」');
        return false;
    }
    var $checkbox = $(this);
    var project_ids = [];
    $('input.recordProjects').each(function(){
        project_ids.push($(this).attr('project_id'));
    });
    var checked = $checkbox.attr('checked');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "recordProjects", 
    	project_ids: project_ids.join(','),
        record_project_profile_id: record_project_profile_id, checked: checked
    	}, dataType:"json", success:function(json){
    		if (json['status'] == false) {
                alert(json['message']);
            } else {
                $('input.recordProjects').each(function(){
                    var $input = $(this);
                    if (checked) {
                        $input.attr('checked', 'checked');
                    } else {
                        $input.attr('checked', '');
                    }
                    $input.parent().highlightFade();
                });
            }
    }});
}

function recordProjects () {
    var $select = $('#id_select_record_project_profile');
    var record_project_profile_id = $select.val();
    if (!record_project_profile_id || record_project_profile_id == '_create') {
        alert('未選擇「工程案紀錄」');
        return false;
    }
    var $checkbox = $(this);
    var project_ids = [$checkbox.attr('project_id')].join(',');
    var checked = $checkbox.attr('checked');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "recordProjects", 
    	project_ids: project_ids,
        record_project_profile_id: record_project_profile_id, checked: checked
    	}, dataType:"json", success:function(json){
    		if (json['status'] == false) {
                alert(json['message']);
            } else {
                $checkbox.parent().highlightFade();
            }
    }});
}

function exportCustomReportHTML () {
    var $select = $('.selectExportCustomReport');
    if (Number($select.val()) > 0){
        window.open('/project/export_custom_report/'+$select.val()+'/?'+$(this).attr('querystring'));
    } else {
        alert('請選擇報表名稱');
        return false;
    }
}

function deleteExportCustomReport () {
    var $obj = $(this);
    var export_custom_report_id = $('.selectExportCustomReport').val();
    var msg = '是否要刪除此自訂報表?';
    if(confirm(msg)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "deleteExportCustomReport", export_custom_report_id: export_custom_report_id},
                dataType:"json", success:function(data){
            if (data['status'] == true){
                $('#exportCustomReportOption_'+export_custom_report_id).fadeOut();
                $('.selectExportCustomReport').attr('value', '')
                $('.uExportCustomReportDialog').text('');
                $('.deleteExportCustomReport').text('');
            }
        }});
    }
}


function uExportCustomReportDialog () {
    var $dialog = $('#id_update_export_custom_report_dialog');
    var export_custom_report_id = $('.selectExportCustomReport').val();
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "rReportFields", 
    	export_custom_report_id: export_custom_report_id
    	}, dataType:"json", success:function(json){
    		if (false == json['status']) {
                alert(json['message']);
            } else {
                var html = '';
                for (var i=0; i<json['tags'].length; i++){
                    var tag = json['tags'][i];
                    html += '<h3 style="margin: 10px">'+tag+'</h3><div class="custom_report_field_div">';
                    var fields = json['fields'][tag];
                    for (var j=0; j<fields.length; j++){
                        var f= fields[j];
                        if (f['export_custom_report_field_checked']){
                            html += '<span class="custom_report_field field_checked"><input checked="checked" class="addOrRemoveFieldFromExportCustomReport"'
                                +' type="checkbox" export_custom_report_field_priority="'+f['export_custom_report_field_priority']
                                +'" export_custom_report_field_id="'+f['export_custom_report_field_id']
                                +'" report_field_id="'+f['id']+'"> <span class="checkedPrevInput">'
                                +f['name']+'</span></span>';
                        } else {
                            html += '<span class="custom_report_field"><input class="addOrRemoveFieldFromExportCustomReport"'
                                +' type="checkbox" export_custom_report_field_priority="'+f['export_custom_report_field_priority']
                                +'" export_custom_report_field_id="'+f['export_custom_report_field_id']
                                +'" report_field_id="'+f['id']+'"> <span class="checkedPrevInput">'
                                +f['name']+'</span></span>';
                        }
                    }
                    html +='</div><br/><br/><br/>';
                }
                $dialog.html(html).find('input.addOrRemoveFieldFromExportCustomReport')
                    .click(addOrRemoveFieldFromExportCustomReport).end()
                    .find('span.checkedPrevInput').click(function(){
                        var $span = $(this);
                        var $input = $span.prev();
                        var is_checked = $input.attr('checked');
                        if (is_checked){
                            $input.attr('checked', '');
                        } else {
                            $input.attr('checked', 'checked');
                        }
                        var export_custom_report_id = $('.selectExportCustomReport').val();
                        var add_or_remove = $input.attr('checked')
                        $.post('/project/ajax/', {submit: 'addOrRemoveFieldFromExportCustomReport',
                            export_custom_report_id:export_custom_report_id, add_or_remove: add_or_remove,
                            report_field_id: $input.attr('report_field_id')}, function(json){
                            if (false == json['status']) {
                                alert(json['message']);
                            } else {
                                $input.attr('export_custom_report_field_id', json['export_custom_report_field_id']);
                                $input.attr('export_custom_report_field_priority', json['export_custom_report_field_priority']);
                                if (json['export_custom_report_field_id']){
                                    $input.parent().addClass('field_checked');
                                } else {
                                    $input.parent().removeClass('field_checked');
                                }
                            }
                        }, 'json');
                    }).end()
                    .dialog({
                    title: '編輯報表',
                    buttons: {
                        '欄位排序': sortExportCustomReportDialog,
                        '關閉本視窗': function() {
                            $(this).dialog('close');
                        }
                    },
                    width: 800
                }).dialog('open');
            }
    }});
}

function _sortByPriority ($a, $b) {
    var a_priority = $('input', $a).attr('export_custom_report_field_priority');
    var b_priority = $('input', $b).attr('export_custom_report_field_priority');
    if (Number(a_priority) > Number(b_priority)) {
        return 1;
    } else if (Number(a_priority) == Number(b_priority)) {
        return 0;
    } else {
        return -1;
    }
}

function sortExportCustomReportDialog () {
    $(this).dialog('close');
    var $dialog = $('#id_sort_export_custom_report_dialog');

    var $update_dialog = $('#id_update_export_custom_report_dialog');

    var spans = [];
    $('.custom_report_field', $update_dialog).each(function(){
        var $span = $(this);
        if ($('input', $span).attr('checked')){
            spans.push($span);
        }
    });
    spans.sort(_sortByPriority);

    var html = '<ul id="id_sortable">';
    for (var i=0; i<spans.length; i++){
        var $span = spans[i];
        var text = $span.text();
        var export_custom_report_field_id = $('input', $span).attr('export_custom_report_field_id');
        var export_custom_report_field_priority = $('input', $span).attr('export_custom_report_field_priority');
        html += '<li export_custom_report_field_id="'+export_custom_report_field_id
            +'" export_custom_report_field_priority="'+export_custom_report_field_priority
            +'"><span class="ui-icon ui-icon-arrowthick-2-n-s"></span>'+text+'</li>';
    }
    html += '</ul>';
    $dialog.html(html).dialog({
        title: '欄位排序',
        buttons: {
            '編輯報表': function() {
                $(this).dialog('close');
                uExportCustomReportDialog()
            },
            '關閉本視窗': function() {
                $(this).dialog('close');
            }
        },
        width: 800
    }).dialog('open');
    $('#id_sortable', $dialog).sortable({
        update: function(event, ui) {
            var $obj = ui.item;
            var $prev = $obj.prev();
            var $next = $obj.next();
            if ($prev.length == 0 && $next.length == 0) {
                alert("It does not happen!");
            } else if ($prev.length == 0) {
                $obj.attr('export_custom_report_field_priority', Number($next.attr('export_custom_report_field_priority'))-16);
            } else if ($next.length == 0 ) {
                $obj.attr('export_custom_report_field_priority', Number($prev.attr('export_custom_report_field_priority'))+16);
            } else {
                $obj.attr('export_custom_report_field_priority', 0.5*(Number($prev.attr('export_custom_report_field_priority'))+Number($next.attr('export_custom_report_field_priority'))));
            }
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "uExportCustomReportFieldPriority", 
            	id: $obj.attr('export_custom_report_field_id'), priority: $obj.attr('export_custom_report_field_priority')
            	}, dataType:"json", success:function(json){
            		if (false == json['status']) {
                        alert(json['message']);
                    } else {
                        $obj.highlightFade('#99CCFF');
                        if (json['prioritys'] == false){
                            $('input[export_custom_report_field_id='+$obj.attr('export_custom_report_field_id')+']')
                                .attr('export_custom_report_field_priority', $obj.attr('export_custom_report_field_priority'));
                        } else {
                            for (var i=0; i<json['prioritys'].length; i++){
                                var p = json['prioritys'][i];
                                $('#id_update_export_custom_report_dialog input[export_custom_report_field_id='+p[0]+']')
                                    .attr('export_custom_report_field_priority', p[1]);
                                $('ul#id_sortable li[export_custom_report_field_id='+p[0]+']')
                                    .attr('export_custom_report_field_priority', p[1]);
                            }
                        }
                    }
            }});
        },
        placeholder: "ui-state-highlight"
    });
    $("#id_sortable", $dialog).disableSelection();
}

function addOrRemoveFieldFromExportCustomReport () {
    var export_custom_report_id = $('.selectExportCustomReport').val();
    var $input = $(this);
    var add_or_remove = $input.attr('checked');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "addOrRemoveFieldFromExportCustomReport", 
    	export_custom_report_id:export_custom_report_id, add_or_remove: add_or_remove,
        report_field_id: $input.attr('report_field_id')
    	}, dataType:"json", success:function(json){
    		if (false == json['status']) {
                alert(json['message']);
            } else {
                $input.attr('export_custom_report_field_id', json['export_custom_report_field_id']);
                $input.attr('export_custom_report_field_priority', json['export_custom_report_field_priority']);
                if (json['export_custom_report_field_id']){
                    $input.parent().addClass('field_checked');
                } else {
                    $input.parent().removeClass('field_checked');
                }
            }
    }});
}

$(document).ready(function(){
    $('#addProject').click(addProject);
    $('#clearSearchInfo').click(clearSearchInfo);
    $('#clearSearchAdvanceInfo').click(clearSearchAdvanceInfo);
    $('#clearBudgetSearchAdvanceInfo').click(clearBudgetSearchAdvanceInfo);
    $('#count_type').click(clearSearchInfo);
    $('#clearBudgetInfo').click(clearBudgetInfo);
//    $('.deletePlan').click(deletePlan);

    $('.updatePlanInfo').click(updatePlanInfo);
    $('.setDefaultProject').click(setDefaultProject);
    $('.editable').click(editProjectInfo);
    $('.update_edited').blur(updateProjectInfo);
//    $('.no_parameter').change(cProjectNo);
    $('.makeStatistics').click(makeStatistics);
    $('.makeStatistics_change').change(makeStatistics);
    $('.makeStatisticsProjects').click(makeStatisticsProjects);
    $('.count_type').change(switchCountType);
    $('.switch').click(switchFR);
    $('#uploadPhoto').click(uploadPhoto);
    $('.deleteProjectPhoto').click(deleteProjectPhoto);
    $('.updatePhotoInfo_Show').click(updatePhotoInfo_Show);
    $('.updatePhotoInfo_Edit').blur(updatePhotoInfo_Edit);
    $('#makeStatistics_Include_sub').click(makeStatistics_Include_sub);
    $('#makeStatistics_not_Include_sub').click(makeStatistics_not_Include_sub);
    $('#status').change(checkVouch);
    $('#undertake_type').change(checkUndertake);
    $('.ShowandHidePlan').click(ShowandHidePlan);
//    $('#record_button').click(makeFundRecord);
//    $('#place').change(getFishingPort);
//    $('#id_place').change(getFishingPort);
    $('.edit_place').change(changeFishingPort);
//    $('#undertake_type').blur(checkUndertakeType);
    $('#fundrecord_year_list').change(changeYearList);
//    $('#delete_button').click(deleteFundRecord);
    $('#makeDownloadFile').change(makeDownloadFile);
    $('#makeWorkExcel').click(makeWorkExcel);
//    $('.fundrecord_set').change(updateFundRecordSet);
    $('.setPlanToWorkExcel').click(setPlanToWorkExcel);
    $('.edit_by_click').click(editBudget);
    $('.show_hided_table').mousemove(showPoppingMemu);
    $('.hideTable').click(hideInfoCol);
    $('.hideCol').click(hideInfoCol);
    $('.showTable').click(showInfoCol);
    $('.transAll').click(transInfoCol);
    $('.searchPlanProjects').click(searchPlanProjects);
    $('.createPlanProjects').click(createPlanProjects);
    $('.project_budget').blur(recountPercent);
    $('.makeChart').click(makeChart);
//    $('.getcoord').change(getCoord);
    $('.updateCoord').change(updateCoord);

    $('.SumBar').click(sumBar);
    $('.balance').change(balanceBudget);
    $('.jsGetChart').click(jsGetChart);
    $('.showProjectMemo').click(showProjectMemo);
    $('.selectYearByChage').change(selectYearByChage);
    $('.deleteProject').click(deleteProject);
    $('.recoverProject').click(recoverProject);
//    $('#addMoreFishingPort').click(addMoreFishingPort);
    $('.deleteFishingPort').click(deleteFishingPort);
    $('.checkBN').blur(checkBN);
    $('.update_planbudget').blur(updatePlanBudget);
    $('.addPlanBudget').click(addPlanBudget);
    $('.deletePlanBudget').click(deletePlanBudget);
    $('.SwitchDisplay').click(switchDisplay);
    $('.singleswitch').click(singleSwitch);
    $('.addProjectFund').click(addProjectFund);
    $('.deleteProjectFund').click(deleteProjectFund);
    $('.hightlightFundrecord').mouseover(hightlightFundrecord);
    $('.hightlightFundrecord').mouseout(unhightlightFundrecord);
    $('.ShowandHideSubPlan').click(showandHideSubPlan);

    $('.redaction').click(redactionProjectInfo);
    $('.updateRedaction').blur(updateProjectRedaction);
    $('#editAttention').click(editAttention);

    $('.selectExportCustomReport').change(selectExportCustomReport);
    $('.recordAllProjects').click(recordAllProjects);
    $('.recordThisPageProjects').click(recordThisPageProjects);
    $('.recordProjects').click(recordProjects);
    $('.exportCustomReportHTML').click(exportCustomReportHTML);
    $('.uExportCustomReportDialog').click(uExportCustomReportDialog);
    $('.deleteExportCustomReport').click(deleteExportCustomReport);

    $('.selectRecordProjectProfile').change(selectRecordProjectProfile);
    $('.selectRecordProjectProfile').children().each(function(){
        if($('#id_record_project_profiles').val() != '' && $(this).attr('value') == $('#id_record_project_profiles').val()){
            $(this).attr('selected', 'selected');
            $('#id_now_record_project_profile_name').text($(this).text());
        }
    });
    $('.selectRecordProjectProfile').change();


});
