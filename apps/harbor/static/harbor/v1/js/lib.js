var delRow = function(){
    if (confirm('確定刪除本紀錄嗎?')){
        var list = $(this).attr('id').split('_');
        var model_name = list[1];
        var row_id = list[2];
        $.ajax({ url: '/harbor/'+row_id+'/delrow/', type: "POST", data:{model_name: model_name,
                project_id: project_id, location_id: location_id}, dataType:"json", success:function(json){
            alert(json['message']);
        }});
        alert('刪除成功');
        if (model_name == 'fishingportphoto') {
            var $row = $('#fishingportphoto_'+row_id);
        } else if (model_name == 'waves') {
            var $row = $('#waves_'+row_id);
        } else if (model_name == 'tide') {
            var $row = $('#tide_'+row_id);
        } else if (model_name == 'boat') {
            var $row = $('#boat_'+row_id);
        } else if (model_name == 'mainproject') {
            var $row = $('#mainproject_'+row_id);
        }else if (model_name == 'project') {
            var $row = $('#project_'+row_id);
        } else if (model_name == 'fisherytype') {
            var $row = $('#fisherytype_'+row_id);
        } else if (model_name == 'fishtype') {
            var $row = $('#fishtype_'+row_id);
        } else if (model_name == 'fisheryoutput') {
            var $row = $('#fisheryoutput_'+row_id);
        } else if (model_name == 'averagerainfall') {
            var $row = $('#averagerainfall_'+row_id);
        } else if (model_name == 'averagetemperature') {
            var $row = $('#averagetemperature_'+row_id);
        } else if (model_name == 'averagepressure') {
            var $row = $('#averagepressure_'+row_id);
        }
        $row.remove();
    }
    return false;
}

var switchPOC = function(){
    var $obj = $(this);
    var show = $obj.attr('id');
    if (show == 'lay_port'){
        $('#port_table').show();
        $('#obva_table').hide();
        $('#lay_obva').show();
        $('#gather_obva').hide();
        $('#city_table').hide();
        $('#lay_city').show();
        $('#gather_city').hide();
        $('#lay_port').hide();
        $('#gather_port').show();
        $('#cam_table').hide();
        $('#lay_cam').show();
        $('#gather_cam').hide();
    } else if (show == 'gather_port'){
        $('#port_table').hide();
        $('#obva_table').hide();
        $('#lay_obva').show();
        $('#gather_obva').hide();
        $('#city_table').hide();
        $('#lay_city').show();
        $('#gather_city').hide();
        $('#lay_port').show();
        $('#gather_port').hide();
        $('#cam_table').hide();
        $('#lay_cam').show();
        $('#gather_cam').hide();
    }
    if (show == 'lay_obva'){
        $('#port_table').hide();
        $('#lay_port').show();
        $('#gather_port').hide();
        $('#obva_table').show();
        $('#city_table').hide();
        $('#lay_city').show();
        $('#gather_city').hide();
        $('#lay_obva').hide();
        $('#gather_obva').show();
        $('#cam_table').hide();
        $('#lay_cam').show();
        $('#gather_cam').hide();
    } else if (show == 'gather_obva'){
        $('#port_table').hide();
        $('#lay_port').show();
        $('#gather_port').hide();
        $('#obva_table').hide();
        $('#city_table').hide();
        $('#lay_city').show();
        $('#gather_city').hide();
        $('#lay_obva').show();
        $('#gather_obva').hide();
        $('#cam_table').hide();
        $('#lay_cam').show();
        $('#gather_cam').hide();
    }
    if (show == 'lay_city'){
        $('#port_table').hide();
        $('#lay_port').show();
        $('#gather_port').hide();
        $('#obva_table').hide();
        $('#lay_obva').show();
        $('#gather_obva').hide();
        $('#city_table').show();
        $('#lay_city').hide();
        $('#gather_city').show();
        $('#cam_table').hide();
        $('#lay_cam').show();
        $('#gather_cam').hide();
    } else if (show == 'gather_city'){
        $('#port_table').hide();
        $('#lay_port').show();
        $('#gather_port').hide();
        $('#obva_table').hide();
        $('#lay_obva').show();
        $('#gather_obva').hide();
        $('#city_table').hide();
        $('#lay_city').show();
        $('#gather_city').hide();
        $('#cam_table').hide();
        $('#lay_cam').show();
        $('#gather_cam').hide();
    }

    if (show == 'lay_cam'){
        $('#port_table').hide();
        $('#obva_table').hide();
        $('#lay_obva').show();
        $('#gather_obva').hide();
        $('#city_table').hide();
        $('#lay_city').show();
        $('#gather_city').hide();
        $('#lay_port').show();
        $('#gather_port').hide();
        $('#cam_table').show();
        $('#lay_cam').hide();
        $('#gather_cam').show();
    } else if (show == 'gather_cam'){
        $('#port_table').hide();
        $('#obva_table').hide();
        $('#lay_obva').show();
        $('#gather_obva').hide();
        $('#city_table').hide();
        $('#lay_city').show();
        $('#gather_city').hide();
        $('#lay_port').show();
        $('#gather_port').hide();
        $('#cam_table').hide();
        $('#lay_cam').show();
        $('#gather_cam').hide();
    }
}

var glPort = function(){
    var $obj = $(this);
    var target = $obj.attr('dn');
    if ($obj.hasClass('lay')){
        $('.gather').hide();
        $('.lay').show();
        $('.open').hide()

        $('#loca_' + target).show();
        $obj.hide();
        $('#gather_' + target).show();
        $('#loca_' + target).attr('class','open');
    } else if ($obj.hasClass('gather')){
        $('#loca_' + target).hide();
        $obj.hide();
        $('#lay_' + target).show()
    }
}

var rPlacePort = function(){
    var $obj = $(this);
    var place = $obj.attr('id');
    $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "rPlacePort",
            place: place}, dataType:"json", success:function(json){
        if (json['status'] != true){
                alert(json['message']);
            } else {
                var portblock = json['portblock'];
                $('#ports_list').html(portblock);
//                var city = ''
//                city += '<span href="/harbor/cityinfo/' + place + '">' + $obj.attr('title') + '</span>'
                $('#enter_button').attr('href','/harbor/cityinfo/' + place);
                $('#place_button').html($obj.attr('title'));
                $('#place_button').show();
            }
    }});
    return false;
}

var switchPhotoType = function(){
    var port = $('#photo_type_select').attr('dn');
    var type = $(this).val();
    window.location = '/harbor/portphotos/' + port + '/' + type;
    return false;
}

var getPhoto = function(){
    var $obj = $(this);
    var id = $obj.attr('id');
    var type = $(this).val();
    $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "getPhoto",
            id: id}, dataType:"json", success:function(json){
        if (json['status']==true){
            $('#show_photo').html(json['photoblock']);
            $('.photonow').attr('class','photolink')
            $obj.attr('class','photonow')
            $('.photolink').click(getPhoto);
        } else {
            alert('');
        }
    }});
    return false;
}

var getInfoMemo = function(){
    var $obj = $(this);
    var type = $obj.attr('type');
    var id = $obj.attr('dn');
    var title = $obj.attr('title');
    var is_infa = $obj.attr('is_infa');
    if (!is_infa) {
        var is_infa = '';
    }
    $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "getInfoMemo",
            type: type, id: id, is_infa: is_infa}, dataType:"json", success:function(json){
        if (json['status']==true){
            $dialog = $(json['contents'].replace(/None/gi,''));
            $dialog.dialog({
                title: title,
                width: json['width'],
                height: json['height'],
                buttons: {
                    '關閉本視窗': function(){
                        $dialog.dialog('close');
                    }
                }
            })
        } else {
            alert('');
        }
    }});
    return false;
}


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

var getPort = function(){
    var $obj = $(this);
    if( $obj.attr('value')){
        var place = $obj.attr('value');
        $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "getPort",
                place: place}, dataType:"json", success:function(json){
            if (json['status']==true){
                $('#FishingPort').html(json['contents'])
            }
        }});
    }
    return false;
}

var getToMonth = function(){
    var $obj = $(this);
    
    var from = $obj.val();
    
    var contents = '';
    contents += '<select id="month_to" class="styleT">';
    for (var i=from ;i<13;i++){
            contents += '<option value="' + i + '">　' + i + '　</option>';
        }
    contents += '</select>';
    $('#ToMonth').html(contents);
    return false;
}

var searchRecord = function(){
    var place = $('#City').val();
    var port = $('#Port').attr('value');
    var year = $('#year').val();
    var month_from = $('#month_from').val();
    var month_to = $('#month_to').val();
    var random = Math.random();
    window.location = '/harbor/installation/?submit=search&place='+place+'&port='+port+'&year='+year+'&month_from='+month_from+'&month_to='+month_to+'&random='+random+'&get_or_post=GET';
}

var closeRecord = function(){
    var $obj = $(this);
    var id = $obj.attr('id');
    $('.open_' + id).hide();
    $('.close_' + id).show();
    $('#record_' + id).fadeOut();
}

var openRecord = function(){
    var $obj = $(this);
    var id = $obj.attr('id');
    $('.close_' + id).hide();
    $('.open_' + id).show();
    $('#record_' + id).fadeIn();
}

var getRecord = function(){
    var port = $('#location').attr('fishingport');
    var year = $('#select_year').val();
    var wyear = Number(year) + 1911
    var month = $('#select_month').val();
    window.location = '/harbor/portinstallation/record/'+ port + '/' + wyear + '/' + month + '/';

}

var editInfo = function(){
    var $obj = $(this);
    var target_id = $obj.attr('id');
    $('.show_' + target_id).hide();
    $('.edit_' + target_id)
                    .fadeIn()
                    .focus();
}

var updateInfo = function(){
    var change = false;
    var $port = $('#location').attr('loca');
    var $obj = $(this);
    var type = $obj.attr('type');
    var target = $obj.attr('id');
    var id = $obj.attr('dn');
    var field = $obj.attr('dt');
    var old_Info = $obj.attr('old_value');
    var new_Info = $obj.attr('value');
    if($obj.hasClass('Pass')){
        return false;
    }
    if (new_Info != old_Info){
            change = true;
    }
    if (change){
        var format = true;
        if ($obj.hasClass('int')){
            var num_check=/^[0-9]*$/;
            if(!(num_check.test(new_Info))){
                var message = '數量格式錯誤！';
                format = false;
            }
        }
        if ($obj.hasClass('time')){
            var time_check=/^\d{1,2}:\d{1,2}$/;
            if(!(time_check.test(new_Info))){
                var message = '時間格式錯誤！';
                format = false;
            }
        }
        if (format){
            $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "updateInfo",
                    id: id, field: field, new_inf: new_inf, old_inf: old_inf}, dataType:"json", success:function(json){
                if (json['status'] != true){
                    alert(json['message']);
                } else {
                    if (type == 'select-one'){
                        $('.edit_' + target).attr('value', new_Info);
                        $('.edit_' + target).attr('old_value', new_Info);
                        $('.show_' + target).html(json['return_name']);
                    } else {
                        $('.edit_' + target).attr('value', new_Info)
                        $('.edit_' + target).attr('old_value', new_Info)
                        $('.show_' + target).html(json['return_name'].replace(/\n/gi, '<br>'));
                    }
                }
            }});
        } else {
            $('.edit_' + target).attr('value', old_Info)
            $('.edit_' + target).attr('old_value', old_Info)
            alert(message);
        }
        $('.show_' + target).fadeIn();
        $('.edit_' + target).hide();
    } else {
        $('.show_' + target).fadeIn();
        $('.edit_' + target).hide();
    }
}

var changePortFile = function(){
    var $obj = $(this);
    var type = $obj.attr('type');
    var row_id = $obj.attr('row_id');
    if (type=='show'){
        $('.showFile_'+row_id).hide();
        $('.editPortFile_'+row_id).show();
        $obj.attr('type', 'edit')
    } else {
        $('.showFile_'+row_id).show();
        $('.editPortFile_'+row_id).hide();
        $obj.attr('type', 'show')
    }
}

var deletePortFile = function(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var name = $obj.attr('neme');
    var msg = '您確定要刪除『'+name+'』檔案嗎？';
    if (confirm(msg)){
        $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "deletePortFile",
                row_id: row_id}, dataType:"json", success:function(json){
            if (json['status']==true){
                alert('刪除成功');
                $('#File_tr_'+row_id).remove();
            } else {
                alert(json['message']);
            }
        }});
    }
}

var editPortFile = function(){
    var $obj = $(this);
    var temp = $obj.attr('id').split('_');
    var field_name = temp[1];
    var field_id = temp[2];
    var value = $obj.attr('value');
    var old_value = $obj.attr('old_value');
    if (value == old_value){
        return false;
    }
    $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "editPortFile",
            value: value, field_name: field_name, field_id: field_id}, dataType:"json", success:function(json){
       if (json['status']==true){
            $obj.attr('value', value)
            $obj.attr('old_value', value)
            $('#showFile_'+ field_name +'_'+field_id).html(json['value'].replace(/\n/gi, '<br>'));
        } else {
            alert(json['message']);
        }
    }});
}

var changeShareFile = function(){
    var $obj = $(this);
    var type = $obj.attr('type');
    var row_id = $obj.attr('row_id');
    if (type=='show'){
        $('.showFile_'+row_id).hide();
        $('.editShareFile_'+row_id).show();
        $obj.attr('type', 'edit')
    } else {
        $('.showFile_'+row_id).show();
        $('.editShareFile_'+row_id).hide();
        $obj.attr('type', 'show')
    }
}

var deleteShareFile = function(){
    var $obj = $(this);
    var row_id = $obj.attr('row_id');
    var name = $obj.attr('neme');
    var msg = '您確定要刪除『'+name+'』檔案嗎？';
    if (confirm(msg)){
        $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "deleteShareFile",
                row_id: row_id}, dataType:"json", success:function(json){
           if (json['status']==true){
                alert('刪除成功');
                $('#File_tr_'+row_id).remove();
            } else {
                alert(json['message']);
            }
        }});
    }
}

var editShareFile = function(){
    var $obj = $(this);
    var temp = $obj.attr('id').split('_');
    var field_name = temp[1];
    var field_id = temp[2];
    var value = $obj.attr('value');
    var old_value = $obj.attr('old_value');
    if (value == old_value){
        return false;
    }
    $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "editShareFile",
            value: value, field_name: field_name, field_id: field_id}, dataType:"json", success:function(json){
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
        $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "deleteCityFile",
                row_id: row_id}, dataType:"json", success:function(json){
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
    $.ajax({ url: '/harbor/readjson/', type: "POST", data:{submit: "editCityFile",
            value: value, field_name: field_name, field_id: field_id}, dataType:"json", success:function(json){
       if (json['status']==true){
            $obj.attr('value', value)
            $obj.attr('old_value', value)
            $('#showFile_'+ field_name +'_'+field_id).html(json['value'].replace(/\n/gi, '<br>'));
        } else {
            alert(json['message']);
        }
    }});
}


var AutoInputFileName = function(){
    var $obj = $(this);
    var name = $obj.attr('value');
    var name = name.match(/[^\/\\]+$/);
    $('#AutoInputFileName_Target').attr('value', name)
}

var CheckNameNotNull = function(){
    var $obj = $(this);
    var name = $('#AutoInputFileName_Target').attr('value');
    if (!name){
        alert('檔案名稱不可為空白，請填入檔名');
        return false;
    }
}

$(document).ready(function(){
    if ($('#location').length >= 1) {
        var location = $('#location').attr('class');
        if (location == 'port'){
            $('#port_table').show();
            $('#lay_port').hide();
            $('#gather_port').show();
            var loca = $('#location').attr('loca');
            $('#loca_' + loca).show();
            $('#loca_' + loca).attr('class','open');
            $('#gather_' + loca).show()
            $('#lay_' + loca).hide()
        } else if (location == 'obva'){
            $('#obva_table').show();
            $('#lay_obva').hide();
            $('#gather_obva').show();
        } else if (location == 'city'){
            $('#city_table').show();
            $('#lay_city').hide();
            $('#gather_city').show();
        } else if (location == 'cam'){
            $('#cam_table').show();
            $('#lay_cam').hide();
            $('#gather_cam').show();
        }
    }

    $('.delRow').click(delRow);
    $('.gal').click(glPort);
    $('.switch').click(switchPOC);
    $('.image_map').click(rPlacePort);
    $('#photo_type_select').change(switchPhotoType);
    $('.photolink').click(getPhoto);
    $('.infomemo').click(getInfoMemo);
    $('.requisite').change(checkRequisite);
    $('.integer').blur(checkInteger);
    $('.float').blur(checkFloat);
    $('.chooseDate').change(checkDate);
    $('#City').change(getPort);
    $('#month_from').change(getToMonth);
    $('#searchRecord').click(searchRecord);
    $('#select_month').change(getRecord);
    $('.editable').click(editInfo);
    $('.update_edited').blur(updateInfo);
    $('.opened_record').click(closeRecord);
    $('.closed_record').click(openRecord);
    $('.changePortFile').click(changePortFile);
    $('.editPortFile').change(editPortFile);
    $('.deletePortFile').click(deletePortFile);
    $('.changeShareFile').click(changeShareFile);
    $('.editShareFile').change(editShareFile);
    $('.deleteShareFile').click(deleteShareFile);
    $('.changeCityFile').click(changeCityFile);
    $('.editCityFile').change(editCityFile);
    $('.deleteCityFile').click(deleteCityFile);
    $('#AutoInputFileName').change(AutoInputFileName);
    $('.CheckNameNotNull').click(CheckNameNotNull);


    $.datepicker.setDefaults({showOn: 'both', buttonImageOnly: true, dateFormat: 'yy-mm-dd',
    buttonImage: '/media/jquery-plugins/calender.png', buttonText: '', onClose:updateInfo});
    $('.chooseDate').each(function() {
    	$(this).datepicker();
    });   
    $('#id_date').datepicker();
});
