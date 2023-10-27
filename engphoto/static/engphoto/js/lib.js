var dialog_close = function(dialog_name, id){
    $('#'+dialog_name+'_dialog_'+id).dialog('close');
}
var deletePhoto = function (type, checkpoint_id, photo_id) {
    var duplicate = $('#showfile_'+photo_id).html().indexOf('重複');
    if (! confirm('所移除的相片，會在半年後由系統自動刪除')){
        return false;
    } 
    $.receiveJSON('/engphoto/deletephoto/'+photo_id+'/', {'type': type, 'csrfmiddlewaretoken': token}, function(json){
        if (json['status'] == false) {
            alert(json['message']);
        } else {
            var $deleteTable = $('#photo_'+photo_id);
            var order = $('#order_'+photo_id).text();
            var $newTable = $(json['html']);
            $('span.order', $newTable).text(order);
            $newTable.insertBefore($deleteTable);
            $deleteTable.remove();
            if (duplicate == -1) {
                var $photonow = $('#photonow_'+checkpoint_id);
                $photonow.text(Number($photonow.text()) - 1);
            }
        }
    });
    if ($('#duplicate_dialog_'+photo_id).length>=1){
        dialog_close('duplicate', photo_id);
    }
    if ($('#notenough_dialog_'+photo_id).length>=1){
        dialog_close('notenough', photo_id);
    }
}
var moveTo = function( target_id , source_id ){
    if(!confirm('確定移動相片? 如果目的地已有相片，將會被移至資源回收筒，並在半年內後自動刪除!')){
        return false;
    }
    $.get('/engphoto/moveto/'+target_id+'/'+source_id+'/', '', function(html){
        var $deleteTable = $('#photo_'+source_id);
        var order = $('#order_'+source_id).text();
        var $newTable = $(html);
        $('span.order', $newTable).text(order);
        $newTable.insertBefore($deleteTable);
        $deleteTable.remove();

        getActualCheckPoint(project_id, '#base');
        dialog_close('movetoelse', source_id);
    });
}
var moveToElseButton = function (source_id) {
    if (!$('#movetoelse_dialog_'+source_id).length){
        $('body').append($('<div id="movetoelse_dialog_'+source_id+'"></div>'));
    }
    var $movetoelse_dialog = $('#movetoelse_dialog_'+source_id);
    if (false && $movetoelse_dialog.text()){
        $movetoelse_dialog.dialog('close');
        $movetoelse_dialog.dialog('open');
    } else {
        $.receiveJSON('/engphoto/getallphotolist/'+source_id+'/', {'csrfmiddlewaretoken': token}, function(json){
            var html = '';
            for (var k=0; k < json['CPs'].length; k++){
                html += '<ul>';
                    html += '<li>'+json['CPs'][k]['dir']['name']+'</li>';
                    html += '<ul>';
                        for (var i in json['CPs'][k]['sublevel']){
                            html += '<li>'+json['CPs'][k]['sublevel'][i]['name']+'</li>';
                            html += '<ul>';
                                for (var j in json['CPs'][k]['sublevel'][i]['photo_ids']){
                                    var photo_id = json['CPs'][k]['sublevel'][i]['photo_ids'][j];
                                    html += '<li>#' + (Number(j)+1) + ' ';
                                    //alert(json['CPs'][k]['sublevel'][i]['photo_ids']);
                                    //alert(source_id);
                                    var not_in_photoids = true;
                                    for (var s=0;s<json['CPs'][k]['sublevel'][i]['photo_ids'].length;s++) {
                                        if (json['CPs'][k]['sublevel'][i]['photo_ids'][s] == source_id){
                                            not_in_photoids = false;
                                            break;
                                        }
                                    }
                                    if (not_in_photoids){
                                        html += '<input name="yy" type="radio" onClick="moveTo('
                                        +json['photos'][photo_id]['id']+', '+source_id+')" /> ';
                                    }
                                    html += json['photos'][photo_id]['position'];
                                    if (json['photos'][photo_id]['note_con']){
                                        html += ': ' + json['photos'][photo_id]['note_con'];
                                    }
                                    html += '</li>';
                                }
                            html += '</ul>';
                        }
                    html += '</ul>';
                html += '</ul>';
            }
            $movetoelse_dialog.html(html);
        });
        $movetoelse_dialog.dialog({
            title: '移動相片至…',
            //modal: true,
            //overlay: {opacity: 0.8, background: "black"},
            buttons: {
                '關閉本視窗': function(){
                    $movetoelse_dialog.dialog('close');
                }
            },
            width: 500,
            height: 500
        });
        $movetoelse_dialog.dialog('open');
    }
}
var ajaxFileUpload = function (obj, inputname) {
    if (!confirm('確定上傳 '+obj.value+' ?')){
        obj.value = '';
        return false;
    }
    var extension = /\.(jpg|jpeg|gif|png|tif|tiff)$/i.exec(obj.value);
    if (!extension) {
        alert('施工相片檔案的副檔名只可以是 .jpg, .jpeg, .gif, .png, .tif, .tiff 等。');
        return false;
    }
    var id = inputname.replace('file_', '');
    $('#showfile_'+id).html($('<div></div>').css({
        'background-image': 'url(/media/images/uploading.gif)',
        'background-repeat': 'no-repeat',
        'width': '400px', 'height': '300px'
    }));

    var photonum = Number($('#upload_photonum').text()) + 1;
    $('#upload_photonum').text(photonum);
    var message = $('#checkpoint_'+id).html()+'的'+$('#order_'+id).html();
    $('#upload_photolist').append($('<li id="photolist_'+id+'">'+message+'</li>'));
    $('#upload_photomsg').show();

    $.ajaxFileUpload({
        url:'/engphoto/updatephotoinfo/'+id+'/?fieldname=file&value=',
        async: true,
        fileElementId: inputname,
        dataType: 'json',
        success: function (json, status) {
            var photonum = Number($('#upload_photonum').text()) - 1;
            if (photonum == 0){
                $('#upload_photonum').text('');
                $('#upload_photomsg').hide();
            }else{
                $('#upload_photonum').text(photonum);
            }
            var removelist = '#photolist_'+json['photo_id'];
            $('#upload_photolist').find(removelist).each(function(){ $(this).remove(); });
            $('#movebutton_'+json['photo_id']+' button').show();
            $('#trashbutton_'+json['photo_id']+' button').show();
            $('#deletebutton_'+json['photo_id']+' button').show();
            if (json['status'] == false){
                $('#showfile_'+json['photo_id']).html('<img src="/media/engphoto/images/nopicture.png" width="400" height="300">');
                alert(json['message']);
            } else {
                if (json['duplicatetype'] == '系統判斷重複'){
                    $('#showfile_'+json['photo_id']).html('');
                    makeDuplicateButton(json['photo_id']);
                } else if (json['enoughtype'] == '未達要求大小的相片'){
                    $('#showfile_'+json['photo_id']).html('');
                    makeNotEnoughButton(json['photo_id']);
                } else {
                    if (json['thumbsrc']){
                        var img = '<a href="/engphoto/bigpicture/'+json['photo_id']
                        +'/" target="photo" onmouseover="style.cursor=\'pointer\'">'
                        +'<img width="400" height="300" class="engphoto" src="/engphoto/getpic/'
                        +json['thumbsrc']+'"></a>';

                        $('#showfile_'+json['photo_id']).html(img); 
                    }
                    if (json['newphoto'] && json['checkpoint_id']){
                        var $photonow = $('#photonow_'+json['checkpoint_id']);
                        $photonow.text(Number($photonow.text()) + 1);
                    }
                    if (json['owner_username']){
                        $('#uploader_'+id).attr('title', '帳號: '+json['owner_username'])
                        .html('上傳者: '+json['owner_name']);
                    }
                }

                if (json['size']){
                    $('#size_'+json['photo_id']).text(json['size']);
                }

                if (json['photodate']){
                    $photodate = $('#i_photodate_'+json['photo_id']);
                    $photodate.attr('value', json['photodate'])
                }

                if (json['uploadtime']){
                    $uploadtime = $('#uploadtime_'+json['photo_id']);
                    $uploadtime.text(json['uploadtime']);
                }

    //            alert(json['message']);
    //            if(typeof(json.error) != 'undefined') {
    //                if(json.error != '') {
    //                    alert(json.error);
    //                }else {
    //                    alert(json.message);
    //                }
    //            }
            }
        },
        error: function (json, status, e) {
            var message = '';
            for (var k in json) {
                message += k + ':' + json[k] + ',';
            }
            var content = 'ajaxFileUpload: '+ status + ', ' + e + ': ' + message;
            var $ajaxError = $('<div id="ajaxError">'+content+'</div>');
            $('body').append($ajaxError);
            $ajaxError.dialog({
                title: '',
                //modal: true,
                //overlay: {opacity: 0.8, background: "black"},
                buttons: {
                    '關閉本視窗': function(){
                        $ajaxError.dialog('close');
                    }
                },
                width: 950,
                height: 550
            });
        }
    });
    return false;
}
var splitPlane = function (){
    var pos = $('#EngPhotoPlane').position();
    var height = $(window).height() - pos['top'] - 18;
    var width = $(window).width() - pos['left']*2 - 8;
    $("#EngPhotoPlane").css({
        'height': height+'px',
        'width': width+'px'
    }).splitter({
        type: 'v',
        initA: true,	// use width of A (#LeftPane) from styles
        accessKey: '|'
    });
    // Firefox doesn't fire resize on page elements
    //$(window).bind("resize", function(){
    //    $("#EngPhotoPlane").trigger("resize"); 
    //}).trigger("resize");
}
var showCheckPointView = function (){
    var id = /\/engphoto\/([0-9]+)\/#?$/.exec(window.location)[1];
    getActualCheckPoint(id, '#base');
}
var checkClick = function(id) {
    $('#msg2_'+id).text('');
    $('#form2_'+id).find('td.top > input.checkpointtab2-checkbox').each(function(){
        if($(this).attr('checked')){
            $('#msg2_'+id).text($('#msg2_'+id).text()+','+$(this).parent().next().text());
        }
    });
    if ($('#msg2_'+id).text()) {
        $('#msg2_'+id).text('已點選: ' + $('#msg2_'+id).text()).css({'background': 'white'}).show();
    }
    $('#msg22_'+id).text($('#msg2_'+id).text()).css({'background': 'white'}).show();
}
var addCheckPoint = function (id, type, QueryString) {
    if (type == 'checkpointtab2'){
        type = 'template';
    } else if (type == 'project_checkpoint'){
        type = 'project'
    }
    $.receiveJSON('/engphoto/'+id+'/addby'+type+'/', QueryString, function (json) {
        alert(json['message']);
        $('#form'+type+'2_'+id).find('input[@type=checkbox]:checked').each(function(){
            $(this).attr('checked', '');
        });
        getActualCheckPoint(id, '#base');
    });
}
var checkNum = function(id, floor, obj) {
    if (isNaN(Number(obj.value))){
        alert('請填入數字');
        obj.value = floor;
        return false;
    } else if (obj.value < floor){
        alert('數量不可少於 '+floor+' 。');
        obj.value = floor;
        return false;
    }
}
var layoutCheckPoint = function(id, type, Templates){
    var content = '<div id="form'+type+'2_'+id+'"><table align="center">';

    //TODO delete
    //將「新增鈕」移至 dialog 右下角
    //content += '<tr><td colspan="3" align="center" width="430"><button id="search2_'+id;
    //content += '" class="search search2_'+id+'">新增</button><div id="msg2_'+id+'"></div></td></tr>';
    content += '<tr>';
    content += '    <th>請勾選所需</th>';
    content += '    <th>查驗點群組/查驗點名稱</th>';
    content += '    <th>基本套數/張數</th>';
    content += '</tr>';
    for (var a in Templates) {
        var b = 0;
        if (Templates[a][b]['help'] == ''){
            content += '<tr title="無說明">';
        } else {
            var help = Templates[a][b]['help'].replace(/\\n/g, '&#13;');
            content += '<tr title="'+ help +'">';
        }
        content += '    <td class="top"><input type="checkbox" class="notice '+type+'-checkbox"';
        content += ' name="checkpointok_'+Templates[a][b]['id']+'"';
        content += ' id="'+type+'_'+id+'_'+Templates[a][b]['id']+'"></td>';
        content += '    <td>'+Templates[a][b]['name']+'</td>';
        content += '    <td><input type="text" size="4" class="notice" value="';
        content += Templates[a][b]['floor']+'"';
        content += ' id="num_'+type+'_'+id+'_'+Templates[a][b]['id'];
        content += '" name="checkpointnum_' + Templates[a][b]['id'] + '"';
        content += ' onChange="return checkNum('+Templates[a][b]['id']+',';
        content += Templates[a][b]['floor']+', this);"></td>';
        content += '</tr>';
        content += '<tr class="hidden" class="sublevel_'+type+'_"'+id;
        content += '" id="sublevel_'+type+'_';
        content += id+'_'+Templates[a][b]['id'];
        content += '"><td colspan="3"><table style="margin-left:20px">';

        for (b = 1;b<=Templates[a].length -1; b++){
            if (Templates[a][b]['help'] == ''){
                content += '<tr title="無說明">'
            } else {
                var help = Templates[a][b]['help'].replace(/\\n/g, '&#13;');
                content += '<tr title="'+ help +'">';
            }
            content += '<td><input type="checkbox" class="notice '+type+'-checkbox"';
            content += ' id="'+Templates[a][b]['id'];
            content += '" name="checkpointok_'+Templates[a][b]['id']+'"></td>';
            content += '<td>' + Templates[a][b]['name'] + '</td>';
            content += '<td><input type="text" size="4" class="notice" value="';
            content += Templates[a][b]['floor']+'"';
            content += ' name="checkpointnum_' + Templates[a][b]['id'] + '"';
            content += ' onChange="return checkNum('+Templates[a][b]['id']+',';
            content += Templates[a][b]['floor']+', this);"></td>';
            content += '</tr>';
        }
        content += '</table></td></tr>';
    }

    //TODO delete
    //將「新增鈕」移至 dialog 右下角
    //content += '<tr><td colspan="3" align="center" width="430"><button id="search2_'+id;
    //content += '" class="search search2_'+id+'">新增</button><div id="msg22_'+id+'"></div></td></tr>';
    content += '</table></div>';

    $('#container-'+type+'_'+id).html(content)
    .find('.'+type+'-checkbox').click(function(){
        var sublevel_id = $(this).attr('id');
        checkClick(id);

        if ($(this).attr('checked')) {
            if ($('#num_'+sublevel_id).val() < 1) {
                $('#num_'+sublevel_id).val(1);
            }
            $('#sublevel_'+sublevel_id).removeClass('hidden')
            .find('input[@type=checkbox]').each(function(){
                this.checked = true;
            });
        } else {
            $('#num_'+sublevel_id).val(0);
            $('#sublevel_'+sublevel_id).addClass('hidden')
            .find('input[@type=checkbox]').each(function(){
                this.checked = false;
            });
        }
    });

    //TODO delete
    //將「新增鈕」移至 dialog 右下角
    //$('.search2_'+id).click(function() {
    //    var id = $(this).attr('id').replace('search', '');
    //    var querystring = $('#form'+type+id).find('input[@type=checkbox]:checked').serialize().split('&');
    //    var project_id = id.split('_')[1];
    //    var qs = ['id='+project_id];
    //    for (var i=0;i < querystring.length; i++) {
    //        var chkid = querystring[i].split('=')[0].split('_')[1];
    //        var num = $('#form'+type+id+' input[@name=checkpointnum_'+chkid+']').attr('value');
    //        qs.push(chkid+'='+num);
    //    }
    //    addCheckPoint(project_id, type, qs.join('&'));
    //});
}
var getOwnProject = function(id){
    $.receiveJSON('/engphoto/'+id+'/getownproject/', {'csrfmiddlewaretoken': token}, function(json){
        $obj = $('#container-checkpointtab3_'+id);
        var content = '';
        if (json['status'] == false){
            content = '無工程案';
        } else if (json['status'] == true){
            content += '<ul>';
            for (var i = 0; i < json['projects'].length; i++){
                var project = json['projects'][i];
                content += '<li><input type="radio" name="projects" id="'+project['id']
                +'" onClick="getProjectCheckPoint(this, '+id+')">';
                content += project['bid_no']+'::'+project['name']+'</li>';
            }
            if (i == 0){
                content += '<li>無其他工程案</li>';
            }
            content += '</ul>';
        }
        $obj.html(content);
    });
}
var getTemplate = function (id) {
    $.receiveJSON('/engphoto/'+id+'/gettemplates/', {'csrfmiddlewaretoken': token}, function(json){
        if (json['status'] == true){
           layoutCheckPoint(id, 'checkpointtab2', json['CheckPoints']);
        }
    });
}
var fieldname_help = {
    'position': '椿號位置或相片名稱',
    'photodate': '拍照日期',
    'inspector_check': '監工檢視',
    'note_con': '營造廠商說明',
    'note_ins': '監造廠商意見',
    'note_eng': '主辦意見',
    'note_exp': '專家意見'
};
var updatePhotoField = function(id){
    var array = /^(.*)_([0-9]+)$/.exec(id);
    var fieldname = array[1];
    var id = array[2];
    var $input = $('#i_'+fieldname+'_'+id);
    $input.highlightFade('yellow');
    $input.parent().highlightFade('yellow');
    if (fieldname == 'inspector_check') {
        if ($input.attr('checked')){
            var value = '1';
//            $input.parent().html('是');
        } else {
            var value = '0';
//            $input.parent().html('否');
        }
    } else {
        var value = $input.val();
//        $input.parent().html(value);
    }
    var fieldnum = Number($('#upload_fieldnum').text()) + 1;
    $('#upload_fieldnum').text(fieldnum);
    var message = $('#checkpoint_'+id).html()+': '+$('#order_'+id).html()+'的'+fieldname_help[fieldname];
    $('#upload_fieldlist').append($('<li id="fieldlist_'+fieldname+'_'+id+'">'+message+'</li>'));
    $('#upload_fieldmsg').show();

    $.receiveJSON('/engphoto/updatephotoinfo/'+id+'/', {'photo_id': id, 'fieldname': fieldname, 'value': value, 'csrfmiddlewaretoken': token},
    function(json) {
        if (json['status'] == true) {
            //var message = '';
            //for (var k in json) {
                //message += k + ': ' + json[k] + ', ';
            //}
            //alert(message);
            var fieldnum = Number($('#upload_fieldnum').text()) - 1;
            if (fieldnum == 0){
                $('#upload_fieldnum').text('');
                $('#upload_fieldmsg').hide();
            }else{
                $('#upload_fieldnum').text(fieldnum);
            }
            var removelist = '#fieldlist_'+json['fieldname']+'_'+json['photo_id'];
            $('#upload_fieldlist').find(removelist).each(function(){ $(this).remove(); });
        }
    });
}
var echo_photoOnChange = function (id) {
    return 'onChange="updatePhotoField(\''+id+'\')"';
}
var getphotos = function (type, kind, id){
    if (type == 'bycheckpoint' && kind != 'checkpoint') {
        return false;
    }
    url = '/engphoto/getphotos'+type+'/'+id+'/';
    $('#RightPane #photos').html('<img src="/media/images/uploading.gif">');

    $.ajax({
        url: url,
        dataType: 'html',
        success: function(html){
            if (html.length < 100){
                html = '未設定查驗點';
            }
            $('#RightPane #photos').html(html).find('.canedit').each(function(){
                    var value = $(this).text();
                    var id = $(this).attr('id');
                    var fieldname = /^(\w+)_[0-9]+$/.exec(id)[1];
                    //alert('id: '+id+', fieldname: '+fieldname+', value: '+value);
                    if (fieldname == 'inspector_check') {
                        if (value == '是') {
                            $(this).html('<input id="i_'+id+'" type="checkbox" class="notice" name="'
                            +id+'" checked '+echo_photoOnChange(id)+'>');
                        } else {
                            $(this).html('<input id="i_'+id+'" type="checkbox" class="notice" name="'
                            +id+'" '+echo_photoOnChange(id)+'>');
                        }
                    } else if (fieldname == 'note_con' || fieldname == 'note_ins'
                        || fieldname == 'note_eng' || fieldname == 'note_exp') {
                        $(this).html('<textarea id="i_'+id+'" cols="20" rows="4" class="notice" name="'
                        +id+'" '+echo_photoOnChange(id)+'>'+value+'</textarea><button>儲存已修改資訊</button>');
                    } else if (fieldname == 'position') {
                        if(value) {
                            $(this).html('<input id="i_'+id+'" type="text" class="notice" name="'
                            +id+'" value="'+value+'" '+echo_photoOnChange(id)+'>');
                        } else {
                            $(this).html('<input id="i_'+id+'" type="text" class="notice" name="'
                            +id+'" value="請填椿號位置或相片名稱" onBlur="if(this.value==\'\') this.value=\'請填椿號位置或相片名稱\'" onFocus="if(this.value.indexOf(\'請\')!=-1) this.value = \'\' " '+echo_photoOnChange(id)+'/>');
                        }
                    } else if (fieldname == 'photodate'){
                        $(this).html('<input id="i_'+id+'" size="10" type="text" class="notice" name="'
                        +id+'" value="'+value+'" '+echo_photoOnChange(id)+'>');

                        $.datepicker.setDefaults({showOn: 'both', buttonImageOnly: true,
                        dateformat: 'yy/mm/dd',
                        buttonImage: '/media/jquery-plugins/calender.png', buttonText: ''});
                        $(this).find('input').each(function(){
                            $(this).datepicker();
                        });
                    }
                    $(this).removeClass('canedit');
            }).end().find('.order').each(function(){
                var id = $(this).attr('id').replace('order_', '');
                if ($('#photolist_'+id).text()) {
                    $('#showfile_'+id).html($('<div></div>').css({
                        'background-image': 'url(/media/images/uploading.gif)',
                        'background-repeat': 'no-repeat',
                        'width': '400px', 'height': '300px'
                    }));
                }
            });
            $('#RightPane #photos').find('.toedit').click();
            $('#RightPane').scrollTop(0);
            $('#RightPane #photos .id_updatePhotoInfo').each(function(){
                var $obj = $(this);
                $obj.click(function(){
                    var photo_id = $(this).attr('photo_id');
                    var comment = $(this).next().next().val();
                    $.receiveJSON('/engphoto/updatephotoinfo/'+photo_id+'/', {'fieldname': 'comment',
                    'value': comment, 'csrfmiddlewaretoken': token},
                    function(json){
                        if (!json['status']){
                            alert('您的意見未儲存成功!');
                        } else {
                            $('#'+json['type']+'_'+photo_id).html(comment.replace(/\n/gi, '<br>'));
                        }
                    });
                });
            });
        }
    });
}
var changeNeed = function () {
    var $id = $(this);
    var id = $id.attr('id');
    var res = cutContentTypeString(id);
    var value = $id.val();
    $.receiveJSON('/engphoto/changeneed/'+id+'/', {'value': value, 'csrfmiddlewaretoken': token}, function(json){
        if (json['status'] == false){
            alert(json['message']);
            $id.val(json['value']);
            return false;
        } else {
            var $item = $('li#'+res['row_id'], $('#container-checkpointtab1_'+project_id));
            var $item_base = $('li#'+res['row_id'], $('#base'));
            $('span.need', $item).text(value);
            $('span.need', $item_base).text(value);
        }
    });
}
var toEdit_engphoto = function () {
    var $obj = $(this);
    if ($obj.attr('input') == 'true'){ return false; }
    $('td[@input=true]').each(function(){
        var $input = $(this).children();
        if ($input.attr('value')) {
            if ($input.attr('id').match('_need_')){
                changeNeed($(this).children());
            } else {
                updateMe($(this).children());
            }
        }
        fromEdit_engphoto($input);
    }) // 將其他 input 改成純文字。
    var value = $obj.text();
    var fieldname = $obj.attr('fieldname');
    var id = 'c' + $obj.attr('id');
    if (fieldname == 'name'){
        var size = 10;
    } else if (fieldname == 'help') {
        var size = 42;
    } else if (fieldname == 'need') {
        var size = 3;
    }
    if (fieldname == 'need'){
        var input = $('<input onBlur="changeNeed($(this))" id="'+id+'"size="'+size
        +'" type="text" value="'+value+'" />');
    } else {
        var input = $('<input onBlur="updateMe($(this))" id="'+id+'"size="'+size
        +'" type="text" value="'+value+'" />');
    }
    $obj.html('').append(input).attr('input', 'true');
}
var fromEdit_engphoto = function($obj){
    var $td = $obj.parent();
    $td.attr('input', 'false');
    $td.html($obj.val());
    var value = $obj.val();
    $td.click(toEdit_engphoto);
    return value;
}
var createCheckPoint = function(id){
    makeAllfromEdit();
    var node = $('#'+id);
    var kind = node.attr('kind');
    var kindname = kind == 'checkpoint' ? '查驗點' : '查驗點群組';
    var name = node.find('span:first').text();
    var $deleteInput = $('#form input[@name="delete"]', $('#edit_context_menu_'+id));
    var $createInput = $('#form input[@name="create"]', $('#edit_context_menu_'+id));
    var $createcheckpointInput = $('#form input[@name="create_checkpoint"]', $('#edit_context_menu_'+id));
    if ($deleteInput.attr('checked')){
        if (kindname == '查驗點') {
            var message = '查驗點，請注意! 其下的相片也會一併刪除';
        } else {
            var message = '查驗點群組，請注意! 其中的查驗點及相片也會一併刪除';
        }
        if (confirm('確定刪除「'+name+'」'+message)){
            var uri_id = $deleteInput.attr('id');
            $.receiveJSON('/common/'+uri_id+'/deleterow/', {'csrfmiddlewaretoken': token}, function(json){
                if (json['status'] == true){
                    alert('已刪除「'+name+'」'+kindname);
                    getActualCheckPoint(project_id, '#base');
                    getActualCheckPoint(project_id, '#container-checkpointtab1_'+project_id);
                } else {
                    alert('無法刪除「'+name+'」'+kindname);
                }
            });
        }
    }
    if ($createInput.attr('checked')){
        $.receiveJSON('/engphoto/addcheckpoint/'+id+'/', {'csrfmiddlewaretoken': token}, function(json){
            if (json['status'] == true){
                alert('已新增'+kindname);
                getActualCheckPoint(project_id, '#base');
                getActualCheckPoint(project_id, '#container-checkpointtab1_'+project_id);
            } else {
                alert('無法新增'+kindname);
            }
        });
    }
    if ($createcheckpointInput.attr('checked')){
        $.receiveJSON('/engphoto/addcheckpoint/'+id+'/', {type: 'child_checkpoint', 'csrfmiddlewaretoken': token}, function(json){
            if (json['status'] == true){
                alert('已新增查驗點');
                getActualCheckPoint(project_id, '#base');
                getActualCheckPoint(project_id, '#container-checkpointtab1_'+project_id);
            } else {
                alert('無法新增查驗點');
            }
        });
    }
    getActualCheckPoint(project_id, '#base');
    getActualCheckPoint(project_id, '#container-checkpointtab1_'+project_id);
    $('#edit_context_menu_'+id).dialog('close');
}
var afterContextMenu = function($node){
    var id = $node.attr('id');
    $('.edit_righthand_menu').remove();
    var $editRightHandMenu = $('<div id="edit_righthand_menu_'+id+'" class="flora edit_righthand_menu"></div>'); 
    $editRightHandMenu.insertAfter($('#MenuBar'));
    var html = '請直接點選「查驗點群組」之下或是「查驗點」之後的圖示<br/><br/>';
    html += '圖示說明：<br/>';
    html += '<img title="新增查驗點群組" src="/media/images/adddir.png"/>: 在該群組後「新增查驗點群組」<br/>';
    html += '<img title="新增查驗點" src="/media/images/additem.png"/>: 在該群組內「新增查驗點」<br/>';
    html += '<img title="編輯" src="/media/images/edit.png"/>: 「編輯」查驗點群組或是查驗點<br/>';
    html += '<img title="刪除" src="/media/images/delete.png"/>: 「刪除」查驗點群組或是查驗點<br/>';

    $editRightHandMenu.html(html).dialog({
        title: '手動新增方法說明:',
        //modal: true,
        //overlay: {opacity: 0.8, background: "black"},
        buttons: {
            '關閉本視窗': function(){
                $editRightHandMenu.dialog('close');
            }
        },
        width: 470,
        height: 240
    });
    $editRightHandMenu.dialog('open');
    return false;
}
var addDirCheckPoint = function(){
    var $id = $(this).parent();
    var id = $id.attr('id');
    var contenttype_id = $id.attr('contenttype_id');
    $.get('/engphoto/addcheckpoint/'+id+'/', '', function(json){
        if (json['status'] != true){
            alert('無法新增查驗點群組');
        } else {
            var new_dir = '<ul>';
            new_dir += '<li class="line">&nbsp;</li><li id="'+json['id']+'" contenttype_id="'+contenttype_id+'" kind="dir" class="folder-open">';
            new_dir += '<img style="float: left;" class="trigger" src="/media/jquery-plugins/tree/images/spacer.gif" border="0"><span class="help" title="無說明"><span class="name">**查驗點群組**</span>(<span id="checkpointuploadnum">0</span>/<span class="need">0</span>)</span><br>';
            new_dir += '<img class="addCPDir create" title="新增查驗點群組" src="/media/images/adddir.png"> ';
            new_dir += '<img class="addCP create" title="新增查驗點" src="/media/images/additem.png"> '; 
            new_dir += '<img class="modify" title="編輯查驗點群組" src="/media/images/edit.png"> ';
            new_dir += '<img class="delete" title="刪除查驗點群組" src="/media/images/delete.png"> ';
            new_dir += '<ul></ul></li>';
            new_dir += '</ul>';
 
            var $new_dir = $(new_dir);
            $new_dir.find('.addCPDir').each(function(){
                $(this).click(addDirCheckPoint);
            }).end().find('.addCP').each(function(){
                $(this).click(addSingleCheckPoint);
            }).end().find('.delete').each(function(){
                $(this).click(deleteCheckPoint);
            }).end().find('.modify').each(function(){
                $(this).click(editCheckPointDialog);
            });
            $new_dir.insertAfter($id.parent());
        }
    }, 'json');
}

var editCheckPoint = function(id) {
    var $id = $('#'+id);
    var kind = $id.attr('kind');
    var name = $('span.name', $id).text();
    var help = $('span:first', $id).attr('title');
    var need = $('.allphotonum', $id).text();
    var $form = $('#checkpoint_form_'+id);
    var form_name = $('.name', $form).val();
    var form_need = $('.need', $form).val();
    var form_help = $('.help', $form).val();

    var $editCheckPointDialog = $('#edit_checkpoint_dialog_'+id); 
    $editCheckPointDialog.dialog('close');
}

var editCheckPointDialog = function() {
    var $id = $(this).parent();
    var id = $id.attr('id');
    var contenttype_id = $id.attr('contenttype_id');
    var kind = $id.attr('kind');
    var name = $('span.name:first', $id).text();
    var help = $('span:first', $id).attr('title');
    var need = $('span.need', $id).text();

    $('.editCheckPointDialog').remove();
    var $editCheckPointDialog = $('<div id="edit_checkpoint_dialog_'+id+'" class="flora editCheckPointDialog"></div>'); 
    $editCheckPointDialog.insertAfter($('#MenuBar'));
    var html = '';
    html += '<ul id="checkpoint_form_'+id+'">';
    html += '<li>名稱: <input type="text" class="name" id="ct'+contenttype_id+'_name_r'+id+'" value="'+name+'"/></li>';
    if (kind != 'dir'){
        html += '<li>張數: <input type="text" class="need" id="ct'+contenttype_id+'_need_r'+id+'" value="'+need+'"/><br/>(所設定張數不可少於已上傳張數)<br/><br/></li>';
    }
    html += '<li>說明: </li>';
    html += '<li><textarea id="ct'+contenttype_id+'_help_r'+id+'">'+help+'</textarea></li>';
    html += '</ul>';
    $editCheckPointDialog.html(html).dialog({
        title: '編輯 ' + name,
        //modal: true,
        //overlay: {opacity: 0.8, background: "black"},
        buttons: {
            '確定儲存並關閉本視窗': function(){
                editCheckPoint(id);
            },
            '關閉本視窗': function(){
                $editCheckPointDialog.dialog('close');
            }
        },
        width: 500,
        height: 300
    }).find('.name').each(function(){
        $(this).change(onChangeUpdate);
    }).end().find('.need').each(function(){
        $(this).change(changeNeed);
    }).end().find('textarea').each(function(){
        $(this).change(onChangeUpdate);
    });
    $editCheckPointDialog.dialog('open');
}
var cutContentTypeString = function(s){
    match = /^ct([0-9]+)_(\w+)_r([0-9]+)$/.exec(s);
    if (!match){
        return {}
    } else {
        return {'fieldname': match[2],
            'contenttype_id': match[1],
            'row_id': match[3]
        }
    }

}
var onChangeUpdate = function() {
    var id = $(this).attr('id');
    var value = $(this).val();
    $.receiveJSON('/common/'+id+'/', {'value': value, 'csrfmiddlewaretoken': token}, function(json){
        if (json['status'] != true){
            alert(json['message']);
        } else {
            res = cutContentTypeString(id);
            var $item = $('#'+res['row_id'], $('#container-checkpointtab1_'+project_id));
            var $item_base = $('#'+res['row_id'], $('#base'));
            if (res['fieldname'] == 'name') {
                $('span.name:first', $item).text(value);
                $('span.name:first', $item_base).text(value);
            } else if (res['fieldname'] == 'help') {
                $('span.help:first', $item).attr('title', value);
                $('span.help:first', $item_base).attr('title', value);
            }
        }
    });
}

var addSingleCheckPoint = function(){
    var $id = $(this).parent();
    var id = $id.attr('id');
    var contenttype_id = $id.attr('contenttype_id');
    $.receiveJSON('/engphoto/addcheckpoint/'+id+'/', {'type': 'child_checkpoint', 'csrfmiddlewaretoken': token}, function(json){
        if (json['status'] != true){
            alert('無法新增查驗點');
        } else {
            var new_item = '<li class="line">&nbsp;</li>';
            new_item += '<li class="doc" id="'+json['id']+'" contenttype_id="'+contenttype_id+'" kind="checkpoint">';
            new_item += '<span class="help" title="無說明"><span class="name">**查驗點**</span>(<span id="photonow_'+json['id']+'">0</span>/<span class="need">0</span>)</span> ';
            new_item += '<img class="modify" title="編輯查驗點" src="/media/images/edit.png"/> ';
            new_item += '<img class="delete" title="刪除查驗點" src="/media/images/delete.png"/>';
            new_item += '</li>';
            var $new_item = $(new_item);
            $new_item.find('.delete').each(function(){
                $(this).click(deleteCheckPoint);
            }).end().find('.modify').each(function(){
                $(this).click(editCheckPointDialog);
            }).end().find('.name').each(function(){
                $(this).click(showCheckPointView);
            });
            $('ul', $id).prepend($new_item);
        }
    });
}
var deleteCheckPoint = function () {
    var $id = $(this).parent();
    var id = $id.attr('id');
    var name = $('span:first', $id).text();
    var contenttype_id = $id.attr('contenttype_id');
    if ($id.attr('kind') == 'dir') {
        var isDir = true;
        var message = '確定刪除「'+name+'」查驗點群組，其所包含的查驗點及已上傳之施工相片將同時刪除!';
    } else {
        var isDir = false;
        var message = '確定刪除「'+name+'」查驗點，其所包含的施工相片將同時刪除!';
    }
    if(!confirm(message)){
        return false;
    } else {
        $.receiveJSON('/common/deleterow/', {'ContentType_id': contenttype_id, 'row_id': id, 'csrfmiddlewaretoken': token}, function(json){
            if (json['status'] == true){
                if (isDir){
                    $('#'+id, $('#base')).parent().remove();
                    $('#'+id, $('#container-checkpointtab1_'+project_id)).parent().remove();
                } else {
                    $('#'+id, $('#base')).prev().remove();
                    $('#'+id, $('#container-checkpointtab1_'+project_id)).prev().remove();
                    $('#'+id, $('#base')).remove();
                    $('#'+id, $('#container-checkpointtab1_'+project_id)).remove();
                }
            } else {
                alert('無法刪除「'+name+'」');
            }
        });
    }
}

var getActualCheckPoint = function (id, plane) {
    $.get('/engphoto/'+id+'/getactualcheckpoint/', '',function(html) {
        $(plane+'.simpleTree').html(html).find('.addCPDir').each(function(){
            $(this).click(addDirCheckPoint);
        }).end().find('.addCP').each(function(){
            $(this).click(addSingleCheckPoint);
        }).end().find('.modify').each(function(){
            $(this).click(editCheckPointDialog);
        }).end().find('.delete').each(function(){
            $(this).click(deleteCheckPoint);
        });
        $(plane+'.simpleTree #expand-folder').toggle(function(){
            $(this).text('全部展開');
            $(this).parent().parent().parent().find('li.folder-open-last').each(function(){
                $(this).removeClass('folder-open-last').addClass('folder-close-last').find('ul').hide();
            });
        }, function (){
            $(this).text('全部折疊');
            $(this).parent().parent().parent().find('li.folder-close-last').each(function(){
                $(this).removeClass('folder-close-last').addClass('folder-open-last').find('ul').show();
            });
        });
        var canedit = $(plane+'.simpleTree #editcheckpoint').attr('value') == 'true' ? true : false;
        if (canedit){
            $('#add_checkpoint_head').show();
            $('#add_checkpoint_foot').show();
            var afterContextMenu_function = afterContextMenu;
            var afterMove_function = function(dir_id, checkpoint_id, priority){
                //alert(dir_id.attr('id')+','+checkpoint_id.attr('id')+','+priority);
                $.receiveJSON('/engphoto//sortcheckpoint/', {'dir_id': dir_id.attr('id'),
                'checkpoint_id': checkpoint_id.attr('id'), 'priority': priority, 'csrfmiddlewaretoken': token},
                function(json) {
                    if (json['status'] == false){
                        alert(json['message']);
                        location.reload(true);
                    }
                });
                return false;
            }
        } else {
            var afterContextMenu_function = false;
            var afterMove_function = false;
        }
        var simpleTreeCollection = $(plane+'.simpleTree').simpleTree({
            drag: canedit,
            autoclose: false,
            afterContextMenu: afterContextMenu_function,
            afterClick: function(node){
                //TODO 因為選取後，字會加外框，在 ie 中會造成字往下移的現象。
                getphotos('bycheckpoint', node.attr('kind'), node.attr('id'));
            }, 
            afterDblClick:function(node){
                //TODO 因為選取後，字會加外框，在 ie 中會造成字往下移的現象。
                getphotos('bycheckpoint', node.attr('kind'), node.attr('id'));
            },
            afterMove: afterMove_function,
            afterAjax:function() { //alert('Loaded');
            },
            animate:true
            //,docToFolderConvert:true
        });
    });
}

var getProjectCheckPoint = function(obj, project_id){
    var $obj = $(obj);
    var id = $obj.attr('id');
    $obj.parent().parent().find('#container-project_checkpoint_'+project_id).each(function(){
        $(this).remove();
    });
    $obj.parent().append($('<div id="container-project_checkpoint_'+project_id+'"></div>'));
    $.receiveJSON('/engphoto/'+id+'/getprojectcheckpoints/', {'csrfmiddlewaretoken': token}, function(json){
        if (json['status'] == true){
            layoutCheckPoint(project_id, 'project_checkpoint', json['CheckPoints']);
        } else {
            $('#container-project_checkpoint_'+project_id).html('<p>無查驗點</p>');
        }
    });
}
var setCheckPoint = function(id, name){
    project_id = id; //將全域變數 project_id 值設為 id
    if ($('#checkpoint'+id).html()){
        $('#checkpoint'+id).dialog('close');
        $('#checkpoint'+id).dialog('open');
    } else {
        var $checkpoint = $('<div id="checkpoint'+id+'" class="flora"></div>'); 
        $checkpoint.insertAfter($('#MenuBar'));

        var html = '';
        html += '        <div id="checkpointtab'+id+'" class="flora">';
        html += '            <ul>';
        html += '                <li><a class="checkpointtabs" href="#checkpointtab1_'+id+'"><span>手動新增編輯查驗點</span></a></li>';
//        html += '                <li><a class="checkpointtabs" href="#checkpointtab2_'+id+'"><span>樣版新增</span></a></li>';
        html += '                <li><a class="checkpointtabs" href="#checkpointtab3_'+id+'"><span>套用舊工程新增</span></a></li>';
        html += '            </ul>';
        html += '            <div id="checkpointtab1_'+id+'">';
        
        html += '欲簡易新增查驗點，請直接點選「查驗點群組」之下或是「查驗點」之後的圖示<br/><br/>';
    	html += '圖示說明：<br/>';
    	html += '<img title="新增查驗點群組" src="/media/images/adddir.png"/>: 在該群組後「新增查驗點群組」<br/>';
    	html += '<img title="新增查驗點" src="/media/images/additem.png"/>: 在該群組內「新增查驗點」<br/>';
    	html += '<img title="編輯" src="/media/images/edit.png"/>: 「編輯」查驗點群組或是查驗點<br/>';
    	html += '<img title="刪除" src="/media/images/delete.png"/>: 「刪除」查驗點群組或是查驗點<br/>';
        html += '_____________________________________________________<br><br>';
        html += '                <ul id="container-checkpointtab1_'+id+'" class="simpleTree"></ul>';
        html += '<div class="contextMenu" id="container-checkpointtab1_'+id+'Menu">';
        html += '    <ul>';
        html += '        <li id="">尚在努力中</li>';
        html += '        <li id="edit"><img src="/media/jquery-plugins/tree/images/page_edit.png" />編輯</li>';
        html += '        <li id="delete"><img src="/media/jquery-plugins/tree/images/page_delete.png" />刪除</li>';
        html += '    </ul>';
        html += '</div>';
        html += '            </div>';
        html += '            <div id="checkpointtab2_'+id+'">';
        html += '                <div id="container-checkpointtab2_'+id+'"></div>';
        html += '            </div>';
        html += '            <div id="checkpointtab3_'+id+'">';
        html += '                <div id="container-checkpointtab3_'+id+'"></div>';
        html += '            </div>';
        html += '        </div>';
        $checkpoint.html(html);
        $checkpoint.find('#checkpointtab'+id+' > ul').tabs();
        getActualCheckPoint(id, '#container-checkpointtab1_'+id);

        var type = '';
        $checkpoint.find('.checkpointtabs').click(function(){
            var array = $(this).attr('href').split('#');
            var tabname_id = array[1].split('_');
            var tabname = tabname_id[0].replace('#', '');
            var id = tabname_id[1];
            if (tabname == 'checkpointtab1') {
                type = 'checkpointtab1';
                getActualCheckPoint(id, '#container-checkpointtab1_'+id);
            }
            if (tabname == 'checkpointtab2') {
                type = 'checkpointtab2';
                if ($('#container-checkpointtab2_'+id).html() == ''){
                    getTemplate(id);
                }
            }
            if (tabname == 'checkpointtab3') {
                type = 'project_checkpoint';
                if ($('#container-checkpointtab3_'+id).html() == ''){
                    getOwnProject(id);
                }
            }
            return false;
        });

        $checkpoint.dialog({
            title: '編輯查驗點: ' + name,
            //modal: true,
            //overlay: {opacity: 0.8, background: "black"},
            buttons: {
                '新增查驗點': function(){
                    if (type == 'checkpointtab2' || type == 'project_checkpoint'){
                        var querystring = $('#form'+type+'2_'+id).find('input[@type=checkbox]:checked').serialize().split('&');
                        var project_id = id;
                        var qs = {'id': project_id, 'csrfmiddlewaretoken': token};
                        for (var i=0;i < querystring.length; i++) {
                            var chkid = querystring[i].split('=')[0].split('_')[1];
                            var num = $('#form'+type+'2_'+id+' input[@name=checkpointnum_'+chkid+']').attr('value');
                            qs[chkid] = num;
                        }
                        addCheckPoint(project_id, type, qs);
                    } else {
                        var $requiredCheckPoint = $('.root ul li:first').next();
                        afterContextMenu($requiredCheckPoint);
                    }
                },
                '關閉本視窗': function(){
                    getActualCheckPoint(project_id, '#base');
                    $checkpoint.dialog('close');
                }
            },
            width: 640,
            height: 545
        });
        $checkpoint.dialog('open');
    }
    return false;
}
var OnOffCoordinate = function(){
    $('#coordinate').toggle();
    var left = $('#picture').position().left;
    var top = $('#picture').position().top;
    $('#coordinate').css({ 'left': left, 'top': top });
}
var changeCheckPoint = function(){
    getPhotoById($('#checkpoints option:selected').val(), type);
}
var setSize = function(){
    var width = $(window).width();
    var height = $(window).height();
    var fitheight = height - margin * 2;
    var fitwidth = fitheight / 3 * 4;
    intOverallDelta = 0;
    if ((fitwidth + 200) > width) {
        fitwidth = width - 200;
        fitheight = fitwidth / 4 * 3;
    }
    $('#menu-container').height(fitheight).width(width-fitwidth-margin*2)
    .css({'left': (fitwidth + margin),'top': margin});
    $('#picture-container').height(fitheight).width(fitwidth).css({'left': margin,'top': margin});
    $('#picture').height(fitheight).width(fitwidth).css({'left': 0, 'top': 0});
    $('#coordinate').height(fitheight).width(fitwidth).css({'left': 0, 'top': 0});

    var leftone_height = $('#leftone').height();
    var rightone_width = $('#rightone').width();
    $('#leftone').css({'left': 0, 'top': (fitheight - leftone_height)/2});
    $('#rightone').css({'left': fitwidth - rightone_width, 'top': (fitheight - leftone_height)/2});

    var base = (fitheight - leftone_height) / 2 - margin - 30;
    var level_height = $('#level').height();
    var big_height = $('#big').height();
    var CH_height = $('#CH').height();
    $('#small').css({'left': fitwidth - 28, 'top': base});
    $('#CH').css({'left': fitwidth - 31, 'top': base - scale_margin - CH_height/2});
    $('#level').css({'left': fitwidth - 28, 'top': base - level_height - scale_margin});
    $('#big').css({'left': fitwidth - 28,
    'top': base - level_height - scale_margin - big_height - scale_margin});
};
var setPhoto = function(prePhoto_id, photo_id, postPhoto_id){
    var picWidth = $('#picture-container').width();
    var picHeight = picWidth / 4 * 3;
    $('#coordinate').height(picHeight).width(picWidth).css({'left': 0, 'top': 0});
    $('#picture').attr('src', photoList[photo_id]['link']).height(picHeight).width(picWidth)
    .css({'left': 0, 'top': 0});
    $(document).attr('title', photoList[photo_id]['titlename'].replace('(正常)', '#'+orderList[photo_id]));
    var infos = new Array('inspector_check', 'note_con', 'note_ins', 'note_eng', 'note_exp', 'photodate', 'size', 'updatetime', 'name');
    for (var k = 0; k < infos.length; k++){
        $('#'+infos[k]).text('');
        $('#'+infos[k]).text(photoList[photo_id][infos[k]]);
    }

    if (prePhoto_id) {
        $('#left-picture').attr('src', photoList[prePhoto_id]['link'])
        $('#leftone').show().attr('value', prePhoto_id);
    } else {
        $('#leftone').hide();
    }
    if (postPhoto_id) {
        $('#right-picture').attr('src', photoList[postPhoto_id]['link']);
        $('#rightone').show().attr('value', postPhoto_id);
    } else {
        $('#rightone').hide();
    }
    $('#picture').show();
    $('#picCanvas').hide();
}
var getPhotoById = function(photo_id, type){
    photo_id = Number(photo_id);
    nowPhoto_id = photo_id;
    if (type == 'checkpoint') {
        var List = checkpointList;
    } else if (type == 'time'){
        var List = timeList;
    } else if (type == 'defect'){
        var List = defectList;
    } else if (type == 'trash'){
        var List = trashList;
    }
    for (var l=0; l < List.length; l++){
        if (List[l] == photo_id){
            var Index = l;
            break;
        }
    }
    $('#serialnumber').text(l+1);
    $('#allphotos').text(List.length);
    if (List.length == 1) {
        var dev_null = 'nothing';
    } else if (Index > 0 && Index < (List.length-1)){
        var prePhoto_id = List[Index - 1];
        var postPhoto_id = List[Index + 1];
    } else if (Index == 0) {
        var prePhoto_id = List[List.length-1];
        var postPhoto_id = List[Index + 1];
    } else if (Index == (List.length-1)) {
        var prePhoto_id = List[Index - 1];
        var postPhoto_id = List[0];
    }
    var queryList = [];
    if (! photoList[prePhoto_id]){
        queryList.push(prePhoto_id);
    }
    if (! photoList[photo_id]){
        queryList.push(photo_id);
    }
    if (! photoList[postPhoto_id]){
        queryList.push(postPhoto_id);
    }
    if (queryList.length > 0){
        $.get('/engphoto/'+project_id+'/getphotosbyid/'+queryList.join('/')+'/', {}, function(json){
            if (json['status'] == false){
                alert(json['message']);
            } else {
                for (var k in json['photos']){
                    photoList[k] = json['photos'][k];
                }
                setPhoto(prePhoto_id, photo_id, postPhoto_id);
            }
        }, 'json');
    } else {
        //setTimeout("setPhoto("+prePhoto_id+", "+photo_id+", "+postPhoto_id+")", 500);
        setPhoto(prePhoto_id, photo_id, postPhoto_id);
    }
}

var alignTogether = function(){
    var left = $(this).position().left;
    var top = $(this).position().top;
    $('#picture').css({ 'left': left, 'top': top });
    $('#coordinate').css({ 'left': left, 'top': top });
};
var firefox_rotate = function (switch_angle, picWidth, picHeight) {  
    var picture = document.getElementById('picture');  
    var picCanvas = document.getElementById('picCanvas');  
    picCanvas.setAttribute('width', picWidth);  
    picCanvas.setAttribute('height', picHeight);
    var picCanvasContext = picCanvas.getContext('2d');  
    picCanvasContext.rotate(switch_angle * Math.PI / 180);
    switch(switch_angle){
        case 90:
            picCanvasContext.drawImage(picture, 0, -picHeight/4*3, picHeight, picHeight/4*3);
        case 180:
            picCanvasContext.drawImage(picture, -picWidth, -picHeight, picWidth, picHeight);
        case 270:
            picCanvasContext.drawImage(picture, -picHeight, 0, picHeight, picHeight/4*3);
    }
    $('#picture').hide();
    $('#coordinate').css({'left': 0, 'top': 0});
    $('#picCanvas').show();
};
var ie_rotate = function(swith_angle, picWidth, picHeight){
    var rotate_type = swith_angle /  90;
    if (rotate_type == 1) {
        $('#picture').draggable('disable').width(picHeight).height(picHeight/4*3);
    } else if (rotate_type == 2) {
        $('#picture').draggable('disable').width(picWidth).height(picHeight);
    } else if (rotate_type == 3) {
        setSizeAndPosition($('#picture'), picWidth-picHeight, 0, picWidth, picHeight);
        $('#picture').draggable('disable').width(picHeight).height(picHeight/4*3);
    }
    document.getElementById("ie-rotator").style.filter=
    'progid:DXImageTransform.Microsoft.BasicImage(rotation=' + rotate_type + ')';
}
var rotate = function(obj, p_deg){
    var picWidth = $('#picture-container').width();
    var picHeight = picWidth / 4 * 3;
    angle =  (angle + p_deg) % 360;
    if (angle != 0){
        $('#scale').hide();
        $(obj).attr('value', '順時針旋90°(旋轉狀態下無法拖拉/放大/縮小)').attr('width', '280');
    }
    else {
        $('#scale').show();
        $(obj).attr('value', '順時針旋90°');
    }
    if ($.browser.msie){
        setSizeAndPosition($('#picture'), 0, 0, picWidth, picHeight);
        if (angle == 0) {
            $('#picture').draggable('enable').width(picWidth).height(picHeight)
            $('#coordinate').draggable('enable');
            document.getElementById("ie-rotator").style.filter='';
            getPhotoById(nowPhoto_id, type);
        } else {
            $('#coordinate').draggable('disable');
            ie_rotate(angle, picWidth, picHeight);
        }
    } else {
        if (angle == 0) {
            $('#coordinate').draggable('enable');
            getPhotoById(nowPhoto_id, type);
        } else {
            $('#coordinate').draggable('disable');
            firefox_rotate(angle, picWidth, picHeight);
        }
    }
}
var setSizeAndPosition = function(elm, x, y, w, h){
    elm.css({ 'width': w, 'height': h, 'left': x, 'top': y });
}
var setCHHeight = function(){
    var width = $(window).width();
    var height = $(window).height();
    var fitheight = height - margin * 2;
    var fitwidth = fitheight / 3 * 4;
    if ((fitwidth + 200) > width) {
        fitwidth = width - 200;
        fitheight = fitwidth / 4 * 3;
    }
    var range = $('#level').height();
    var leftone_height = $('#leftone').height();
    var base = (fitheight - leftone_height) / 2 - margin - 30;
    var level_height = $('#level').height();
    var CH_height = $('#CH').height();
    $('#CH').css({'top': base-scale_margin-CH_height/2-level_height*intOverallDelta/maxScale});
}
var bigPic = function(){
    var oriwidth = $('#picture-container').width();
    var oriheight = oriwidth / 4 * 3;
    var left = $('#picture').position().left;
    var top = $('#picture').position().top;
    var blocks = new Array($('#picture'), $('#coordinate')); //可放大縮小的區塊
    var step = maxScale / 10;
    intOverallDelta += step;
    var scale = (100 + intOverallDelta) / 100;
    if (intOverallDelta <= maxScale) {
        for (var k = 0; k < blocks.length; k++){
            setSizeAndPosition(blocks[k], left-oriwidth*scale*step/maxScale,
            top-oriheight*scale*step/maxScale,oriwidth * scale,oriheight * scale)
        }
    } else {
        intOverallDelta = maxScale;
    }
    setCHHeight();
}
var smallPic = function(){
    var oriwidth = $('#picture-container').width();
    var oriheight = oriwidth / 4 * 3;
    var left = $('#picture').position().left;
    var top = $('#picture').position().top;
    var blocks = new Array($('#picture'), $('#coordinate')); //可放大縮小的區塊
    var step = maxScale / 10;
    intOverallDelta -= step;
    if (intOverallDelta <= 0) {
        intOverallDelta = 0
        for (var k = 0; k < blocks.length; k++){
            setSizeAndPosition(blocks[k], 0, 0, oriwidth, oriheight);
        }
    } else {
        var scale = (100 + intOverallDelta) / 100;
        for (var k = 0; k < blocks.length; k++){
            setSizeAndPosition(blocks[k], left+oriwidth*scale*step/maxScale,
            top+oriheight*scale*step/maxScale,oriwidth * scale,oriheight * scale)
        }
    }
    setCHHeight();
}
var setAccordion_menu = function(){
    $('.acc').click(function(){
        $('.acc').each(function(){
            $(this).removeClass('active').removeClass('selected');
        });
        $(this).addClass('active').addClass('selected');
        var type = $(this).attr('id');
        if (type == 'bycheckpoint'){
            $('#content_checkpoint').show();
        } else {
            $('#content_checkpoint').hide();
            if ($('#'+type+' .content').text() == '' || menu_type != type){
                $('#'+type+' .content').text('');
                $.receiveJSON('/engphoto/getphotonum/'+$(this).attr('id')+'/', {'csrfmiddlewaretoken': token}, function(json){
                    if (json['page'] == 0){
                        $('#'+json['type']+' .content').append($('<div>無</div>'));
                    } else {
                        var message = '';
                        for (var i = 0; i < json['page']; i++){
                            message += '<div id="page_'+i+'" class="page">第 ' + (i+1) + ' 頁</div>';
                        }
                        $('#'+json['type']+' .content').append(message);
                        $('#'+json['type']+' .content').height(20*json['page']);
                    }
                    $('.page').click(function(){
                        $('.page').removeClass('now');
                        var page_id = $(this).attr('id').split('_')[1];
                        var type = $(this).parent().parent().attr('id');
                        getphotos(type, '', page_id);
                        $(this).addClass('now');
                    });
                });
            }
        }
        menu_type = type;
    });
}
var setEnough = function (id) {
    if (! confirm('確定放寬本施工相片的檔案大小限制?')){
        return false;
    } 
    $.receiveJSON('/engphoto/makeenough/'+id+'/', {'csrfmiddlewaretoken': token}, function(j){
        json = j['photos'][id];
        $('#movebutton_'+id+' button').show();
        $('#deletebutton_'+id+' button').show();

        if (json['thumbsrc']){
            var img = '<a href="/engphoto/bigpicture/'+id
            +'/" target="photo" onmouseover="style.cursor=\'pointer\'">'
            +'<img width="400" height="300" class="engphoto" src="/engphoto/getpic/'
            +json['thumbsrc']+'"></a>';

            $('#showfile_'+id).html(img); 
        }
        if (json['checkpoint_id']){
            var $photonow = $('#photonow_'+json['checkpoint_id']);
            $photonow.text(Number($photonow.text()) + 1);
        }

        if (json['size']){
            $('#size_'+id).text(json['size']);
        }

        if (json['photodate']){
            $photodate = $('#photodate_'+id);
            $photodate.text(json['photodate']);
        }
    });
    dialog_close('notenough', id);
}
var setNonduplicate = function (id) {
    if (! confirm('確定判定本施工相片為「非重複相片」?')){
        return false;
    } 
    $.receiveJSON('/engphoto/makenonduplicate/'+id+'/', {'csrfmiddlewaretoken': token}, function(j){
        json = j['photos'][id];
        $('#movebutton_'+id+' button').show();
        $('#deletebutton_'+id+' button').show();

        if (json['thumbsrc']){
            var img = '<a href="/engphoto/bigpicture/'+id
            +'/" target="photo" onmouseover="style.cursor=\'pointer\'">'
            +'<img width="400" height="300" class="engphoto" src="/engphoto/getpic/'
            +json['thumbsrc']+'"></a>';

            $('#showfile_'+id).html(img); 
        }
        if (json['checkpoint_id']){
            var $photonow = $('#photonow_'+json['checkpoint_id']);
            $photonow.text(Number($photonow.text()) + 1);
        }

        if (json['size']){
            $('#size_'+id).text(json['size']);
        }

        if (json['photodate']){
            $photodate = $('#photodate_'+id);
            $photodate.text(json['photodate']);
        }
    });
    dialog_close('duplicate', id);
}
var getNotEnough = function(id){
    if (!$('#notenough_dialog_'+id).length){
        $('body').append($('<div id="notenough_dialog_'+id+'"></div>'));
    }
    var $dialog = $('#notenough_dialog_'+id);
    $dialog.html('<div id="left-dialog"><h3 align="center">檔案大小未達 150Kb 的施工相片</h3></div>')

    $.receiveJSON('/engphoto/getphotosbynotenough/'+id+'/', {'csrfmiddlewaretoken': token}, function(json){
        if (json['notenough']){
            var link = json['notenough'][id]['thumbsrc'];
            var name = json['notenough'][id]['name'];
            var uploadtime = json['notenough'][id]['uploadtime'];
            var img_info = '<div><p><div id="name">'+name+'</div><div id="uploadtime">上傳時間：'
            +uploadtime+'</div></p><img src="/engphoto/getpic/'+link+'" /></div>';
            $('#left-dialog', $dialog).append($(img_info));
            if(json['delete'] && json['notenough'][id]['phototype'] == '正常'){
                var buttons = {
                    '移至待改善相簿': function() {
                        deletePhoto( '待改善相簿', -1, id );
                    },
                    '放寬本相片限制': function() {
                        setEnough( id );
                    },
                    '關閉本視窗': function(){
                        $dialog.dialog('close');
                    }
                }
            } else {
                var buttons = {
                    '關閉本視窗': function(){
                        $dialog.dialog('close');
                    }
                }
            }
        }

        $dialog.dialog({
            title: '檢視未達 150Kb 的施工相片',
            //modal: true,
            //overlay: {opacity: 0.8, background: "black"},
            buttons: buttons,
            width: 500,
            height: 450
        });
        $dialog.dialog('open');
    });
}
var getDuplicates = function(id){
    if (!$('#duplicate_dialog_'+id).length){
        $('body').append($('<div id="duplicate_dialog_'+id+'"></div>'));
    }
    var $dialog = $('#duplicate_dialog_'+id);
    $dialog.html('<div id="left-dialog"><h3 align="center">疑似重複的施工相片</h3></div><div id="right-dialog"><h3 align="center">先前上傳的施工相片</h3></div>')

    $.receiveJSON('/engphoto/getphotosbyduplicate/'+id+'/', {'csrfmiddlewaretoken': token}, function(json){
        if (json['suspend']){
            for (var k in json['suspend']){
                var link = json['suspend'][k]['thumbsrc'];
                var name = json['suspend'][k]['name'];
                var uploadtime = json['suspend'][k]['uploadtime'];
                var img_info = '<div><p><div id="name">'+name+'</div><div id="uploadtime">上傳時間：'
                +uploadtime+'</div></p><img src="/engphoto/getpic/'+link+'" /></div>';
                $('#left-dialog', $dialog).append($(img_info));
            }
            if (json['suspend'][id]['phototype'] != '正常') {
                $('#left-dialog h3', $dialog).text('重複的施工相片');
            
                var buttons = {
                    '關閉本視窗': function(){
                        $dialog.dialog('close');
                    }
                }
            } else {
                if(json['delete']){
                    var buttons = {
                        '確為重複相片，並移至待改善相簿': function() {
                            deletePhoto( '待改善相簿', -1, id );
                        },
                        '認定非重複相片': function() {
                            setNonduplicate( id );
                        },
                        '關閉本視窗': function(){
                            $dialog.dialog('close');
                        }
                    }
                } else {
                    var buttons = {
                        '關閉本視窗': function(){
                            $dialog.dialog('close');
                        }
                    }
                }
            }
        }

        var i = 0;
        for (var k in json['duplicates']){
            i += 1;
            if ((i % 2) == 1) { var row = 'odd'; }
            else { var row = 'even'; }
            var link = json['duplicates'][k]['thumbsrc'];
            var project_name = json['duplicates'][k]['project_name'];
            var name = json['duplicates'][k]['name'];
            var uploadtime = json['duplicates'][k]['uploadtime'];
            var img_info = '<div class="'+row+'"><p><div id="name">'+project_name+'/'+name
            +'</div><div id="uploadtime">上傳時間：'+uploadtime
            +'</div></p><img src="/engphoto/getpic/'+link+'" /></div>';
            $('#right-dialog', $dialog).append($(img_info));
        }
        if (i != 0){
            var width = 870;
        } else {
            $('#right-dialog h3', $dialog).text('');
            var width = 500;
        }

        $dialog.dialog({
            title: '檢視重複相片',
            //modal: true,
            //overlay: {opacity: 0.8, background: "black"},
            buttons: buttons,
            width: width,
            height: 500
        });
        $dialog.dialog('open');
    });
}
var makeDuplicateButton = function (photo_id){
    var $div = $('#showfile_'+photo_id);
    $div.html('');
    $div.append($('<img src="/media/engphoto/images/duplicatepicture.png" />'));
    $div.append($('<button onClick="getDuplicates('+photo_id+')">檢視重複相片</button>'));
}
var makeNotEnoughButton = function (photo_id){
    var $div = $('#showfile_'+photo_id);
    $div.html('');
    $div.append($('<img src="/media/engphoto/images/under150kb.png" />'));
    $div.append($('<button onClick="getNotEnough('+photo_id+')">檢視未達 150Kb 相片</button>'));
}
