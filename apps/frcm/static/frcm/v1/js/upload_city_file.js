var setUploadCityFileForm = function(id) {
    var $obj = $('#'+id);
    if($obj.attr('status') == 'setuped') { return false }

    $obj.attr('METHOD', 'POST').attr('action', '/harbor/cityfiles/js/')
    .attr('enctype', 'multipart/form-data').attr('status', 'setuped');
    var html = '';
    html += '<ul style="list-style: none">';
    html += '    <li>歸檔縣市： <select name="place_id" class="rCitysSelect"><option value="">請選擇</option></select></li>';
    html += '    <li>詳細位置： <input type="text" name="location" /></li>';
    html += '    <li>檔案名稱： <input type="text" name="name" /></li>';
    html += '    <li>檔案備註： </li>';
    html += '    <li>　　　　　 <textarea name="memo"></textarea></li>';
    html += '    <li>Ｘ座標　： <input type="text" name="lng" /></li>';
    html += '    <li>Ｙ座標　： <input type="text" name="lat" /></li>';
    html += '    <li>選擇檔案： <input type="file" name="file" /></li>';
    html += '    <li><input type="submit" class="uploadCityFileWithJS" value="確定上傳" /></li>';
    html += '    <li><input type="hidden" name="redirect" /></li>';
    html += '</ul>';
    $obj.append($(html));
    $('.uploadCityFileWithJS').click(uploadCityFileWithJS);
    $('.rCitysSelect', $obj).mouseover(rCitysSelect);
}

var rCitysSelect = function () {
    var $obj = $(this);
    if ($('option', $obj).length > 1) { return false }
    $.post('/general/ajax/', {submit: 'rCitysSelect'}, function(json) {
        if (json['status'] == false) {
            alert(json['message']);
        } else {
            var option = '';
            for (var i=0; i<json['citys'].length; i++) {
                var city = json['citys'][i];
                option += '<option value="'+city['id']+'">'+city['name']+'</option>';
            }
            $obj.append($(option));
        }
    }, "json");
}

var uploadCityFileWithJS = function () {
    var $form = $(this).parent().parent().parent();
    var city = $('select', $form).val();
    if(!city){
        alert('歸檔縣市必選');
        return false;
    }
    var file = $('input[name=file]', $form).val();
    if(!file){
        alert('未選擇檔案');
        return false;
    }
    $('input[name=redirect]', $form).val(window.location.href);
}

$(document).ready(function(){
    $('.upload_city_file').each(function() {
        setUploadCityFileForm($(this).attr('id'));
    });
});
