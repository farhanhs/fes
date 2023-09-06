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

function rFindLocation(){
	var $obj = $(this);
    var place_id = $obj.attr("value");
    if (!place_id){
    	return false
    }
    $.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "rFindLocation", place_id: place_id}, dataType:"json", success:function(data){
        if(data["status"]){
        	$("#change_location").html($(data["html"]));
        }
    }});
}

function error_no(){
	var $obj = $(this);
    var value = $obj.attr("value");
    if (value != ""){
    	$.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "error_no", value: value}, dataType:"json", success:function(data){
            if (data["status"] == false){
            	$obj.attr('style', 'background-color: red;');
            	alert('無此缺失編號，請檢查');
            } else {
            	$obj.attr('style', 'background-color: #F1F1F1;');
            }
        }});
    }
}

function add_New_Supervise_Case(){
	var $obj = $(this);
	var num_check=/^-?[0-9]*$/;
	var float_check = /^(-?\d+)(\.\d+)?$/;
    var needExistData = $(".needExist");
    for (var i=0;i<needExistData.length;i++){
        if(needExistData[i].value==""){
            alert("請檢查必填欄位！");
            return false;
        }
    }
    var needBeInteger = $(".integer");
    for (var i=0;i<needBeInteger.length;i++){
        if(needBeInteger[i].value!="" && !(num_check.test(needBeInteger[i].value))){
            alert("扣點統計為整數欄位！");
            return false;
        }
    }
    var needBeFloat = $(".float");
    for (var i=0;i<needBeFloat.length;i++){
        if(needBeFloat[i].value!="" && !(float_check.test(needBeFloat[i].value))){
        	$obj = $(this);
        	var name = $obj.attr('name');
            alert("請檢查" + char_name + "數字欄位！");
            return false;
        }
    }
    
    var plan = $("#plan").val();
    var subordinate_agencies_unit = $("#subordinate_agencies_unit").val();
    var date = $("#date").val();
    var project = $("#project").val();
    var place = $("#place").val();
    var location = $("#location").val();
    var project_organizer_agencies = $("#project_organizer_agencies").val();
    var project_manage_unit = $("#project_manage_unit").val();
    var designer = $("#designer").val();
    var inspector = $("#inspector").val();
    var construct = $("#construct").val();
    var budget_price = $("#budget_price").val();
    var contract_price = $("#contract_price").val();
    var info = $("#info").val();
    var progress_date = $("#progress_date").val();
    var scheduled_progress = $("#scheduled_progress").val();
    var actual_progress = $("#actual_progress").val();
    var scheduled_money = $("#scheduled_money").val();
    var actual_money = $("#actual_money").val();
    var outguides = $("#outguides").val();
    var inguides = $("#inguides").val();
    var start_date = $("#start_date").val();
    var expected_completion_date = $("#expected_completion_date").val();
    var captains = $("#captains").val();
    var workers = $("#workers").val();
    var score = $("#score").val();
    var merit = $("#merit").val();
    var advise = $("#advise").val();
    var other_advise = $("#other_advise").val();
    var construct_deduction = $("#construct_deduction").val();
    var inspector_deduction = $("#inspector_deduction").val();
    var organizer_deduction = $("#organizer_deduction").val();
    var project_manage_deduction = $("#project_manage_deduction").val();
    var test = $("#test").val();
    var error_num = parseInt($("#add_New_Error").attr("now_num")); 
//    var all_error = [];
//    for (var i=1;i<error_num+1;i++){
//    	all_error.push([$("#error_no_"+i).val(), $("#error_level_"+i).val(), $("#error_context_"+i).val()]);
//    }
//    all_error = $.stringify(all_error);
    $.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "add_New_Supervise_Case", 
    	plan: plan, subordinate_agencies_unit: subordinate_agencies_unit, date: date, project: project, 
    	place: place, location: location, project_organizer_agencies: project_organizer_agencies, project_manage_unit: project_manage_unit, 
    	designer: designer, inspector: inspector, construct: construct, budget_price: budget_price, 
    	contract_price: contract_price, info: info, progress_date: progress_date, scheduled_progress: scheduled_progress, 
    	actual_progress: actual_progress, scheduled_money: scheduled_money, actual_money: actual_money, outguides: outguides, 
    	inguides: inguides, start_date: start_date, expected_completion_date: expected_completion_date, captains: captains, 
    	workers: workers, score: score, merit: merit, advise: advise, organizer_deduction: organizer_deduction,
    	other_advise: other_advise, construct_deduction: construct_deduction, inspector_deduction: inspector_deduction,
    	test: test, project_manage_deduction: project_manage_deduction
    	}, dataType:"json", success:function(data){
        if(data["status"]){
        	alert('新增成功');
        	window.location = '/supervise/profile/' + data["case_id"] + '/#add_New_Error';
        }
    }});
}


function search_Supervise_Case(){
	var $obj = $(this);
	var num_check=/^-?[0-9]*$/;
	var float_check = /^(-?\d+)(\.\d+)?$/;
    var needBeInteger = $(".integer");
    var needBeFloat = $(".float");
    for (var i=0;i<needBeFloat.length;i++){
        if(needBeFloat[i].value!="" && !(float_check.test(needBeFloat[i].value))){
        	var name = needBeFloat[i].name;
            alert("請檢查數字欄位！");
            return false;
        }
    }
    var plan = $("#plan").val();
    var subordinate_agencies_unit = $("#subordinate_agencies_unit").val();
    var date_from = $("#date_from").val();
    var date_to = $("#date_to").val();
    var project = $("#project").val();
    var location = $("#location").val();
    var place = $("#place").val();
    var project_organizer_agencies = $("#project_organizer_agencies").val();
    var project_manage_unit = $("#project_manage_unit").val();
    var budget_price_from = $("#budget_price_from").val();
    var budget_price_to = $("#budget_price_to").val();
    var designer = $("#designer").val();
    var contract_price_from = $("#contract_price_from").val();
    var contract_price_to = $("#contract_price_to").val();
    var inspector = $("#inspector").val();
    var scheduled_progress_from = $("#scheduled_progress_from").val();
    var scheduled_progress_to = $("#scheduled_progress_to").val();
    var construct = $("#construct").val();
    var actual_progress_from = $("#actual_progress_from").val();
    var actual_progress_to = $("#actual_progress_to").val();
    var outguides = $("#outguides").val();
    var start_date_from = $("#start_date_from").val();
    var start_date_to = $("#start_date_to").val();
    var inguides = $("#inguides").val();
    var expected_completion_date_from = $("#expected_completion_date_from").val();
    var expected_completion_date_to = $("#expected_completion_date_to").val();
    var score_from = $("#score_from").val();
    var score_to = $("#score_to").val();
    var error = $("#error").val();
    $.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "search_Supervise_Case", 
    	plan: plan, subordinate_agencies_unit: subordinate_agencies_unit, date_from: date_from, date_to: date_to,
    	project: project, location: location, place: place, project_organizer_agencies: project_organizer_agencies,
    	project_manage_unit: project_manage_unit, budget_price_from: budget_price_from, budget_price_to: budget_price_to,
    	designer: designer, contract_price_from: contract_price_from, contract_price_to: contract_price_to,
    	inspector: inspector, scheduled_progress_from: scheduled_progress_from, scheduled_progress_to: scheduled_progress_to,
    	construct: construct, actual_progress_from: actual_progress_from, actual_progress_to: actual_progress_to,
    	outguides: outguides, start_date_from: start_date_from, start_date_to: start_date_to, inguides: inguides, 
    	expected_completion_date_from: expected_completion_date_from, expected_completion_date_to: expected_completion_date_to,
    	score_from: score_from, score_to: score_to, error: error
    	}, dataType:"json", success:function(data){
        if(data["status"]){
        	var html = $(data["html"]);
        	$("#search_Result").html(html);
        	forEach(document.getElementsByTagName('table'), function(table) {
    	      if (table.className.search(/\bsortable\b/) != -1) {
    	        sorttable.makeSortable(table);
    	      }
    	    });
        	$(".deleteCase").click(deleteCase);
        }
    }});
}


jQuery.extend({
    stringify : function stringify(obj) {
        var t = typeof (obj);
        if (t != "object" || obj === null) {
            // simple data type
            if (t == "string") obj = '"' + obj + '"';
            return String(obj);
        } else {
            // recurse array or object
            var n, v, json = [], arr = (obj && obj.constructor == Array);

            for (n in obj) {
                v = obj[n];
                t = typeof(v);
                if (obj.hasOwnProperty(n)) {
                    if (t == "string") v = '"' + v + '"'; else if (t == "object" && v !== null) v = jQuery.stringify(v);
                    json.push((arr ? "" : '"' + n + '":') + String(v));
                }
            }
            return (arr ? "[" : "{") + String(json) + (arr ? "]" : "}");
        }
    }
});

function ScoreLevel(){
	var $obj = $(this);
	var id = $obj.attr('id');
	var score = $obj.attr('value');
	if (score >= 90){
		$("#"+id+"_level").html('(優等)');
	} else if (score >= 80) {
		$("#"+id+"_level").html('(甲等)');
	} else if (score >= 70) {
		$("#"+id+"_level").html('(乙等)');
	} else if (score >= 60) {
		$("#"+id+"_level").html('(丙等)');
	} else if (score < 60) {
		$("#"+id+"_level").html('(丁等)');
	} else {
		alert('請輸入數字分數!!');
		$obj.attr('value', '');
	}
}

function change_edit_type(){
	var $obj = $(this);
	var field_name = $obj.attr('field_name');
	$('#show_info__'+field_name).hide();
	$('#edit_info__'+field_name).show().focus();
}


function change_view_type(){
	var $obj = $(this);
	var needExist = $obj.attr('needExist');
	var table_name = $obj.attr('table_name');
	var field_name = $obj.attr('name');
	var row_id = $obj.attr('row_id');
	var value = $obj.attr('value');
	var old_value = $obj.attr('old_value');
	var data_type = $obj.attr('data_type');
	var check = 'true';
	
	var num_check=/^-?[0-9]*$/;
	var float_check = /^(-?\d+)(\.\d+)?$/;
	var date_check=/^(([1-9]\d{0,3}|0)\-\d{2}\-\d{2})|(([1-9]\d{0,3}|0)\.\d{2}\.\d{2})|(([1-9]\d{0,3}|0)\/\d{2}\/\d{2})$/;
	if (needExist == 'True' && value == ''){
		alert('此欄位不可為空值');
		check = 'false';
	}
	if (data_type == 'integer' && !(num_check.test(value))){
		alert('請輸入整數!');
		check = 'false';
	}
	if (data_type == 'date' && !(date_check.test(value))){
		alert('請使用小日曆點選或輸入正確日期格式，如"2012-01-01"!');
		check = 'false';
	}
	if (data_type == 'float' && !(float_check.test(value))){
		alert('請輸入數字!');
		check = 'false';
	}
	if (check == 'false'){
		$obj.attr('value', old_value);
	} else if (value != old_value) {
		$.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "update_supervise_info", 
			value: value, row_id: row_id, table_name: table_name, field_name: field_name
			}, 
			dataType:"json", success:function(data){
            if (data["status"] == false){
            	alert(data["msg"]);
            	$obj.attr('value', old_value);
            } else {
            	if (field_name=='place') {
            		$('#location_td').html(data["html"]);
            		$(".change_edit_type").click(change_edit_type);
            		$(".change_view_type").blur(change_view_type);
            	}
            	if (data_type=='float') {
            		value = TransformThousands(value);
            	}
            	$obj.attr('old_value', value);
            	$('#show_info__'+field_name).html(data["return_value"].replace(/\n/gi, '<br>'));
            }
        }});
	}
	$('#show_info__'+field_name).show();
	$('#edit_info__'+field_name).hide();
}

function deleteGuide(){
	var $obj = $(this);
	var field_name = $obj.attr('field_name');
	var row_id = $obj.attr('row_id');
	var case_id = $obj.attr('case_id');
	if (confirm('確定要刪除嗎??')){
		$.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "deleteGuide", 
			case_id: case_id, row_id: row_id, field_name: field_name
			}, 
			dataType:"json", success:function(data){
	        if (data["status"] == false){
	        	alert(data["msg"]);
	        } else {
	        	$('#tr_'+field_name+'_'+row_id).remove();
	        }
	    }});
	}
}


function addGuide(){
	var $obj = $(this);
	var field_name = $obj.attr('field_name');
	var name = $('#'+field_name).attr('value');
	var case_id = $obj.attr('case_id');
	$.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "addGuide", 
		case_id: case_id, field_name: field_name, name: name
		}, 
		dataType:"json", success:function(data){
        if (data["status"] == false){
        	alert(data["msg"]);
        } else {
        	$(data["html"]).insertBefore($('#insert_place_'+field_name));
        	$('#'+field_name).attr('value', '');
        	$(".deleteGuide").click(deleteGuide);
        }
    }});
}


function change_view_type_error(){
	var $obj = $(this);
	var table_name = $obj.attr('table_name');
	var field_name = $obj.attr('name');
	var field_name_id = $obj.attr('field_name');
	var row_id = $obj.attr('row_id');
	var value = $obj.attr('value');
	var old_value = $obj.attr('old_value');
	if (value != old_value) {
		$.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "change_view_type_error", 
			value: value, row_id: row_id, table_name: table_name, field_name: field_name
			}, 
			dataType:"json", success:function(data){
            if (data["status"] == false){
            	alert(data["msg"]);
            	$obj.attr('value', old_value);
            } else {
            	$obj.attr('old_value', value);
            	$('#show_info__'+field_name_id).html(value.replace(/\n/gi, '<br>'));
            }
        }});
	}
	$('#show_info__'+field_name_id).show();
	$('#edit_info__'+field_name_id).hide();
}

function add_New_Error(){
	var $obj = $(this);
	var case_id = $obj.attr('case_id');
    var now_num = parseInt($obj.attr("now_num"));
    var next_num = now_num + 1;
    var html = '';
    html += '<tr id="temp_Error_Tr_' + next_num + '">'
    html += '   <td><img src="/media/images/additem.png" error_num="' + next_num + '" case_id="'+ case_id +'" title="新增缺失" class="add_New_Error_For_Case"></td>'
    html += '	<td><input class="input_text error_no" id="error_no_' + next_num + '" type="text" name="error_no_' + next_num + '" size=7 value=""/></td>'
    html += '	<td><input class="input_text" id="error_level_' + next_num + '" type="text" name="error_level_' + next_num + '" size=4 value=""/></td>'
    html += '	<td><input class="input_text" id="error_context_' + next_num + '" type="text" name="error_context_' + next_num + '" size=90 value=""/></td>'
    html += '</tr>'
    $(html).insertBefore($("#insert_Error_Place"));
    $obj.attr('now_num', next_num);
    $(".error_no").blur(error_no);
    $(".add_New_Error_For_Case").click(add_New_Error_For_Case);
}

function add_New_Error_For_Case(){
	var $obj = $(this);
	var case_id = $obj.attr('case_id');
	var error_num = $obj.attr('error_num');
	var error_no = $('#error_no_'+error_num).attr('value');
	var error_level = $('#error_level_'+error_num).attr('value');
	var error_context = $('#error_context_'+error_num).attr('value');
	
	$.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "add_New_Error_For_Case", 
		case_id: case_id, error_no: error_no, error_level: error_level, error_context: error_context
		}, 
		dataType:"json", success:function(data){
        if (data["status"] == false){
        	alert(data["msg"]);
        } else {
        	$('#temp_Error_Tr_'+error_num).remove();
        	$(data["html"]).insertBefore($("#insert_Error_Place"));
        	$(".change_view_type_error").blur(change_view_type_error);
        	$(".change_edit_type").click(change_edit_type);
        	$(".deleteError").click(deleteError);
        }
    }});
}

function deleteError(){
	var $obj = $(this);
	var error_id = $obj.attr('error_id');
	if (confirm('確定要刪除嗎??')){
		$.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "deleteError", 
			error_id: error_id
			}, 
			dataType:"json", success:function(data){
	        if (data["status"] == false){
	        	alert(data["msg"]);
	        } else {
	        	$('#error_tr_'+error_id).remove();
	        }
	    }});
	}
}

function deleteCase(){
	var $obj = $(this);
	var case_id = $obj.attr('case_id');
	if (confirm('確定要刪除嗎?? 注意：刪除後將無法回復!!!')){
		$.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "deleteCase", 
			case_id: case_id
			}, 
			dataType:"json", success:function(data){
	        if (data["status"] == false){
	        	alert(data["msg"]);
	        } else {
	        	$('#case_tr_'+case_id).remove();
	        }
	    }});
	}
}


function upload_Photo_File() {
    var $obj = $(this);
    var supervise_id = $obj.attr('supervise_id');
    var name = $('#newfile_name_'+supervise_id).attr('value');
    var file = $('#newfile_file_'+supervise_id).attr('value');
    var memo = $('#newfile_memo_'+supervise_id).attr('value');
    var ext = $('#newfile_file_'+supervise_id).attr('value').split('.');
    ext = ext[ext.length-1].toLowerCase();

    if (!(ext=='png' || ext=='bmp' || ext=='jpg' || ext=='jpeg' || ext=='tif' || ext=='tiff')){
        alert('錯誤，非圖片格式，此處僅能上傳圖片檔案，如 png / bmp / jpg / jpeg / tif / tiff 等類型檔案!!!')
        return false;
    }
    
    if (!file){
        alert('請選擇檔案!!!')
        return false;
    }

    if (!confirm('確定上傳 '+file+' ?  按下確定後開始上傳，請勿關閉此頁面!!')){
        return false;
    }

    $.ajaxFileUpload({
        url: '/supervise/upload_photo_file/'+supervise_id+'/?name='+name+'&memo='+memo,
        async: true,
        fileElementId: 'newfile_file_'+supervise_id,
        dataType: 'json',
        success: function (json, status) {
            if (json['status'] == false){
                alert(json['message']);
            } else {
                $('#newfile_file_'+supervise_id).attr('value', '');
                $('#newfile_name_'+supervise_id).attr('value', '');
                $('#newfile_memo_'+supervise_id).attr('value', '');
                var html = '';
                html += '<span id="error_Photo_'+json['id']+'">';
                html += '<a class="show_Big_Error_Photo" image_src="/'+json['photo_rUrl']+'" title="'+json['name']+'-'+json['memo']+'">';
                html += '<img src="/'+json['photo_rThumbUrl']+'" width=150 title="'+json['name']+'-'+json['memo']+'"></a>';
                html += '<img class="deleteErrorPhoto" row_id='+json['id']+' src="/media/images/delete.png" width=20 title="刪除照片">';
                html += '</span>';
                $(html).insertBefore($('#insert_New_Error_Photo'));
            	$(".deleteErrorPhoto").click(deleteErrorPhoto);
            	$(".show_Big_Error_Photo").click(show_Big_Error_Photo);
            }
        },
        error: function (json, status, e) {
        }
    });
}

function selectTable() {
    var $obj = $(this);
    var table_id = $obj.attr('table_id');
    var year = $('#select_year').attr('value');
    window.location = '/supervise/statistics_table/' + year + '/' + table_id + '/';
}

function showFilterCases() {
    var $obj = $(this);
    var ids = $obj.attr('ids');
    var deduction = $obj.attr('deduction');
    var search_condition = $obj.attr('search_condition');
    $.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "showFilterCases", 
    	ids: ids, deduction: deduction, search_condition: search_condition
    	}, dataType:"json", success:function(data){
        if(data["status"]){
        	var html = $(data["html"]);
        	$("#search_Result").html(html);
        	forEach(document.getElementsByTagName('table'), function(table) {
    	      if (table.className.search(/\bsortable\b/) != -1) {
    	        sorttable.makeSortable(table);
    	      }
    	    });
        	$(".deleteCase").click(deleteCase);
            $('.showFilterCases').attr('bgcolor', 'white');
            $obj.attr('bgcolor', '#91FF92');
            window.location = "#sarch_result";
            
        }
    }});
}

function deleteErrorPhoto() {
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    if (confirm('確定要刪除此張缺失相片嗎，刪除後將無法恢復!!')){
    	$.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "deleteErrorPhoto", 
        	row_id: row_id
        	}, dataType:"json", success:function(data){
            if(data["status"]){
            	$('#error_Photo_'+row_id).remove();
            }
        }});
    }
}

function show_Big_Error_Photo() {
    var $obj = $(this);
    var title = $obj.attr('title');
    var url = $obj.attr('image_src');
    var html = '<table><tr><td>'+title+'</td></tr>';
    html += '<tr><td><img src="'+url+'" width=800></td></tr></table>';
    $dialog = $(html);
    $dialog.dialog({
        title: "缺失相片",
        width: 850,
        height: 650,
        buttons: {
            "關閉本視窗": function(){
                $dialog.dialog("close");
            }
        }
    });
    $dialog.dialog("open");
}

function search_Error_Keyword() {
    var $obj = $(this);
    var key = $('#error_keyword').attr('value');
    $.ajax({ url:"/supervise/ajax/", type: "POST", data:{submit: "search_Error_Keyword",
            key: key
            }, dataType:"json", success:function(data){
        if(data["status"]){
            $('#search_Error_Result').html($(data["html"]));
        }
    }});
}


//取得瀏覽器視窗高度
function getBrowserHeight() {
    if ($.browser.msie) {
        return document.compatMode == "CSS1Compat" ? document.documentElement.clientHeight :
                 document.body.clientHeight;
    } else {
        return self.innerHeight;
    }
}

//取得瀏覽器視窗寬度
function getBrowserWidth() {
    if ($.browser.msie) {
        return document.compatMode == "CSS1Compat" ? document.documentElement.clientWidth :
                 document.body.clientWidth;
    } else {
        return self.innerWidth;
    }
} 

function hide_or_show_Error_Search() {
    var $obj = $(this);
    var action = $obj.attr('action');
    if (action == 'show') {
        $('#side').show();
    } else {
        $('#side').hide();
    }
}

// function makeDocSuperviseCase(){
//     $("#IAmLoading").show();
//     $("#IAmLoading").fadeOut(15000);
//     var $obj = $(this);
//     var row_id = $obj.attr('row_id');
//     window.location = '/supervise/make_doc_supervise_case/' + row_id + '/';
// }


$(document).ready(function(){
	$("#place").change(rFindLocation);
	$("#add_New_Error").click(add_New_Error);
	$("#add_New_Supervise_Case").click(add_New_Supervise_Case);
	$("#search_Supervise_Case").click(search_Supervise_Case);
	$(".error_no").blur(error_no);
	$(".ScoreLevel").change(ScoreLevel);
	$(".change_edit_type").click(change_edit_type);
	$(".change_view_type").blur(change_view_type);
	$(".deleteGuide").click(deleteGuide);
	$(".addGuide").click(addGuide);
	$(".change_view_type_error").blur(change_view_type_error);
	$(".add_New_Error_For_Case").click(add_New_Error_For_Case);
	$(".deleteError").click(deleteError);
	$(".deleteCase").click(deleteCase);
	$("#upload_Photo_File").click(upload_Photo_File);
	$(".selectTable").click(selectTable);
	$(".showFilterCases").click(showFilterCases);
	$(".deleteErrorPhoto").click(deleteErrorPhoto);
	$(".show_Big_Error_Photo").click(show_Big_Error_Photo);
	$("#search_Error_Keyword").click(search_Error_Keyword);
    $(".hide_or_show_Error_Search").click(hide_or_show_Error_Search);
    // $("#makeDocSuperviseCase").click(makeDocSuperviseCase);

	$(".setDate").datepicker({
        buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png",
        dateFormat: "yy-mm-dd", beforeShow: function(){$(this).show();},onClose: change_view_type
    });
	$(".setDateCreate").datepicker({
        buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png",
        dateFormat: "yy-mm-dd", beforeShow: function(){$(this).show();}
    });
});

