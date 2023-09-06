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
/* randomUUID.js - Version 1.0
*
* Copyright 2008, Robert Kieffer
*
* This software is made available under the terms of the Open Software License
* v3.0 (available here: http://www.opensource.org/licenses/osl-3.0.php )
*
* The latest version of this file can be found at:
* http://www.broofa.com/Tools/randomUUID.js
*
* For more information, or to comment on this, please go to:
* http://www.broofa.com/blog/?p=151
*/

/**
* Create and return a "version 4" RFC-4122 UUID string.
*/
function randomUUID() {
  var s = [], itoh = '0123456789ABCDEF';

  // Make array of random hex digits. The UUID only has 32 digits in it, but we
  // allocate an extra items to make room for the '-'s we'll be inserting.
  for (var i = 0; i <36; i++) s[i] = Math.floor(Math.random()*0x10);

  // Conform to RFC-4122, section 4.4
  s[14] = 4;  // Set 4 high bits of time_high field to version
  s[19] = (s[19] & 0x3) | 0x8;  // Specify 2 high bits of clock sequence

  // Convert to hex chars
  for (var i = 0; i <36; i++) s[i] = itoh[s[i]];

  // Insert '-'s
  s[8] = s[13] = s[18] = s[23] = '-';

  return s.join('');
}


function BE3204Control (ip, login) {
    this.transport = 'transfer.nchu-cm.com'
    this.ip = ip;
    this.login = login;
}
BE3204Control.prototype = {
    init_img: function (url) {
        this.set_quality('2');
        $("#cam_img").attr("src", url);
        return this;
    },
    ptz: function (key) {
        var hash = {
            Stop: '000000',
            UL: '0C0C$',
            Up: '0800$',
            UR: '0A0C$',
            Left: '04$00',
            Right: '02$00',
            DL: '140C$',
            Down: '1000$',
            DR: '120C$',
            ZoomIn: '200000',
            ZoomOut: '400000'
        }
        if (!hash[key]) {return this;}
        var cmd = hash[key];
        var speed = "0C";
        var url = "http://" + this.transport + "/besys?ip=" + this.ip + "&login=" + this.login + "&cmd=dv840output=A000";
        var cmd = cmd.replace(/\$/, speed);
        url += cmd;
        url += "&UUID=" + randomUUID();
        $("#PTZCmdSender").attr("src", url);
        return this;
    },
    run_preset: function (preset_no) {
        var url = "http://" + this.transport + "/besys?ip=" + this.ip + "&login=" + this.login + "&cmd=dv840output=A0000700" + preset_no + "&UUID=" + randomUUID();
        $("#PTZCmdSender").attr("src", url);
        return this;
    },
    set_quality: function(quality) {
        var url = "http://" + this.transport + "/besys?ip=" + this.ip + "&login=" + this.login + "&cmd=quality=" + quality + "&UUID=" + randomUUID();
        $("#PTZCmdSender").attr("src", url);
        return this;
    }
}


function PELCODControl (ip, login) {
    this.transport = 'transfer.nchu-cm.com'
    this.ip = ip;
    this.login = login;
}
PELCODControl.prototype = {
    init_img: function (url) {
        this.set_quality('2');
        $("#cam_img").attr("src", url);
        return this;
    },
    ptz: function (key) {
        var motion = 'continue';
        if (motion == 'continue') {
            var hash = {
                Stop: 'Stop',
                UL: 'UpLeftStart',
                Up: 'UpStart',
                UR: 'UpRightStart',
                Left: 'LeftStart',
                Right: 'RightStart',
                DL: 'DownLeftStart',
                Down: 'DownStart',
                DR: 'DownRightStart',
                ZoomIn: 'ZoomInStart',
                ZoomOut: 'ZoomOutStart'
            }
        } else {
            var hash = {
                Stop: 'Stop',
                UL: 'UpLeft',
                Up: 'Up',
                UR: 'UpRight',
                Left: 'Left',
                Right: 'Right',
                DL: 'DownLeft',
                Down: 'Down',
                DR: 'DownRight',
                ZoomIn: 'ZoomIn',
                ZoomOut: 'ZoomOut'
            }
        }
        if (!hash[key]) {return this;}
        var cmd = hash[key];
        var speed = "0";
        var cmd = 'Dir='+cmd+'&PTZSpeed='+speed;
        var child = document.getElementById('cam_img').contentWindow;
        if (child.pelcod_ptz){
            child.pelcod_ptz(cmd);
        } else {
            var url = "http://" + this.transport + "/gksys?ip=" + this.ip + "&login=" + this.login + "&cmd=" + cmd + "&UUID=" + randomUUID();
            $("#PTZCmdSender").attr("src", url);
        }
        return this;
    },
    run_preset: function (preset_no) {
        var cmd = "Dir=Point"+preset_no;
        var child = document.getElementById('cam_img').contentWindow;
        if (child.pelcod_ptz){
            child.pelcod_ptz(cmd);
        } else {
            var url = "http://" + this.transport + "/gksys?ip=" + this.ip + "&login=" + this.login + "&cmd=" + cmd + "&UUID=" + randomUUID();
            $("#PTZCmdSender").attr("src", url);
        }
        return this;
    },
    set_quality: function (quality) {
        /* should use admin authority, so i decide disable this function */
        var hash = {
            '0': 'high',
            '2': 'middle',
            '4': 'low'
        }
        var url = 'http://fes.fa.gov.tw/monitor/update_quality/?ip='+this.ip+'&type='+hash[quality];
        $("#PTZCmdSender").attr("src", url);
        return this;
    }
}


function CameraControl (machine_no, ip, login) {
    if (!machine_no || !ip || !login) {
        var machine_no = $("#PTZCmdSender").attr("machine_no");
        var ip = $("#PTZCmdSender").attr("ip");
        var login = $("#PTZCmdSender").attr("login");
    } else {
        $("#PTZCmdSender").attr("machine_no", machine_no);
        $("#PTZCmdSender").attr("ip", ip);
        $("#PTZCmdSender").attr("login", login);
    }
    if (machine_no == 'BE3204') {
        this.camera = new BE3204Control(ip, login);
    } else if (machine_no == 'PELCO-D') {
        this.camera = new PELCODControl(ip, login);
    } else {
        if (window.console) {
            console.log('['+machine_no+'] was not defined');
        }
        return false;
    }
}


function getDataByCam () {
    $('.live_monitor_name').removeClass('it_is_living_monitor');
    $.cookie('live_monitor_id', $(this).attr('live_monitor_id'));
    $(this).addClass('it_is_living_monitor');

    var cam_id = $(this).attr('live_monitor_id');
    if(cam_id==""){
        $("#cam_img").attr("src", "/weblive/camimg/init/0");
        $("#select_preset").html("");
        $("#select_quality").html("");
        $("#cam_note").html("");
    }else{
        if($.browser.msie){var browser = "msie"}else{var browser = "cfso"}
        $.ajax({url:"/__ajax__/", type: "POST", data:{module: "weblive.views",
            submit: "getDataByCam", cam_id: cam_id, browser: browser}, dataType:"json", success: function(data){
            if(data["status"]){
                var list = ['left_up_button', 'left_down_button', 'right_up_button', 'right_down_button'];
                for (var i=0; i<list.length; i++) {
                    if (data['machine_no'] == 'PELCO-D') {
                        $('#'+list[i]).hide();
                    } else {
                        $('#'+list[i]).show();
                    }
                }
                var camera = (new CameraControl(data["machine_no"], data['ip'], data['login'])).camera;
                camera.init_img(data["url"]);
                $("#select_preset").html(data["preset"]);
                $("#select_quality").html(data["quality"]);
                $("#preset").change(getSceneByPreset);
                $("#quality").change(setQualityByCmd);

                $("#cam_note").html(data["note"]);

				//INFO adrina test$("#PTZimage").click(testCoord);
            }
        }});
    }
}

function sendPTZCmd(cmd){
    var cam_id = $('a.it_is_living_monitor').attr('live_monitor_id');
    if(cam_id){
        var camera = (new CameraControl()).camera;
        camera.ptz(cmd);

        if(cmd!="000000"){$("#preset").attr("value", "")};
    }
    return false;
}


function getSceneByPreset(){
    var preset_no = Number($("#preset option:selected").val());
    preset_no = preset_no.toString(16);
    if(preset_no.length==1){preset_no = "0" + preset_no}
    var camera = (new CameraControl()).camera;
    camera.run_preset(preset_no);
}

function setQualityByCmd(){
    var quality = $("#quality option:selected").val();
    var camera = (new CameraControl()).camera;
    camera.set_quality(quality);
}

function getPageCoord(element){
	var coord = {x: 0, y: 0};
	while(element){
		coord.x += element.offsetLeft;
		coord.y += element.offsetTop;
		element = element.offsetParent;
	}
	return coord;
}

function ctlptz(event){
	var $obj = this;
	var w = $obj.clientWidth;
	var h = $obj.clientHeight
	var line_L = w/3
	var line_R = w*2/3
	var line_T = h/3
	var line_B = h*2/3

	var target = event.target;
	if(target.offsetLeft==undefined){
		target = target.parentNode;
	}
	var pageCoord = getPageCoord(target);
	var eventCoord = {
		x: window.pageXOffset + event.clientX,
		y: window.pageYOffset + event.clientY
	};
	if (event.offsetX == undefined) {
		var coord = {
			x: eventCoord.x - pageCoord.x,
			y: eventCoord.y - pageCoord.y
		};
	} else {
		var coord = {
			x: event.offsetX,
			y: event.offsetY
		};
	}

	var x = coord.x;
	var y = coord.y;

	if(x<line_L&&y<line_T){
		sendPTZCmd('0C0C$');
	}else if(x>line_L&&x<line_R&&y<line_T){
		sendPTZCmd('0800$');
	}else if(x>line_R&&y<line_T){
		sendPTZCmd('0A0C$');
	}else if(x<line_L&&y>line_T&&y<line_B){
		sendPTZCmd('04$00');
	}else if(x>line_R&&y>line_T&&y<line_B){
		sendPTZCmd('02$00');
	}else if(x<line_L&&y>line_B){
		sendPTZCmd('140C$');
	}else if(x>line_L&&x<line_R&&y>line_B){
		sendPTZCmd('1000$');
	}else if(x>line_R&&y>line_B){
		sendPTZCmd('120C$');
	}
}

function stop(){
	sendPTZCmd('000000');
}

function ctlzoom(objEvent, intDelta){
	if(intDelta>0){
		sendPTZCmd('200000');
	}else if (intDelta<0){
		sendPTZCmd('400000');
	}
	window.setTimeout(stop, 500);
}

function iamalive () {
    var live_monitor_id = $.cookie('live_monitor_id');
    var fes_id = $('a[live_monitor_id='+live_monitor_id+']').attr('fes_id');
    if (live_monitor_id && fes_id) {
        var now = new Date();
        var uuid = $.cookie('uuid');
        var src = '/weblive/iamalive/'+fes_id+'/?uuid='+uuid+'&time='+now.toUTCString();
        $('#iamalive').attr('src', src);
    }

    setTimeout('iamalive();', 10000);
}

$(document).ready(function(){
	$("#ctr_layer").mousedown(ctlptz);
	$("#ctr_layer").mouseup(stop);
	$("#ctr_layer").mouseout(stop);
	$("#ctr_layer").mousewheel(ctlzoom);

    $("#tree").treeview({
		control: "#treecontrol",
		persist: "cookie",
		cookieId: "treeview-red"
	});

    $('.live_monitor_name').click(getDataByCam);
    var live_monitor_id = $.cookie('live_monitor_id');
    if (live_monitor_id) {
        $('a[live_monitor_id='+live_monitor_id+']').click();
    }

    var uuid = $.cookie('uuid');
    if (!uuid) {
        $.cookie('uuid', randomUUID());
    }

    iamalive();
});
