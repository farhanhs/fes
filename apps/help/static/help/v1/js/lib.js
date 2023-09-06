
var changeModel = function(){
    var $obj = $(this);
    var now_model = $obj.attr('now_model');
    var model_list = $('#model_list').attr('value').split(',');
    for (var i=0;i<model_list.length;i++){
        $('.'+model_list[i]+'_table').hide();
        $('#thumb_img_'+model_list[i]).attr('class', '')
    }
    $('.'+now_model+'_table').fadeIn();
    $('#thumb_img_'+now_model).attr('class', 'active')
    return false;
}


$(document).ready(function(){
    $('.changeModel').click(changeModel);
});
