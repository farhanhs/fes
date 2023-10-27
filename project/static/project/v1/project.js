function switchSubType(){
    var $obj = $(this);
    var type = $('#project_type option:selected').val();
    $(".subType").hide();
    $("#sub_"+type).show();
    getSubLocation(renewSubLocation, false);
}

function getSubLocation(callback, edit, project_id){
    var type = $('#project_type option:selected').val() || $('#edit_project_type option:selected').val();
    var place = $('#place option:selected').val() || $('#place option:selected').val();
    var project_id = $('#project_id').attr('value');
    if(place){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "getSubLocation", type: type, place: place, edit: edit, project_id: project_id}, dataType:"json", success:function(data){
            if(data["status"]){
                callback(data)
            }else{
                alert(data["msg"]);
            }
        }});
    }
}

function renewSubLocation(data){
    $("#SubLocation").html(data["html"]);
    $("#sort").html(data["html_sort"]);
    $("#x_coord").attr("value", "");
    $("#y_coord").attr("value", "");
    $('.setCoord').change(setCoord);
}

function addSubLocationOption(data){
    $(data["html"]).insertAfter($("#insertSubLocation"));
    $('.redaction').click(redactionProjectInfo);
    $('.updateRedaction').blur(updateProjectRedaction);
}

function cProject(){
    var $obj = $(this);
    var format = true;

    var num_check=/^-?[0-9]*$/;
    var email_check=/^[a-z0-9][-a-z0-9\.]*@([a-z0-9-]+\.)+[a-z]+$/;
    var needExistData = $(".needExist");
    for (var i=0;i<needExistData.length;i++){
        if(needExistData[i].value==""){
            alert("請檢查必填欄位！");
            format = false;
            return false;
        }
    }
    var needBeInteger = $(".integer");
    for (var i=0;i<needBeInteger.length;i++){
        if(needBeInteger[i].value!="" && !(num_check.test(needBeInteger[i].value))){
            alert("座標值須為整數！");
            format = false;
            return false;
        }
    }
    var needBeEMail = $(".email");
    for (var i=0;i<needBeEMail.length;i++){
        if(needBeEMail[i].value!="" && !(email_check.test(needBeEMail[i].value))){
            alert("請輸入正確格式之E-Mail！");
            format = false;
            return false;
        }
    }
    if(format){
        var action = $obj.attr('action');
        var plan_id = $("#plan").val();
        var year = $("#year").val();
        var project_type = $("#project_type").val();
        var project_sub_type = $("#sub_"+project_type).val();
        var name = $("#name").val();
        var bid_no = $("#bid_no").val();
        var place_id = $("#place").val();
        var allot_rate = $("#allot_rate").val();
        var sub_location_list = $(".sub_location");
        var sub_location = "";
        for (var i=0;i<sub_location_list.length;i++){
            sub_location += sub_location_list[i].value + ",";
        }
        var x_coord = $("#x_coord").val();
        var y_coord = $("#y_coord").val();
        var location = $("#location").val();
        var purchase_type_id = $("#purchase_type").val();
        var budget_type_id = $("#budget_type").val();
        var budget_sub_type_id = $("#budget_sub_type").val();
        var undertake_type_id = $("#undertake_type").val();
        var unit_id = $("#unit").val();
        var self_charge = $("#self_charge").val();
        var self_contacter = $("#self_contacter").val();
        var self_contacter_phone = $("#self_contacter_phone").val();
        var self_contacter_email = $("#self_contacter_email").val();
        var local_charge = $("#local_charge").val();
        var local_contacter = $("#local_contacter").val();
        var local_contacter_phone = $("#local_contacter_phone").val();
        var local_contacter_email = $("#local_contacter_email").val();
        var contractor_charge = $("#contractor_charge").val();
        var contractor_contacter = $("#contractor_contacter").val();
        var contractor_contacter_phone = $("#contractor_contacter_phone").val();
        var contractor_contacter_email = $("#contractor_contacter_email").val();
        var capital_ratify_budget = $("#capital_ratify_budget").val();
        var capital_ratify_local_budget = $("#capital_ratify_local_budget").val();

        var project_memo = $("#project_memo").val();
        
        $.ajax({ url:"/project/ajax/", type: "POST", data:{
                submit: "cProject", plan_id: plan_id, year: year, project_type: project_type, project_sub_type: project_sub_type, allot_rate: allot_rate,
                name: name, bid_no: bid_no, place_id: place_id, sub_location: sub_location, x_coord: x_coord, y_coord: y_coord,
                location: location, budget_type_id: budget_type_id, budget_sub_type_id: budget_sub_type_id, undertake_type_id: undertake_type_id, unit_id: unit_id,
                self_charge: self_charge, self_contacter: self_contacter, self_contacter_phone: self_contacter_phone, self_contacter_email: self_contacter_email,
                local_charge: local_charge, local_contacter: local_contacter, local_contacter_phone: local_contacter_phone, local_contacter_email: local_contacter_email,
                contractor_charge: contractor_charge, contractor_contacter: contractor_contacter, contractor_contacter_phone: contractor_contacter_phone, contractor_contacter_email: contractor_contacter_email,
                project_memo: project_memo, capital_ratify_budget: capital_ratify_budget, purchase_type_id: purchase_type_id, action: action, capital_ratify_local_budget: capital_ratify_local_budget
            }, dataType:"json", success:function(data){
            if(data["status"]){
                var msg = "新增成功！是否繼續新增工程？"
                if(confirm(msg)){
                    window.location = '/project/addproject/plan_id:' + plan_id + '/';
                    window.open('/project/basic/' + data['new_project_id']);
                }else{
                    if (!action){
                        window.location = '/project/basic/' + data['new_project_id'];
                    } else {
                        window.location = '/project/draft_project/fishery/';
                    }
                }
            }else{
                alert(data["msg"]);
            }
        }});
    }
}

function setCoord(){
    var $obj = $(this);
    var type = $obj.attr("id");
    var x = $("#"+type+" option:selected").attr('twdx');
    var y = $("#"+type+" option:selected").attr('twdy');
    $("#x_coord").attr("value", x);
    $("#y_coord").attr("value", y);
}

function dSubLocation(row_id){
    var project_id = $(".target_project").attr("id");
    var location_id = $("#sub_location_"+row_id+" option:selected").val();
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "dSubLocation", project_id: project_id, location_id: location_id}, dataType:"json", success:function(data){
        if(data["status"]){
            $("#row_"+row_id).hide();
        }else{
            alert(data["msg"]);
            $("#row_"+row_id).hide();
        }
    }});
}

function switchTable(){
    var $obj = $(this);
    var id = $obj.attr("id");
    var state = $obj.attr("state");
    if(state=="show"){
        $("." + id).hide();
        $obj.attr("state", "hide");
    }else if(state=="hide"){
        $("." + id).fadeIn();
        $obj.attr("state", "show");
    }   
}

function syncPCCProject(){
    var pcc_no = $(".edit_pcc_no").val();
    if(pcc_no==""){
        alert("請輸入工程會編號！");
        return false
    }
    $("#PCCSYNCINFO").hide();
    $("#SYNCMESSAGE").show();
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "syncPCCData", pcc_no: pcc_no}, dataType:"json", success:function(data){
        if(data["status"]){
            alert("更新成功！");
            $("#SYNCMESSAGE").hide();
            $("#PCCSYNCINFO").show();
        }else{
            alert("更新失敗！請檢查編號是否正確或是否有權限！");
            $("#SYNCMESSAGE").hide();
            $("#PCCSYNCINFO").show();
        }
    }});
}

function showPCCProject(){
    var $obj = $(this);
    var project_id = $obj.attr("project_id");
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "rPCCProject", project_id: project_id}, dataType:"json", success:function(data){
        var content = '<div class="flora" style="overflow: auto" align="center">';
        content += data["html"];
        content += "</div>";
        $dialog = $(content);
        $dialog.dialog({
            title: "工程會標案系統資訊",
            width: 900,
            height: 700,
            buttons: {
//                "同步資料": function(){
//                    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "syncPCCProjectData", project_id: project_id}, dataType:"json", success:function(data){
//                        if(data["status"]){
//                            alert("同步成功！");
//                            location.reload();
//                            $dialog.dialog("close");
//                        }else{
//                            alert(data["msg"]);
//                        }
//                    }});
//                },
                "關閉本視窗": function(){
                    $dialog.dialog("close");
                }
            }
        });
        $dialog.dialog("open");
        $(".syncFund").click(syncFundRecord);
    }});
}

function cAppropriate(){
    var $obj = $(this);
    var project_id = $obj.attr("project_id");
    var year = $obj.attr("year");

    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "cAppropriate", "project_id": project_id, "year": year}, dataType:"json", success:function(data){
        if(data["status"]){
            $(data["html"]).insertAfter($("#insertAppropriate"));
            $('.deleteProjectAppropriate').click(dAppropriate);
            $('.redaction').click(redactionProjectInfo);
            $('.updateRedaction').blur(updateProjectRedaction);
            $(".setDate").datepicker({
                buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png", dateFormat: "yy-mm-dd",
                beforeShow: function(){$(this).show();}, onClose: updateProjectRedaction
            });
        }
    }});
}

function addAllocation(){
    var $obj = $(this);
    var project_id = $obj.attr("project_id");
    var year = $obj.attr("year");

    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "addAllocation", "project_id": project_id}, dataType:"json", success:function(data){
        if(data["status"]){
            $(data["html"]).insertAfter($("#insertAllocation"));
            $('.deleteProjectAllocation').click(deleteProjectAllocation);
            $('.redaction').click(redactionProjectInfo);
            $('.updateRedaction').blur(updateProjectRedaction);
            $(".setDate").datepicker({
                buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png", dateFormat: "yy-mm-dd",
                beforeShow: function(){$(this).show();}, onClose: updateProjectRedaction
            });
        }
    }});
}

function dAppropriate(){
    var $obj = $(this);
    var appropriate_id = $obj.attr("appropriate_id");
    var stage = $obj.attr("stage");
    var msg = "是否確定刪除" + stage + "之紀錄？"
    if (confirm(msg)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "dAppropriate", appropriate_id: appropriate_id}, dataType:"json", success:function(data){
            if(data["status"]){
                $("#appropriate_"+appropriate_id).fadeOut();
            }
        }});
    }
}

function deleteProjectAllocation(){
    var $obj = $(this);
    var allocation_id = $obj.attr("allocation_id");
    var stage = $obj.attr("stage");
    var msg = "是否確定刪除" + stage + "之紀錄？"
    if (confirm(msg)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "deleteProjectAllocation", allocation_id: allocation_id}, dataType:"json", success:function(data){
            if(data["status"]){
                $("#Tr_Allocation_"+allocation_id).fadeOut();
            }
        }});
    }
}

function showAccoutingData(){
    var $obj = $(this);
    var project_id = $obj.attr("project_id");
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "rAccoutingData", project_id: project_id}, dataType:"json", success:function(data){
        var content = '<div class="flora" style="overflow: auto" align="center">';
        content += data["html"];
        content += "</div>";
        $dialog = $(content);
        $dialog.dialog({
            title: "會計系統資訊",
            width: 600,
            height: 500,
            buttons: {
//                "同步資料": function(){
//                    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "syncAccoutingData", project_id: project_id}, dataType:"json", success:function(data){
//                        if(data["status"]){
//                            alert("同步成功！");
//                            location.reload();
//                            $dialog.dialog("close");
//                        }else{
//                            alert(data["msg"]);
//                        }
//                    }});
//                },
                "關閉本視窗": function(){
                    $dialog.dialog("close");
                }
            }
        });
        $dialog.dialog("open");
        $(".syncFund").click(syncFundRecord);
    }});
}

function showPCCFundingDetail(){
    var $obj = $(this);
    var project_id = $obj.attr("project_id");
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "rFundingDetail", project_id: project_id}, dataType:"json", success:function(data){
        var content = '<div class="flora" style="overflow: auto" align="center">';
        content += data["html"];
        content += "</div>";
        $dialog = $(content);
        $dialog.dialog({
            title: "工程撥款明細表",
            width: 700,
            height: 500,
            buttons: {
                "匯出檔案": function(){
                    $('textarea[name=body]').val($("#detail_list").html());
                    $('form#xxx').submit();
                },
                "關閉本視窗": function(){
                    $dialog.dialog("close");
                }
            }
        });
        $dialog.dialog("open");
        $(".syncFund").click(syncFundRecord);
    }});
}

function showPCCFundRecord(){
    var $obj = $(this);
    var project_id = $obj.attr("project_id");
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "rPCCFundRecord", project_id: project_id}, dataType:"json", success:function(data){
        if(data["record"]){
            var content = '<div class="flora" style="overflow: auto" align="center">';
            content += data["html"];
            content += "</div>";
            $dialog = $(content);
            $dialog.dialog({
                title: "工程會標案系統金額資訊",
                width: 700,
                height: 500,
                buttons: {
                    "關閉本視窗": function(){
                        $dialog.dialog("close");
                        location.reload();
                    }
                }
            });
            $dialog.dialog("open");
            $(".syncFund").click(syncFundRecord);
        }else{
            var msg = "此工程尚未與工程會標案管理系統同步。請至工程基本資料填寫工程會編號以讀取標案管理系統資訊。";
            alert(msg);
        }
    }});
}

function syncFundRecord(){
    var $obj = $(this);
    var relay_fund_id = $obj.attr("relay_fund_id");
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "syncFundRecord", relay_fund_id: relay_fund_id}, dataType:"json", success:function(data){
        if(data["status"]){
            $obj.fadeOut();
        }
    }});
}

function dProjectFundRecord(){
    var $obj = $(this);
    var fundrecord_id = $obj.attr("fundrecord_id");
    var stage = $obj.attr("stage");
    var msg = "是否確定刪除" + stage + "之紀錄？"
    if (confirm(msg)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "dProjectFundRecord", fundrecord_id: fundrecord_id}, dataType:"json", success:function(data){
            if(data["status"]){
				$("#fundrecord_"+fundrecord_id).fadeOut();
                alert("刪除成功。");
            }
        }});
    }
}

function reserveProject(){
    var $obj = $(this);
    var project_id = $obj.attr("project_id");
    var amount = $("#amount").val();
    if(amount==""){
        alert("請填寫保留數。");
    }else{
        var num_check=/^[0-9]*$/;
        var float_check=/^[1-9]d*.d*|0.d*[1-9]d*$/;
        var date_check=/^(([1-9]\d{0,3}|0)\-\d{2}\-\d{2})|(([1-9]\d{0,3}|0)\.\d{2}\.\d{2})|(([1-9]\d{0,3}|0)\/\d{2}\/\d{2})$/;
        var apply_date = $("#apply_date").val();
        var reserve_date = $("#reserve_date").val();
        var allocation = $("#allocation").val();
        var un_allocation = $("#un_allocation").val();
        var reason = $('#reason').val();
        var prove = $('#prove').val();
        var memo = $('#memo').val();
        var format = true;
        if(!(float_check.test(amount)) && !(num_check.test(amount))){
            var message = '申請保留數格式錯誤！';
            format = false;
            alert(message);
        }
        if(format){
            $.ajax({ url:"/project/ajax/", type: "POST", data:{
                    submit: "runReserveProject", project_id: project_id, amount: amount, apply_date: apply_date, reserve_date: reserve_date,
                    allocation: allocation, un_allocation: un_allocation, reason: reason, prove: prove, memo: memo
                }, dataType:"json", success:function(data){
                    if(data["status"]){
                        alert("新增成功!");
                        window.location = '/project/fund/' + project_id;
                    }
            }});
        }
    }
}

function dReserve(){
    var $obj = $(this);
    var reserve_id = $obj.attr('reserve_id');
    message = '確定撤銷跨年並刪除此年度會計資料？';
    if(confirm(message)) {
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "dReserve", reserve_id: reserve_id}, dataType:"json", success:function(data){
            if (data['status'] != true){
                alert(data['message']);
            } else {
				$("#budget_"+data['year']).fadeOut();
                alert("刪除成功！");
            }
        }});
    }
    return false;
}

function showPCCProgress(){
    var $obj = $(this);
    var project_id = $obj.attr("project_id");
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "rPCCProgress", project_id: project_id}, dataType:"json", success:function(data){
        if(data["record"]){
            var content = '<div class="flora" style="overflow: auto" align="center">';
            content += data["html"];
            content += "</div>";
            $dialog = $(content);
            $dialog.dialog({
                title: "工程會標案系統進度資訊",
                width: 700,
                height: 500,
                buttons: {
                    "關閉本視窗": function(){
                        $dialog.dialog("close");
                        location.reload();
                    }
                }
            });
            $dialog.dialog("open");
            $(".syncProgress").click(syncProgress);
        }else{
            var msg = "此工程尚未與工程會標案管理系統同步。請至工程基本資料填寫工程會編號以讀取標案管理系統資訊。";
            alert(msg);
        }
    }});
}

function syncProgress(){
    var $obj = $(this);
    var relay_progress_id = $obj.attr("relay_progress_id");
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "syncProgress", relay_progress_id: relay_progress_id}, dataType:"json", success:function(data){
        if(data["status"]){
            $obj.fadeOut();
        }
    }});
}

function dProgress(){
    var $obj = $(this);
    var progress_id = $obj.attr("progress_id");
    var stage = $obj.attr("stage");
    var msg = "是否確定刪除" + stage + "之紀錄？"
    if (confirm(msg)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "dProgress", progress_id: progress_id}, dataType:"json", success:function(data){
            if(data["status"]){
				$("#progress_"+progress_id).fadeOut();
                alert("刪除成功。");
            }
        }});
    }
}

function ShowBatchEdit(){
    var $obj = $(this);
    var show = $('#BatchEdit').attr("show");
    if (show=="False") {
        $('#BatchEdit').show();
        $('#BatchEdit').attr("show", 'True')
    } else {
        $('#BatchEdit').hide();
        $('#BatchEdit').attr("show", 'False')
    }
}

function BatchEdit_Plan(){
    var $obj = $(this);
    var p_list = $obj.attr("p_list");
    var p_list_count = $obj.attr("p_list_count");
    var plan_no = $obj.val();
    var plan_name = $("#BatchEdit_Plan option:selected").attr("name");
    var msg = "是否確定將如下  " + p_list_count + "件  結果之『所屬計畫』批次修改為(" + plan_name + ")？"
    if (plan_no!=0 && confirm(msg)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "BatchEdit_Plan", p_list: p_list, plan_no: plan_no}, dataType:"json", success:function(data){
            if(data["status"]){
                alert("修改成功，已將  " + p_list_count + "件  結果修改完畢，請重新搜尋後確認。");
                $('#BatchEdit_info').show();
            }
        }});
    }
}

function ChangeBgcolor_over() {
    var $obj = $(this);
    var plan_id = $obj.attr("plan_id");
    $('#PlanTable_'+plan_id).attr("bgcolor", "#AFFFB0")
}

function ChangeBgcolor_out() {
    var $obj = $(this);
    var plan_id = $obj.attr("plan_id");
    $('#PlanTable_'+plan_id).attr("bgcolor", "")
}

function deletePlan(){
    var $obj = $(this);
    var plan_name = $obj.attr('plan_name');
    var plan_id = $obj.attr('plan_id');
    var message = '您確定要刪除計畫『 '+plan_name+' 』嗎?  此計畫已確認"無"下層計畫 !';
    if (confirm(message)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "deletePlan", plan_id: plan_id, plan_name: plan_name}, dataType:"json", success:function(data){
            if(data["status"]){
                window.location = '/project/replan/' + data['up_plan_id'];
                alert('刪除計畫成功');
            } else {
                alert(data['message']);
            }
        }});
    } else {
        return false;
    }
}

var sortPlan = function(){
    var $obj = $(this);
    var plan_name = $obj.attr('plan_name');
    var plan_id = $obj.attr('plan_id');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "getPlanListInTable", plan_id: plan_id, plan_name: plan_name}, dataType:"json", success:function(data){
        var html = '<div class="flora" style="overflow: auto"><table><tr><td>';
        html += '<h1>欲移動計畫：<br>『' + plan_name + '』</h1>';
        html += '<br><h2>第一步、選擇您要移動的位置</h2>';
        html += data['table'];
        html += '<br><h2>第二步、選擇層級關係</h2>';
        html += '　　　<div class="level_radio_table"><input id="relation_radio" name="relation_radio" type="radio" value="theSameLevel">同階層　　';
        html += '<input id="relation_radio" name="relation_radio" type="radio" value="isSubLevel">下層計畫</div>';
        html += '<br><br><br><input class="updatePlanSort" type="submit" value="確定移動" /><br><br><br>';
        html += '</td></tr></table><div style="display: none;" id="wantSortPlan" value="' + plan_id + '"></div></div>';
        $dialog = $(html);
        $dialog.dialog({
            title: '階層選擇視窗',
            width: 700,
            height: 600,
            buttons: {
                '關閉本視窗': function(){
                    $dialog.dialog('close');
                }
            }
        });
        $dialog.dialog('open');
        $('.updatePlanSort').click(updatePlanSort);
    }});
}

var updatePlanSort = function(){
    var plan_radio = $('.plan_radio_table input[@type=radio]:checked').val();
    if (!plan_radio){
        alert('請選擇欲移動位置');
        return false;
    }
    var relation_radio = $('.level_radio_table input[@type=radio]:checked').val();
    if (!relation_radio){
        alert('請選擇層級關係');
        return false;
    }
    var wantSortPlan = $('#wantSortPlan').attr('value');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "updatePlanSort", plan_radio: plan_radio, relation_radio: relation_radio, wantSortPlan: wantSortPlan}, dataType:"json", success:function(data){
        if(data["status"]){
            window.location = '/project/replan/' + wantSortPlan;
            window.location.reload(true);
            alert('移動完成');
        }
    }});
}

function Show_Plan_Info(){
    var $obj = $(this);
    var plan_id = $obj.attr('plan_id');
    var field_name = $obj.attr('field_name');
    $('#Show_Plan_Info_'+field_name+'_'+plan_id).hide();
    $('#Edit_Plan_Info_'+field_name+'_'+plan_id).show().focus();
}

function Hide_Plan_Info(){
    var $obj = $(this);
    var plan_id = $obj.attr('plan_id');
    var field_name = $obj.attr('field_name');
    var float_check=/^[0-9]+$/;
    var value = $obj.attr('value');
    var old_value = $obj.attr('old_value');
    var input_type = $obj.attr('input_type');
    if (value != old_value){
        if (input_type=='float' && !(float_check.test(value)) && value!=''){
            alert('請填入數字');
            $obj.attr('value', old_value)
        } else {
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "updatePlanInfo", field_name: field_name,
                    value: value, plan_id: plan_id},
                    dataType:"json", success:function(data){
                if(data["status"]){
                    if (field_name=='budget_type'){
                        var return_value = data['return_value'];
                        var return_value_2 = data['return_value_2'];
                        $obj.attr('value', return_value)
                        $obj.attr('old_value', return_value)
                        $("#Show_Plan_Info_"+field_name+"_"+plan_id).html(return_value_2.replace(/\n/gi, '<br>'));
                    } else {
                        var return_value = data['return_value'];
                        $obj.attr('value', return_value)
                        $obj.attr('old_value', return_value)
                        if (input_type=='float'){
                            $("#Show_Plan_Info_"+field_name+"_"+plan_id).html(TransformThousands(return_value));
                        } else {
                            $("#Show_Plan_Info_"+field_name+"_"+plan_id).html(return_value.replace(/\n/gi, '<br>'));
                        }
                    }
                } else {
                    alert(data['msg']);
                    $obj.attr('value', old_value);
                }
            }});
        }
    }
    $('#Show_Plan_Info_'+field_name+'_'+plan_id).show();
    $('#Edit_Plan_Info_'+field_name+'_'+plan_id).hide();
}


function Show_Budget_Info(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var field_name = $obj.attr('field_name');
    $('#Show_Budget_Info_'+field_name+'_'+row_id).hide();
    $('#Edit_Budget_Info_'+field_name+'_'+row_id).show().focus();
}

function Hide_Budget_Info(){
    var $obj = $(this);
    var year = $('#year').attr('value');
    var row_id = $obj.attr('row_id');
    var table_name = $obj.attr('table_name');
    var field_name = $obj.attr('field_name');
    var float_check=/^[0-9]+$/;
    var value = $obj.attr('value');
    var old_value = $obj.attr('old_value');
    var input_type = $obj.attr('input_type');
    if (value != old_value){
        if (input_type=='float' && !(float_check.test(value)) && value!=''){
            alert('請填入數字');
            $obj.attr('value', old_value)
        } else {
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "updateBudgetInfo", field_name: field_name,
                    value: value, row_id: row_id, table_name: table_name, input_type: input_type, year: year},
                    dataType:"json", success:function(data){
                if(data["status"]){
                    var return_value = data['return_value'];
                    $obj.attr('value', return_value)
                    $obj.attr('old_value', return_value)
                    if (input_type=='float'){
                        $("#Show_Budget_Info_"+field_name+"_"+row_id).html(TransformThousands(return_value));
                    } else {
                        $("#Show_Budget_Info_"+field_name+"_"+row_id).html(return_value.replace(/\n/gi, '<br>'));
                    }
                    if (field_name=='contract') {
                        var return_value = data['manage'];
                        $('#Edit_Budget_Info_manage_'+row_id).attr('value', return_value)
                        $('#Edit_Budget_Info_manage_'+row_id).attr('old_value', return_value)
                        $("#Show_Budget_Info_manage_"+row_id).html(TransformThousands(return_value).replace(/\n/gi, '<br>'));
                        
                    }
                    if (input_type=='float'){
                        if (table_name=='Budget'){ var change_id = $obj.attr('fund_id'); } else { var change_id = row_id; }
                        $('#rTotalProjectBudget_'+change_id).html(TransformThousands(data['rTotalProjectBudget']));
                        $('#rTotalAppropriatebyLastYear_'+change_id).html(TransformThousands(data['rTotalAppropriatebyLastYear']));
                        $('#rShouldPayThisYear_'+change_id).html(TransformThousands(data['rShouldPayThisYear']));
                        $('#rTotalAppropriatebyThisYear_'+change_id).html(TransformThousands(data['rTotalAppropriatebyThisYear']));
                        $('#rTotalProjectNotPayThisYear_'+change_id).html(TransformThousands(data['rTotalProjectNotPayThisYear']));
                    }
                } else {
                    alert(data['msg']);
                    $obj.attr('value', old_value);
                }
            }});
        }
    }
    $('#Show_Budget_Info_'+field_name+'_'+row_id).show();
    $('#Edit_Budget_Info_'+field_name+'_'+row_id).hide();
}


var addPlan = function(){
    var $obj = $(this);
    var plan_id = $obj.attr('plan_id');
    var lv = $obj.attr('lv');
    if (lv == 'equal'){
        var lv_msg = '同層';
    } else {
        var lv_msg = '下層';
    }
    var html = '<div class="flora" style="overflow: auto"><table class="add_plan_table"><tr><td>';
    html += '<h1>新增『' + lv_msg + '』計畫名稱：</h1><br>';
    html += '<input mother="' + plan_id + '" lv="' + lv + '" id="new_plan_name" type="text" name="new_plan_name" maxlength="128" size="60" value=""/>';
    html += '<br><input id="addPlan_Button" type="submit" value="確定新增" /><td><tr><table></div>';
    $dialog = $(html);
    $dialog.dialog({
        title: '新增計畫視窗',
        width: 600,
        height: 250,
        buttons: {
            '關閉本視窗': function(){
                $dialog.dialog('close');
            }
        }
    });
    $dialog.dialog('open');
    $('#addPlan_Button').click(addPlan_Button);
}

var addPlan_Button = function(){
    var text = $('#new_plan_name');
    var name = text.attr('value');
    
    if (name==""){
        alert('請填寫計畫名稱');
    } else {
        var lv = text.attr('lv');
        var plan_id = text.attr('mother');
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "addPlan", lv: lv, plan_id: plan_id, name: name},
                dataType:"json", success:function(data){
            if(data["status"]){
                alert('新增成功!!');
                window.location = '/project/replan/' + data["new_plan_id"];
            } else {
                alert(data['msg']);
            }
        }});
    }
}


var addPlanBudget = function(){
    var $obj = $(this);
    var plan_id = $obj.attr('plan_id');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "addPlanBudget", plan_id: plan_id},
            dataType:"json", success:function(data){
        if(data["status"]){
            location.reload();
            window.location = '/project/replan/' + plan_id + '/#tag_addBudget';
        } else {
            alert(data['msg']);
        }
    }});
}


var deletePlanBudget = function(){
    var $obj = $(this);
    var plan_id = $obj.attr('plan_id');
    var year = $obj.attr('year');
    if(confirm('確定要刪除『' + year + '年度』之預算嗎？(此動作不可恢復)')){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "deletePlanBudget", plan_id: plan_id},
                dataType:"json", success:function(data){
            if(data["status"]){
                $("#PlanBudget_tr_"+plan_id).remove();
                alert('刪除成功!!');
            } else {
                alert(data['msg']);
            }
        }});
    }
}

var editProjectListBudget = function(){
    var $obj = $(this);
    var plan_id = $obj.attr('plan_id');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "get_editProjectListBudget_Option", plan_id: plan_id}, dataType:"json", success:function(data){
        var content = '';
        content += data["html"];
        $dialog = $(content);
        $dialog.dialog({
            title: "篩選器",
            width: 600,
            height: 320
        });
        $dialog.dialog("open");
        $("#editProjectListBudget_Button").click(editProjectListBudget_Button);
    }});
}

var editProjectListBudget_Button = function(){
    var year = $('#year').attr('value');
    var plan_id = $('#plan_id').attr('plan_id');
    var sub_plan = $('#sub_plan').attr('value');
    var budget_sub_type = $('#budget_sub_type').attr('value');
    var undertake_type = $('#undertake_type').attr('value');
    window.location = '/project/edit_project_list_budget/' + plan_id + '/' + year + '/'+ sub_plan + '/' + budget_sub_type + '/' + undertake_type + '/';
}

var autoSum = function(){
    var $obj = $(this);
    var plan_id = $obj.attr('plan_id');
    var title = $obj.attr('title');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "updateAutoSum", plan_id: plan_id},
            dataType:"json", success:function(data){
        if(data["status"]){
            window.location = '/project/replan/' + plan_id;
        } else {
            alert(data['msg']);
        }
    }});
}

var Filter_Project_Type = function(){
    var $obj = $(this);
    var type_id = $obj.attr('type_id');
    var type = $obj.attr('type');
    var now = $obj.attr('now');
    if (now=='show'){
        $obj.attr('now', 'hide')
        $("#"+type+"_light1_"+type_id).attr('src', '/media/project/image/red_light.png')
        $("#"+type+"_light2_"+type_id).attr('src', '/media/project/image/red_light.png')
        $("#"+type+"_light1_"+type_id).attr('title', '顯示此類別')
        $("#"+type+"_light2_"+type_id).attr('title', '顯示此類別')
        $("."+type+"_"+type_id).hide();
        $("."+type+"_"+type_id).attr('tag', 'hide_project'); 
    } else {
        $obj.attr('now', 'show')
        $("#"+type+"_light1_"+type_id).attr('src', '/media/project/image/green_light.png')
        $("#"+type+"_light2_"+type_id).attr('src', '/media/project/image/green_light.png')
        $("#"+type+"_light1_"+type_id).attr('title', '隱藏此類別')
        $("#"+type+"_light2_"+type_id).attr('title', '隱藏此類別')
        $("."+type+"_"+type_id).show();
        $("."+type+"_"+type_id).attr('tag', 'show_project');
    }
    if (countProjectTag()){
        $("#filter_project_num").html(countProjectTag());
    } else {
        $("#filter_project_num").html("0");
    }
}


var getMorePlaninfo = function(){
    var $obj = $(this);
    var now = $obj.attr('now');
    if (now=='show'){
        $obj.attr('now', 'hide')
        $(".gray_color").hide();
    } else {
        $obj.attr('now', 'show')
        $(".gray_color").show();
    }
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

function countProjectTag() {
    var matches = document.body.innerHTML.match(/show_project/gi);
    return matches ? matches.length : 0;
}

function cReserve(){
    var url = $(this).attr("href");
    window.location = url;
}

function Change_Backlight_over() {
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var $obj_td = $('#Backlight_tr_'+row_id+' td');
    for (var i = 1;i <= 21;i++){
        $('#td_'+i+'_'+row_id).attr("bgcolor", "#FEFFCD")
    }
    var title = $obj.attr('title');
    var t0 = $('.sData').offset().top;
    var t1 = t0 + $('.sData').height();

    $('td[field_name=plan_no]').each(function(){
        var $td = $(this);
        var title = $td.attr('title');
        var td_top = $td.offset().top;
        var td_bottom = td_top + $td.height();
        if ((t0 <= td_top && td_top < t1) || (t0 <= td_bottom && td_bottom < t1)) {
            var $div = $('<div style="position: absolute; z-index: 300; top: '+Math.ceil((td_top+td_bottom)/2)
                +'px; left: '+(mouseX+150)+'px;" class="plan_no_div">' 
                + '<table style="border-collapse: collapse;" border="1" cellpadding="2" cellspacing="2">'
                + '<tr><td bgcolor="#FFFFFF">' + title + '</td></tr></table></div>');
            $('#id_body').prepend($div);
        }
    })

}

function Change_Backlight_out() {
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    for (var i = 1;i <= 21;i++){
        $('#td_'+i+'_'+row_id).attr('bgcolor', $('#td_'+i+'_'+row_id).attr('old_bgcolor'))
    }
    $('.plan_no_div').remove();
}

function setChaseProject(){
    var $obj = $(this);
    var project_id = $obj.attr('value');
    var item = $('#checkbox_'+project_id);
    var checked = item.attr('checked');
    var check = item.attr('check');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "setChaseProject", project_id: project_id},
            dataType:"json", success:function(data){
        if (data['status'] != true){
            alert(data['message']);
        } else {
            if (check == 'check') {
                $('#setChaseProject_'+project_id).html('');
                item.attr('check', '');
            } else {
                $('#setChaseProject_'+project_id).html('<span class="style2">追蹤進度</span>');
                item.attr('check', 'check');
            }
        }
    }});
}

function setAllChaseProject(){
    var $obj = $(this);
    var project_ids = $obj.attr('value').replace('[', '').replace(']', '').split(', ');
    var checked = $obj.attr('checked');
    for (var i=0;i<project_ids.length;i++){
        var item = $('.checkbox_'+project_ids[i]);
        if (checked && !item.attr('checked')){
            item.click();
        } else if (!checked && item.attr('checked')) {
            item.click();
        }
    }
}

function addNewChase(){
    var msg = '你確定要重新開始新的《追蹤紀錄》嗎?';
    var msg2 = '是否要自動匯入上一次所有的追蹤工程案?';
    var user_id = $(this).attr('user_id');
    alert(user_id);
    if(confirm(msg)){
        if(confirm(msg2)){
            var auto_import = 'True';
        } else {
            var auto_import = 'False';
        }
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "addNewChase", auto_import: auto_import, user_id: user_id},
                dataType:"json", success:function(data){
            if (data['status'] == true){
                window.location = '/project/county_chase/';
            }
        }});
    }
}

function deleteLastChase(){
    var msg = '你確定要清除這一次的追蹤嗎? (所有填寫內容將會被刪除，且無法恢復!!)';
    if(confirm(msg)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "deleteLastChase"},
                dataType:"json", success:function(data){
            if (data['status'] == true){
                window.location = '/project/county_chase/';
            }
        }});
    }
}

function ShowChaseProject(){
    var $obj = $(this);
    var place_id = $obj.attr('place_id');
    var type = $obj.attr('type');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "ShowChaseProject", place_id: place_id, type: type}, dataType:"json", success:function(data){
        var html = data["html"];
        $dialog = $(html);
        $dialog.dialog({
            title: "工程資訊",
            width: 900,
            height: 500,
            buttons: {
                "關閉本視窗": function(){
                    $dialog.dialog("close");
                }
            }
        });
        $dialog.dialog("open");
    }});
}

function updateChartNewUpdateInfoDialog(){
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "updateChartNewUpdateInfoDialog"}, dataType:"json", success:function(data){
        var html = data["html"];
        $dialog = $(html);
        $dialog.dialog({
            title: "更新資訊",
            width: 900,
            height: 500,
            buttons: {
                "關閉本視窗": function(){
                    $dialog.dialog("close");
                }
            }
        });
        $dialog.dialog("open");
        $('#updateChartNewUpdateInfo').click(updateChartNewUpdateInfo);
    }});
}

function updateChartNewUpdateInfo(){
    var msg = '確定將資料清空嗎(按取消可保留圖示)';
    if(confirm(msg)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "updateChartNewUpdateInfo"},
                dataType:"json", success:function(data){
            if (data['status'] == true){
                $dialog.dialog("close");
                $('#updateChartNewUpdateInfoDialog').fadeOut();
            }
        }});
    }
}

function id_vouch_date_ub(){
    var $obj = $(this);
    $("#id_vouch_date_lb").attr('value', $obj.attr('value'))
}

function setCheckForClose(){
    var $obj = $(this);
    var chase_id = $obj.attr('chase_id');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "setCheckForClose", chase_id: chase_id},
            dataType:"json", success:function(data){
        if (data['status'] == true){
            $obj.html(data['msg']);
            if (data['msg'] == '點擊確定'){
                $("#setFalseForClose_"+chase_id).show();
                $("#td_setCheckForClose_"+chase_id).attr('bgcolor', '#FFB0AF')
            } else {
                $("#setFalseForClose_"+chase_id).hide();
                $("#td_setCheckForClose_"+chase_id).attr('bgcolor', '#91FF92')
            }
        }
    }});
}

function setFalseForClose(){
    var $obj = $(this);
    var chase_id = $obj.attr('chase_id');
    var msg = '駁回申請後若需『確認完工』需請工程師重新提出申請，您確定駁回嗎?';
    if(confirm(msg)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "setFalseForClose", chase_id: chase_id},
                dataType:"json", success:function(data){
            if (data['status'] == true){
                alert('已駁回申請');
                $("#setCheckForClose"+chase_id).hide();
                $("#setFalseForClose_"+chase_id).hide();
            }
        }});
    }
}

function setCheckForComplete(){
    var $obj = $(this);
    var chase_id = $obj.attr('chase_id');
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "setCheckForComplete", chase_id: chase_id},
            dataType:"json", success:function(data){
        if (data['status'] == true){
            $obj.html(data['msg']);
            if (data['msg'] == '點擊確定'){
                $("#setFalseForComplete_"+chase_id).show();
                $("#td_setCheckForComplete_"+chase_id).attr('bgcolor', '#FFB0AF')
            } else {
                $("#setFalseForComplete_"+chase_id).hide();
                $("#td_setCheckForComplete_"+chase_id).attr('bgcolor', '#91FF92')
            }
        }
    }});
}

function setFalseForComplete(){
    var $obj = $(this);
    var chase_id = $obj.attr('chase_id');
    var msg = '駁回申請後若需『確認填寫完畢』需請工程師重新提出申請，您確定駁回嗎?';
    if(confirm(msg)){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "setFalseForComplete", chase_id: chase_id},
                dataType:"json", success:function(data){
            if (data['status'] == true){
                alert('已駁回申請');
                $("#setCheckForComplete"+chase_id).hide();
                $("#setFalseForComplete_"+chase_id).hide();
            }
        }});
    }
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
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "updateChaseInfo", chase_id: chase_id, 
                field_name: field_name,table_name: table_name, value: value},
                    dataType:"json", success:function(data){
                if (data['status'] == true){
                    var return_value = data['return_value'];
                    $obj.attr('value', return_value)
                    $obj.attr('old_value', return_value)
                    if (input_type=='float'){
                        $("#Show_Chase_Info_"+field_name+"_"+chase_id).html(TransformThousands(return_value));
                    } else {
                        $("#Show_Chase_Info_"+field_name+"_"+chase_id).html(return_value.replace(/\n/gi, '<br>'));
                    }
                } else {
                    alert(data['msg']);
                    $obj.attr('value', old_value);
                }
            }});
        }
    }
    $('#Show_Chase_Info_'+field_name+'_'+chase_id).show();
    $('#Edit_Chase_Info_'+field_name+'_'+chase_id).hide();
}


function makeExcelButton(){
    $("#IAmLoading").show();
    $("#IAmLoading").fadeOut(15000);
}


function hideNotImportantInfo(){
    alert('將隱藏不需要的資訊，如需顯示請"重新整理"即可');
    $("#ChaseTable").show();
    $(".NotImportant").hide();
}

var Show_Memo_Info = function(){
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var field_name = $obj.attr('field_name');
    $('#Show_Memo_Info_'+field_name+'_'+project_id).hide();
    $('#Edit_Memo_Info_'+field_name+'_'+project_id).show().focus();
}

var Hide_Memo_Info = function(){
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
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
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "updateMemoInfo", project_id: project_id,
                field_name: field_name,table_name: table_name, value: value},
                    dataType:"json", success:function(data){
                if (data['status'] == true){
                    var return_value = data['return_value'];
                    $obj.attr('value', return_value)
                    $obj.attr('old_value', return_value)
                    if (input_type=='float'){
                        $("#Show_Memo_Info_"+field_name+"_"+project_id).html(TransformThousands(return_value));
                    } else {
                        $("#Show_Memo_Info_"+field_name+"_"+project_id).html(return_value.replace(/\n/gi, '<br>'));
                    }
                } else {
                    alert(data['msg']);
                    $obj.attr('value', old_value);
                }
            }});
        }
    }
    $('#Show_Memo_Info_'+field_name+'_'+project_id).show();
    $('#Edit_Memo_Info_'+field_name+'_'+project_id).hide();
}


var show_upload_Field = function(){
    $('#upload_Field').show();
}

var upload_DocumentFile = function () {
    var $obj = $(this);
    var project_id = $obj.attr('project_id');
    var file = $('#newfile_file_'+project_id).attr('value');
    var date = $('#newfile_date_'+project_id).attr('value');
    var no = $('#newfile_no_'+project_id).attr('value');
    var memo = $('#newfile_memo_'+project_id).attr('value');

    if (!file){
        alert('請選擇檔案!!!')
        return false;
    }

    if (!date){
        alert('發文日期為必填欄位!!!')
        return false;
    }

    if (!confirm('確定上傳 '+file+' ?  按下確定後開始上傳，請勿關閉此頁面!!')){
        return false;
    }

    $.ajaxFileUpload({
        url:'/project/upload_document_file/'+project_id+'/?date='+date+'&no='+no+'&memo='+memo,
        async: true,
        fileElementId: 'newfile_file_'+project_id,
        dataType: 'json',
        success: function (json, status) {
            if (json['status'] == false){
                alert(json['message']);
            } else {
                $('#newfile_file_'+project_id).attr('value', '');
                $('#newfile_date_'+project_id).attr('value', '');
                $('#newfile_no_'+project_id).attr('value', '');
                $('#newfile_memo_'+project_id).attr('value', '');
                $('#upload_Field').hide();
                $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "makeNewFileTr", id: json["id"]},
                        dataType:"json", success:function(data){
                    if (data['status'] == true){
                        $(data["html"]).insertBefore($("#File_Insert_Place"));
                        $('#tr_file_document_'+ json["id"] +' .pleaseUseRightClick').click(pleaseUseRightClick);
                        $('#tr_file_document_'+ json["id"] +' .deleteDocumentFile').click(deleteDocumentFile);
                        $('#tr_file_document_'+ json["id"] +' .Show_File_Info').click(Show_File_Info);
                        $('#tr_file_document_'+ json["id"] +' .Hide_File_Info').blur(Hide_File_Info);
                    }
                }});
            }
        },
        error: function (json, status, e) {
        }
    });
    return false;
}

var pleaseUseRightClick = function(){
    alert('請使用滑鼠右鍵，"IE:另存目標"　or　"FireFox:鏈結另存新檔"　or　"Chrome:另存連結為" !!');
    return false;
}

var deleteDocumentFile = function(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    if (!confirm('確定刪除文件??')){
        return false;
    }
    $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "deleteDocumentFile", row_id: row_id},
            dataType:"json", success:function(data){
        if (data['status'] == true){
            $('#tr_file_document_'+row_id).remove();
        }
    }});
}

var Show_File_Info = function(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var field_name = $obj.attr('field_name');
    $('#Show_File_Info_'+field_name+'_'+row_id).hide();
    $('#Edit_File_Info_'+field_name+'_'+row_id).show().focus();
}

var Hide_File_Info = function(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
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
            $.ajax({ url:"/project/ajax/", type: "POST", data:{submit: "updateFileInfo", row_id: row_id,
                field_name: field_name,table_name: table_name, value: value},
                    dataType:"json", success:function(data){
                if (data['status'] == true){
                    var return_value = data['return_value'];
                    $obj.attr('value', return_value)
                    $obj.attr('old_value', return_value)
                    if (input_type=='float'){
                        $("#Show_File_Info_"+field_name+"_"+row_id).html(TransformThousands(return_value));
                    } else {
                        $("#Show_File_Info_"+field_name+"_"+row_id).html(return_value.replace(/\n/gi, '<br>'));
                    }
                } else {
                    alert(data['msg']);
                    $obj.attr('value', old_value);
                }
            }});
        }
    }
    $('#Show_File_Info_'+field_name+'_'+row_id).show();
    $('#Edit_File_Info_'+field_name+'_'+row_id).hide();
}


function add_Draft_Project(){
    var $obj = $(this);
    var format = true;
    var next_url = $obj.attr('next_url');
    var action = $obj.attr('action');
    var del_project_id = $obj.attr('del_project_id');
    var num_check=/^-?[0-9]*$/;
    var needExistData = $(".needExist");
    for (var i=0;i<needExistData.length;i++){
        if(needExistData[i].value==""){
            alert("請檢查必填欄位！");
            format = false;
            return false;
        }
    }
    var needBeInteger = $(".integer");
    for (var i=0;i<needBeInteger.length;i++){
        if(needBeInteger[i].value!="" && !(num_check.test(needBeInteger[i].value))){
            alert("座標值須為整數！");
            format = false;
            return false;
        }
    }
    var sort = $("#sort").attr('value');
    if (!sort || sort=='undefined'){
        alert("請選擇優先順序！");
        format = false;
        return false;
    }

    if(format){
        var year = $("#year").val();
        var plan_id = $("#plan").val();
        var project_id = $("#exProject").val();
        var name = $("#name").val();
        var capital_ratify_budget = $("#capital_ratify_budget").val();
        var self_money = $("#self_money").val();
        var local_money = $("#local_money").val();
        var project_type = $("#project_type").val();
        var project_sub_type = $("#sub_"+project_type).val();
        var place_id = $("#place").val();
        var sub_location_list = $(".sub_location");
        var sub_location = "";
        for (var i=0;i<sub_location_list.length;i++){
            sub_location += sub_location_list[i].value + ",";
        }
        var purchase_type_id = $("#purchase_type").val();
        var budget_sub_type_id = $("#budget_sub_type").val();
        var undertake_type_id = $("#undertake_type").val();
        var unit_id = $("#unit").val();
        var info = $("#info").val();
        var review_results = $("#review_results").val();
        var design = $("#design").val();
        var fish_boat = $("#fish_boat").val();
        var real_fish_boat = $("#real_fish_boat").val();
        var other_memo = $("#other_memo").val();
        var fect = $("#fect").val();
        var memo = $("#memo").val();
        var type = $obj.attr('draft_type');
        var sort = $("#sort").attr('value');
        $.ajax({ url:"/project/ajax/", type: "POST", data:{
                submit: "add_Draft_Project", plan_id: plan_id, year: year, name: name, capital_ratify_budget: capital_ratify_budget,
                self_money: self_money, local_money: local_money, project_type: project_type, project_sub_type: project_sub_type,
                place_id: place_id, sub_location: sub_location, purchase_type_id: purchase_type_id,
                budget_sub_type_id: budget_sub_type_id, undertake_type_id: undertake_type_id, unit_id: unit_id,
                info: info, review_results: review_results, design: design, type: type, sort: sort,
                fish_boat: fish_boat, real_fish_boat: real_fish_boat, project_id: project_id,
                other_memo: other_memo, fect: fect, memo: memo, action: action, del_project_id: del_project_id
            }, dataType:"json", success:function(data){
            if(data["status"]){
                var msg = "新增成功！"
                window.location = next_url;
//                $('#name').attr('value', '')
//                $('#Is_Inherit_Project').attr('value', 'False')
//                $('#Search_Project_Name').attr('value', '')
//                $('#capital_ratify_budget').attr('value', '')
//                $('#self_money').attr('value', '')
//                $('#local_money').attr('value', '')
//                $('#info').attr('value', '')
//                $('#review_results').attr('value', '')
//                $('#design').attr('value', '')
//                $('#fish_boat').attr('value', '')
//                $('#real_fish_boat').attr('value', '')
//                $('#other_memo').attr('value', '')
//                $('#fect').attr('value', '')
//                $('#memo').attr('value', '')
//                if(confirm(msg)){
//                    $('#Draft_Table').show();
//                    $('#Show_Draft_Table').attr('show_type', 'hide')
//                }else{
//                    $('#Draft_Table').hide();
//                    $('#Show_Draft_Table').attr('show_type', 'show')
//                }
            }else{
                alert(data["msg"]);
            }
        }});
    }
}

function Is_Inherit_Project(){
    var $obj = $(this);
    var value = $obj.val();
    if (value == 'True') {
        $('#Find_Project_Input').show();
    } else {
        $('#Find_Project_Input').hide();
    }
}

function Search_Project_Name_Button(){
    var name = $('#Search_Project_Name').val();
    if (!name || name=='請輸入工程名稱關鍵字') {
        alert('請輸入工程名稱關鍵字');
        return false;
    }
    $.ajax({ url:"/project/ajax/", type: "POST", data:{
            submit: "Search_Project_Name_Button", name: name
        }, dataType:"json", success:function(data){
        if(data["status"]){
            var html = $(data["html"]);
            $('#exProject').html(html);
        }else{
            alert(data["msg"]);
        }
    }});
}

function Show_Draft_Table(){
    var $obj = $(this);
    var value = $obj.attr('show_type');
    if (value == 'show') {
        $('#Draft_Table').show();
        $obj.attr('show_type', 'hide')
    } else {
        $('#Draft_Table').hide();
        $obj.attr('show_type', 'show')
    }
}

function delete_Draft_Project(){
    var $obj = $(this);
    var project_id = $obj.attr('draft_project_id');
    if (confirm('你確定要刪除此提案嗎??')){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{
                submit: "delete_Draft_Project", project_id: project_id
            }, dataType:"json", success:function(data){
            if(data["status"]){
                $('#tr_project_'+project_id).remove();
            }
            alert(data["msg"]);
        }});
    }
    
}

function edit_Draft_Project(){
    var $obj = $(this);
    var project_id = $obj.attr('draft_project_id');

    $.ajax({ url:"/project/ajax/", type: "POST", data:{
            submit: "edit_Draft_Project", project_id: project_id
        }, dataType:"json", success:function(data){
        if(data["status"]){
            $('#Draft_Table').show();
            $('#add_Draft_Project_add').hide();
            $('#add_Draft_Project_update').show();
            $('#add_Draft_Project_update').attr('del_project_id', data['project_id'])
            for (i=0; i<data['data'].length; i++) {
                var field_name = data['data'][i][0];
                var field_value = data['data'][i][1];
                $('#'+field_name).attr('value', field_value)
            }
            if (data['exproject'].length != 0){
                $('#Is_Inherit_Project').attr('value', 'True')
                $('#Find_Project_Input').show();
                $('#exProject').html('<option value="'+data['exproject'][0]+'" selected="selected">'+data['exproject'][1]+'</option>');
            } else {
                $('#Is_Inherit_Project').attr('value', 'False')
                $('#Find_Project_Input').hide();
            }

            if (data["port_list"].length != 0){
                $('#SubLocation').html(data["port_html"]);
            } else {
                $('#place').change();
            }

            if (data["html_sort"].length != 0){
                $('#sort').html(data["html_sort"]);
            }

            $('#year').focus();
        }

    }});
}


function cancel_Draft_Project(){
    window.location = '/frcm/add_draft';
}

function update_type_Draft_Project(){
    var $obj = $(this);
    var project_name = $obj.attr('project_name');
    var project_id = $obj.attr('draft_project_id');
    if (confirm('你確定要將'+ project_name +'轉移至"漁業署提案區"嗎??')){
        $.ajax({ url:"/project/ajax/", type: "POST", data:{
                submit: "update_type_Draft_Project", project_id: project_id
            }, dataType:"json", success:function(data){
            if(data["status"]){
                $('#tr_project_'+project_id).remove();
            }
        }});
    }
}

function add_New_Project_From_Draft(){
    var $obj = $(this);
    var project_name = $obj.attr('project_name');
    var project_id = $obj.attr('draft_project_id');
    if (confirm('你確定要將'+ project_name +'轉移至"正式管考工程"嗎??(注意：因欄位差異過大，當您完成新增工程的同時，將無法恢復回草稿區)')){
        window.location = '/project/addproject_from_draft/'+project_id+'/';
    }
}

function change_allot_rate(){
    var $obj = $(this);
    var capital_ratify_budget = parseInt($('#capital_ratify_budget').val(), 10);
    if (!capital_ratify_budget){capital_ratify_budget = 0;}
    var capital_ratify_local_budget = parseInt($('#capital_ratify_local_budget').val(), 10);
    if (!capital_ratify_local_budget){capital_ratify_local_budget = 0;}
    if ((capital_ratify_budget + capital_ratify_local_budget) != 0){
        $('#allot_rate').attr('value', capital_ratify_budget*100 / (capital_ratify_budget + capital_ratify_local_budget))
    } else {
        $('#allot_rate').attr('value', 100)
    }
}


var mouseX = 0;
var mouseY = 0;

$(document).ready(function(){
    $().mousemove( function(e) {
        mouseX = e.pageX;
        mouseY = e.pageY;
    });
    $('.pleaseUseRightClick').click(pleaseUseRightClick);
    $('.deleteDocumentFile').click(deleteDocumentFile);
    $('.Show_File_Info').click(Show_File_Info);
    $('.Hide_File_Info').blur(Hide_File_Info);

    $('.addPlan').click(addPlan);
    $("#deletePlan").click(deletePlan);
    $('.sortPlan').click(sortPlan);
    $('.Show_Plan_Info').click(Show_Plan_Info);
    $('.Hide_Plan_Info').blur(Hide_Plan_Info);
    $("#addPlanBudget").click(addPlanBudget);
    $(".deletePlanBudget").click(deletePlanBudget);
    $("#autoSum").click(autoSum);
    $(".Filter_Project_Type").click(Filter_Project_Type);
    $("#getMorePlaninfo").click(getMorePlaninfo);
    $("#editProjectListBudget").click(editProjectListBudget);
    $("#makeExcelButton").click(makeExcelButton);

    $('.Show_Budget_Info').click(Show_Budget_Info);
    $('.Hide_Budget_Info').blur(Hide_Budget_Info);

    $(".Change_Backlight").mouseover(Change_Backlight_over);
    
    $(".Change_Backlight").mouseout(Change_Backlight_out);

    $("#project_type").change(switchSubType);
    $("#cProject").click(cProject);
    $(".title_bar").click(switchTable);
    $("#sync_pcc_project").click(syncPCCProject)
    $('#show_pcc_project').click(showPCCProject);

    $('.addAppropriate').click(cAppropriate);
    $('.deleteProjectAppropriate').click(dAppropriate);

    $('.addAllocation').click(addAllocation);
    $('.deleteProjectAllocation').click(deleteProjectAllocation);

    $('.setChaseProject').click(setChaseProject);
    $('#setAllChaseProject').click(setAllChaseProject);
    $('#addNewChase').click(addNewChase);
    $('.ShowChaseProject').click(ShowChaseProject);
    $('#deleteLastChase').click(deleteLastChase);
    $('#updateChartNewUpdateInfo').click(updateChartNewUpdateInfo);
    $('#updateChartNewUpdateInfoDialog').click(updateChartNewUpdateInfoDialog);

    $('.setCheckForClose').click(setCheckForClose);
    $('.setFalseForClose').click(setFalseForClose);
    $('.setCheckForComplete').click(setCheckForComplete);
    $('.setFalseForComplete').click(setFalseForComplete);

    $('.getAccoutingData').click(showAccoutingData);
    $('.getFundingDetail').click(showPCCFundingDetail);
    $('.getPCCRecord').click(showPCCFundRecord);
    $('.deleteProjectFundRecord').click(dProjectFundRecord);
    $("#cReserve").click(cReserve);
    $("#reserve").click(reserveProject);
    $(".deleteProjectReserve").click(dReserve);

    $('.Show_Memo_Info').click(Show_Memo_Info);
    $('.Hide_Memo_Info').blur(Hide_Memo_Info);

    $("#show_pcc_progress_info").click(showPCCProgress);
    $(".deleteProjectProgress").click(dProgress);

    $("#ShowBatchEdit").click(ShowBatchEdit);
    $("#BatchEdit_Plan").change(BatchEdit_Plan);

    $(".change_allot_rate").change(change_allot_rate);

    $(".ChangeBgcolor").mouseover(ChangeBgcolor_over);
    $(".ChangeBgcolor").mouseout(ChangeBgcolor_out);

    $("#id_vouch_date_ub").change(id_vouch_date_ub);

    $('.Show_Chase_Info').click(Show_Chase_Info);
    $('.Hide_Chase_Info').blur(Hide_Chase_Info);

    $('#hideNotImportantInfo').click(hideNotImportantInfo);

    $('#show_upload_Field').click(show_upload_Field);
    $('#upload_DocumentFile').click(upload_DocumentFile);

    $('.add_Draft_Project').click(add_Draft_Project);
    $('#cancel_Draft_Project').click(cancel_Draft_Project);
    $('#Is_Inherit_Project').change(Is_Inherit_Project);
    $('#Search_Project_Name_Button').click(Search_Project_Name_Button);
    $('#Show_Draft_Table').click(Show_Draft_Table);
    $('.delete_Draft_Project').click(delete_Draft_Project);
    $('.edit_Draft_Project').click(edit_Draft_Project);
    $('.update_type_Draft_Project').click(update_type_Draft_Project);
    $('.add_New_Project_From_Draft').click(add_New_Project_From_Draft);


    // <{----- Active JQuery UI -----}>
    $(".setDate").datepicker({
        buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png",
        dateFormat: "yy-mm-dd", beforeShow: function(){$(this).show();},onClose: updateProjectRedaction
    });

    $(".chooseChaseDate").datepicker({
        buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png",
        dateFormat: "yy-mm-dd", beforeShow: function(){$(this).show();},onClose: Show_Chase_Info
    });

    $(".chooseFileDate").datepicker({
        buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png",
        dateFormat: "yy-mm-dd", beforeShow: function(){$(this).show();},onClose: Hide_File_Info
    });

    $("#id_vouch_date_ub").datepicker({
        buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png",
        dateFormat: "yy-mm-dd", onClose: updateProjectRedaction
    });
    $("#id_vouch_date_lb").datepicker({
        buttonImageOnly: true, buttonImage: "/media/project/image/calendar.png",
        dateFormat: "yy-mm-dd", onClose: updateProjectRedaction
    });

    $("#FunsInfoTabs").tabs();
    
    $('#checked_msg').ajaxStart(function(){
        $(this).text('執行中，請稍待，請勿關閉此頁面!!!!');
    })
    $('#checked_msg').ajaxStop(function(){
        $(this).text('');
    })

});

