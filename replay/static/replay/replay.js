function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            var csrftoken = $('input[name=csrfmiddlewaretoken]:first').val();
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
var actions = {
	backward: function(speed) {
		$f.getPlugin('slowmotion').backward(speed);
	},
	forward: function(speed) {
		$f.getPlugin('slowmotion').forward(speed);
	},
	normal: function() {
		$f.getPlugin('slowmotion').normal();
	}
}

function set_monitor () {
    $('.monitor_name').removeClass('it_is_me');
    $.cookie('monitor_id', $(this).attr('monitor_id'));
    $(this).addClass('it_is_me');
    if($('input#datetime_picker').val()){
        decide_time_range();
    }
}


function get_video_duration () {
    var monitor_id = $.cookie('monitor_id');
    return Number($('a.monitor_name[monitor_id='+monitor_id+']').attr('video_duration'));
}


function change_video () {
    var link = $(this).attr('src');
    $('.download_url').attr('href', link);
    if($('#html5_video').css('display') != 'none'){
        var video = document.getElementsByTagName('video')[0];
        video.src = link;
        video.defaultPlaybackRate = get_video_duration() / 300;
        video.load();
        video.play();
    } else {
        flowplayer("flash_video", "/media/replay/flowplayer/flowplayer-3.2.7.swf", {
//            plugins: {
//                slowmotion: {
//                    url: '/media/replay/flowplayer/flowplayer.slowmotion/flowplayer.slowmotion-3.2.1.swf'
//                },
//                speedIndicator: {
//                    url: '/media/replay/flowplayer/flowplayer.content/flowplayer.content-3.2.0.swf',
//                    bottom: 50,
//                    right: 15,
//                    width: 135,
//                    height: 30,
//                    border: 'none',
//                    style: {
//                        body: {
//                            fontSize: 12,
//                            fontFamily: 'Arial',
//                            textAlign: 'center',
//                            color: '#ffffff'
//                        }
//                    },
//
//                    backgroundColor: 'rgba(20, 20, 20, 0.5)',
//
//                    // we don't want the plugin to be displayed by default,
//                    // only when a speed change occur.
//                    display: 'none'
//                },
//                controls: {
//                    // enable tooltips for the buttons
//                    tooltips: { buttons: true }
//                }
//            },
            playlist: [{url: link}],
            allowfullscreen: false,
            mute: true,
            clip: {
                autoPlay: true,
                autoBuffering: true
            }});
    }
}


function decide_time_range () {
    $('img#loading').show();
    $('#video_in_5_minutes').hide();
    var monitor_id = $.cookie('monitor_id');
    var time_str = $('input#datetime_picker').val();
    if (monitor_id && time_str) {
        $.ajax({url:"/__ajax__/", type: "POST", data: {module: "replay.views",
            submit: "decide_time_range", monitor_id: monitor_id, time_str: time_str},
            dataType:"json", success: function(data) {
            $('img#loading').hide();
            if(!data["status"]) {
                alert(data['message']);
            } else {
                $('#minutes td.link').removeClass('link')
                    .attr('src', '')
                    .click(function(){});
                if (data['links'].length == 0){
                    alert('本時段無紀錄檔');
                    return false;
                }
                $('#video_note').text($('a[monitor_id='+monitor_id+']').text());
                $('#video_in_5_minutes').show();
                for (var i=0; i<data['links'].length; i++){
                    var link = data['links'][i];
                    var res = /([0-9][0-9]).mp4$/.exec(link);
                    if (res && res[1]){
                        $('#minutes td:contains('+res[1]+')')
                            .addClass('link')
                            .attr('src', link)
                            .click(change_video);
                    }
                }
                var link = data['links'][0];
                $('.download_url').attr('href', link);
                if($('#html5_video').css('display') != 'none'){
                    var video = document.getElementsByTagName('video')[0];
                    video.src = link;
                    video.defaultPlaybackRate = get_video_duration() / 300;
                    video.load();
                    video.play();
                } else {
                    flowplayer("flash_video", "/media/replay/flowplayer/flowplayer-3.2.7.swf", {
//                        plugins: {
//                            slowmotion: {
//                                url: '/media/replay/flowplayer/flowplayer.slowmotion/flowplayer.slowmotion-3.2.1.swf'
//                            },
//                            speedIndicator: {
//                                url: '/media/replay/flowplayer/flowplayer.content/flowplayer.content-3.2.0.swf',
//                                bottom: 50,
//                                right: 15,
//                                width: 135,
//                                height: 30,
//                                border: 'none',
//                                style: {
//                                    body: {
//                                        fontSize: 12,
//                                        fontFamily: 'Arial',
//                                        textAlign: 'center',
//                                        color: '#ffffff'
//                                    }
//                                },
//                                backgroundColor: 'rgba(20, 20, 20, 0.5)',
//                                // we don't want the plugin to be displayed by default,
//                                // only when a speed change occur.
//                                display: 'none'
//                            },
//                            controls: {
//                                // enable tooltips for the buttons
//                                tooltips: { buttons: true }
//                            }
//                        },
                        playlist: [{url: link}],
                        allowfullscreen: false,
                        mute: true,
                        clip: {
                            autoPlay: true,
                            autoBuffering: true
                        }});
                }
            }
        }, error: function(jqXHR, textStatus, errorThrown){
            alert(jqXHR.response);
        }});
    } else if (!monitor_id) {
        $('img#loading').hide();
        alert('您未選擇攝影機!');
    } else {
        $('img#loading').hide();
        alert('您未選擇觀看時段!');
    }
}


$(document).ready(function(){
    var now = new Date();
    $('input#datetime_picker').datetimepicker({
        onClose: function () {
            decide_time_range();
        },
        showMinute: false,
        stepMinute: 5,
        dateFormat: 'yy-mm-dd',
        timeFormat: 'hh時',
        minDate: new Date(now-2505600000),
        maxDate: new Date(now-3600000)
    });

    $("#tree").treeview({
		control: "#treecontrol",
		persist: "cookie",
		cookieId: "treeview-red"
	});

    $('.monitor_name').click(set_monitor);
    var monitor_id = $.cookie('monitor_id');
    if (monitor_id) {
        $('a[monitor_id='+monitor_id+']').click();
    }
})
