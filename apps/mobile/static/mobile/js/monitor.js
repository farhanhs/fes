function scale_iframe() {
    var w_scale = $('#monitor_screen').width()/640,
        h_scale = $('#monitor_screen').height()/430,
        scale = w_scale < h_scale ? w_scale : h_scale;

    if (scale < 1) {
        $('#cam_img').css({'transform': 'scale(' + scale + ')'});
    }
}


function switch_monitor() {
    $('#cam_img').attr('src', $(this).val());
}


function initial() {
    // scale_iframe();
    $('#monitor_selector').change(switch_monitor);
}


$(document).ready(function(){
    initial();
});
