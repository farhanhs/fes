function NewFileUploader($buttom, row_id, table_name){
    var buttom_id = $buttom.attr('id');
    var file_type = $buttom.attr('file_type');

    var uploader = new plupload.Uploader({
        runtimes: 'html5',
        browse_button: buttom_id,
        url: '/frcm/new_file_upload/',
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
                    if (file_type=='綜合試驗紀錄'){
                        var record_id = $buttom.attr('record_id');
                        for (i=0;i<file_num;i++){
                            var html = '';
                            html += '<li id="li_projectfile_' + files[i].id + '"><a id="file_link_' + files[i].id + '" href="">';
                            html += files[i].name + '</a>，上傳進度：<span id="file_percent_';
                            html += files[i].id + '">0 %</span><img class="deleteRow pointer ImageButtonHover"';
                            html += 'src="/static/project/image/plan_delete.png" width="20" table_name="projectfile"';
                            html += 'row_id="{{ file.id }}" row_name="' + files[i].name + '"';
                            html += 'id="file_img_' + files[i].id + '" module_name="frcm" remove_target="li_projectfile_{{ file.id }}" title="刪除檔案"></li>';
                            $('#waitting_for_upload_' + record_id).append(html);
                        }
                    } else {
                        for (i=0;i<file_num;i++){
                            $('#waitting_for_upload').append('<li id="li_projectfile_' + files[i].id + '">' + files[i].name + '，上傳進度：<div class="progress progress-striped active" style="width: 200px;"><div class="progress-bar progress-bar-warning" id="file_percent_' + files[i].id + '" style="width: 0%"></div></div></li>');
                        }
                    }
                    up.start();
                }else{
                    return false
                }
            },
            FileUploaded:function(up, file, res){
                var json = $.parseJSON(res.response);
                var html = $(json['html']);
                html.appendTo($('#table_files > tbody:last'));
                $(".deleteRow", html).click(deleteRow);
                $('.ClickShowInfo', html).click(ClickShowInfo);
                $('.BlurUpdateInfo', html).blur(BlurUpdateInfo);
                $('.edit_projectfile_tag', html).click(edit_projectfile_tag);
                $('.BlurUpdateInfo', html).keypress(function(event) {
                    var $obj = $(this);
                    if (!$obj.is("textarea") && event.which == 13){
                        $obj.blur();
                    }
                });
                $('#file_percent_' + file.id).parent().attr('class', 'progress');
                $('#file_percent_' + file.id).attr('class', 'progress-bar progress-bar-success');
                // 自動加入標籤
                var tag_id = $('#new_file').attr('tag_id');
                var tag_name = $('#new_file').attr('tag_name');
                if (tag_id && tag_id!='undefined' && tag_id!='all'){
                    var projectfile_id = json['id'];
                    var data = {
                        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
                    }
                    data['tag_add'] = tag_id;
                    $.ajax({
                        url: '/frcm/api/v2/projectfile/' + projectfile_id + '/',
                        type: 'PUT',
                        data: JSON.stringify(data),
                        contentType: 'application/json',
                        dataType: 'json',
                        success: function (json, text, xhr) {
                            var $span_tags = $('#span_tags_' + projectfile_id);
                            var html = $span_tags.html();
                            var $edit_projectfile_tag = $('#edit_projectfile_tag_' + projectfile_id);
                            var have_tags = $edit_projectfile_tag.attr('have_tags');
                            var $tr_ProjectFile = $('#tr_ProjectFile_' + projectfile_id);
                            var tr_class = $tr_ProjectFile.attr('class');
                            html +=  tag_name + '<br>';
                            have_tags += tag_id + ','
                            tr_class += ' tag_' + tag_id;
                            $span_tags.html(html);
                            $edit_projectfile_tag.attr('have_tags', have_tags);
                            $tr_ProjectFile.attr('class', tr_class);

                        },
                        error: function() {
                            // alert('FUCK');
                        }
                    })
                }
                $('#li_projectfile_' + file.id).remove();
            },
            UploadProgress:function(up, file) {
                $('#file_percent_' + file.id).attr('style', 'width: ' + file.percent + "%");
                $('#file_percent_' + file.id).html(file.percent + "%");
            }
        }
    });
    uploader.init();
}



function select_tag(){
    var $obj = $(this);
    var tag_id = $obj.attr('tag_id');
    var tag_name = $obj.attr('tag_name');
    $('.tag_all').hide();
    $('.select_tag').css('font-weight', 'inherit');
    $('.select_tag').css('background-color', '');
    console.log(tag_id);
    $('.tag_' + tag_id).show();
    $obj.css('font-weight', 'bolder');
    $obj.attr('style', 'background-color: yellow;');
    $('#new_file').attr('tag_id', tag_id);
    $('#new_file').attr('tag_name', tag_name);
}


function edit_projectfile_tag(){
    var $obj = $(this);
    var projectfile_id = $obj.attr('projectfile_id');
    var have_tags = $obj.attr('have_tags');
    var projectfile_name = $('#edit_part_name_' + projectfile_id).val();
    var tags_num = parseInt($('#tags_num').val(), 10);
    var tags_list = $('#tags_list').val().split(',');
    $('#projectfile_tag_dialog_div').attr('projectfile_id', projectfile_id);
    $('#projectfile_tag_dialog_name').html(projectfile_name + ' 標籤編輯');
    for (i=0;i<tags_list.length-1;i++){
        var str = tags_list[i] + ',';
        if (have_tags.indexOf(str)>-1){
            $('#tag_checkbox_' + tags_list[i]).prop('checked', true);
        } else {
            $('#tag_checkbox_' + tags_list[i]).prop('checked', false);
        }
    }
}


function add_or_remove_tag(){
    var $obj = $(this);
    var projectfile_id = $('#projectfile_tag_dialog_div').attr('projectfile_id');
    var tag_id = $obj.val();
    var tag_name = $obj.attr('tag_name');
    var data = {
        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
    }

    if ($obj.prop('checked')){
        data['tag_add'] = tag_id;
    } else {
        data['tag_remove'] = tag_id;
    }

    $.ajax({
        url: '/frcm/api/v2/projectfile/' + projectfile_id + '/',
        type: 'PUT',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json',
        success: function (json, text, xhr) {
            var $span_tags = $('#span_tags_' + projectfile_id);
            var html = $span_tags.html();
            var $edit_projectfile_tag = $('#edit_projectfile_tag_' + projectfile_id);
            var have_tags = $edit_projectfile_tag.attr('have_tags');
            var $tr_ProjectFile = $('#tr_ProjectFile_' + projectfile_id);
            var tr_class = $tr_ProjectFile.attr('class');
            if ($obj.prop('checked')){
                html +=  tag_name + '<br>';
                have_tags += tag_id + ','
                tr_class += ' tag_' + tag_id;
            } else {
                html = html.replace(tag_name + '<br>', '');
                have_tags = have_tags.replace(tag_id + ',', '');
                tr_class = tr_class.replace('tag_' + tag_id, '');
            }
            $span_tags.html(html);
            $edit_projectfile_tag.attr('have_tags', have_tags);
            $tr_ProjectFile.attr('class', tr_class);

        },
        error: function() {
            // alert('FUCK');
        }
    })
}



$(document).ready(function(){
    $('.select_tag').click(select_tag);
    $('.edit_projectfile_tag').click(edit_projectfile_tag);
    $('.add_or_remove_tag').click(add_or_remove_tag);
    
    $(".uploader").each(function(){
        var $obj = $(this);
        var row_id = $obj.attr("row_id");
        var table_name = $obj.attr("table_name");
        NewFileUploader($obj, row_id, table_name);
    });
});