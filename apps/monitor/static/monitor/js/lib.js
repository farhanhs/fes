var ip_check=/^((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))*$/;

var getFishingPortOptions = function(){
    var $obj = $(this);
    if($obj.val()){
        var place = $obj.val();
        $.post("/monitor/matchAJAX/", {"submit": "getFishingPort", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "place": place, "state": "All"}, function(json){
            if (json["status"]){
                $("#FishingPort").html(json["contents"]);
                $("#port").change(relocateMap);
                relocateMap();
            }
        }, "json")
    } else {
        var contents = "";
        contents += '<select id="port" class="form-control">';
        contents += '<option value="">請選擇縣市</option>';
        contents += '</select>';
        $("#FishingPort").html(contents);
        $("#coord").html("請選擇漁港後移動標記");
        $("#lat").val("");
        $("#lng").val("");
        initialize();
    }
    checkComplete();
    return false;
}

var relocateMap = function(){
    var port = $("#port option:selected");
    if(port.val()==""){
        $("#coord").html("請選擇漁港後移動標記");
        $("#lat").val("");
        $("#lng").val("");
        initialize();
    }else{
        var lat = port.attr("lat");
        var lng = port.attr("lng");
        resetCoordLocation(lat, lng);
        $("#coord").html("請選擇漁港後移動標記");
        $("#lat").val("");
        $("#lng").val("");
    }
    checkComplete();
    return false;
}

var initializeAddPage = function(){
    $("#cam_submit").attr("disabled", true);
    $("#name").val("");
    $("#note").val("");
    $("#IP").val("");
    $("#account").val("");
    $("#place").val("");
}

var initializeEditPage = function(){
    $("#selected_cam").val("");
    $("#name").val("");
    $("#machine_no").val("");
    $("#note").val("");
    $("#IP").val("");
    $("#video_url").val("");
    $("#place_for_edit").val("");
    $("#coord").html("請選擇攝影機");
}

var updateMarkerPosition = function(Position){
    var lat = Position.lat();
    var lng = Position.lng();
    $("#coord").html(String(Position));
    $("#lat").val(lat);
    $("#lng").val(lng);
    checkComplete();
}

var checkCoord = function(){
    var lat = $("#lat").val();
    var lng = $("#lng").val();
    if(lat!="" && lng!=""){
        $("#check_coord").attr("src", "/media/monitor/image/check.png");
        return true;
    }else{
        $("#check_coord").attr("src", "/media/monitor/image/uncheck.png");
        return false;
    }
}

var checkName = function(){
    var name = $("#name").val();
    if(name!=""){
        $("#check_name").attr("src", "/media/monitor/image/check.png");
        return true;
    }else{
        $("#check_name").attr("src", "/media/monitor/image/uncheck.png");
        return false;
    }
}

var checkIP = function(){
    var IP = $("#IP").val();
    if(ip_check.test(IP) && IP!=""){
        $("#check_IP").attr("src", "/media/monitor/image/check.png");
        return true;
    }else{
        $("#check_IP").attr("src", "/media/monitor/image/uncheck.png");
        return false;
    }
}

var checkAccount = function(){
    var account = $("#account").val();
    if(account!=""){
        $("#check_account").attr("src", "/media/monitor/image/check.png");
        return true;
    }else{
        $("#check_account").attr("src", "/media/monitor/image/uncheck.png");
        return false;
    }
}

var checkPasswd = function(){
    var passwd = $("#passwd").val()
    var passwd_check = $("#passwd_check").val()
    if(passwd==passwd_check && passwd!=""){
        $("#check_passwd").attr("src", "/media/monitor/image/check.png");
        return true;
    }else{
        $("#check_passwd").attr("src", "/media/monitor/image/uncheck.png");
        return false;
    }
}

var checkComplete = function(){
    var cam_need = $(".cam_need");
    var complete = true;
    for(i=0;i<cam_need.length;i++){
        if($("#"+cam_need[i].id).val()==""){
            complete = false;
        }
    }
    checkCoord();
    checkName();
    if(!checkIP()){
        complete = false;
    }
    checkAccount();
    if(!checkPasswd()){
        complete = false;
    }
    var video_url = $("#video_url").val();
    if (!/^https?:\/\/[^\/]+\/.*$/.test(video_url)){
        $("#check_video_url").attr("src", "/media/monitor/image/uncheck.png");
        complete = false;
    } else {
        $("#check_video_url").attr("src", "/media/monitor/image/check.png");
    }
    if(complete){
        $("#cam_submit").attr("disabled", false);
    }else{
        $("#cam_submit").attr("disabled", true);
    }
}

var addCam = function(){
    var place = $("#place").val();
    var port = $("#port").val();
    var lat = $("#lat").val();
    var lng = $("#lng").val();
    var name = $("#name").val();
    var machine_no = $("#machine_no").val();
    var location = $("#note").val();
    var IP = $("#IP").val();
    var account = $("#account").val();
    var passwd = $("#passwd").val();
    var video_url = $("#video_url").val();
    $.post("/monitor/matchAJAX/", {submit: "addCam", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, place: place, port: port,
        lat: lat, lng: lng, name: name, machine_no: machine_no,
        location: location, IP: IP, account: account, passwd: passwd,
        video_url: video_url}, function(json){
        if (json["status"]){
            alert(json["msg"]);
            window.location.reload();
        }else{
            alert(json["msg"]);
        }
    }, "json")
}

var makeCamMapBlock = function(){
    var block = $("#ViewCamBlock");
    var area = block.attr("area");
    $.post("/monitor/matchAJAX/", {"submit": "makeCamMapBlock", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "area": area}, function(json){
        if (json["status"]){
            if(json["cam"]){
                var Cam = {
                  map: null,
                  infoWindow: null
                };
                Cam.closeInfoWindow = function() {
                    Cam.infoWindow.close();
                };
                Cam.openInfoWindow = function(marker){
                    var content = "<table>";
                    content += "<tr><td>名稱：</td>";
                    content += "<td>" + marker.name + "</td><td></td></tr>";
                    content += "<tr><td>說明：</td>";
                    content += "<td>" + marker.location + "</td><td></td></tr>";
                    content += '<tr><td></td><td></td><td><button id="' + marker.id + '" class="makeCamImgBlock">觀看畫面</button></td></tr>';
                    content += "</table>";
                    Cam.infoWindow.close();
                    Cam.infoWindow = new google.maps.InfoWindow({
                        content: content
                    });
                    Cam.infoWindow.open(Cam.map,marker);
                    $(".makeCamImgBlock").click(makeCamImgBlock);
                };
                var newLatlng = new google.maps.LatLng(json["lat"], json["lng"]);
                Cam.map = new google.maps.Map(document.getElementById('map_canvas'), {
                    zoom: 16,
                    center: newLatlng,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                });
                Cam.infoWindow = new google.maps.InfoWindow();
                google.maps.event.addListener(Cam.map, 'click', Cam.closeInfoWindow);
                for(i=0;i<json["monitor_list"].length;i++){
                    var MonitorLatlng = new google.maps.LatLng(json["monitor_list"][i].lat, json["monitor_list"][i].lng);
                    marker = new google.maps.Marker({
                        position: MonitorLatlng,
                        title: json["monitor_list"][i].name,
                        map: Cam.map,
                        icon: "/media/monitor/image/CameraIcon.png",
                        id: json["monitor_list"][i].id,
                        name: json["monitor_list"][i].name,
                        location: json["monitor_list"][i].location,
                        video_url: json["monitor_list"][i].video_url
                    });
                    google.maps.event.addListener(marker, 'click', function() {
                        Cam.openInfoWindow(this);
                    });
                 }
            }else{
                $("#no_cams").show();
                $("#map_canvas").hide();
            }
        }
    }, "json")
}

var __sto = setTimeout;
window.setTimeout = function(callback,timeout,param){
    var args = Array.prototype.slice.call(arguments,2);
    var _cb = function(){
        callback.apply(null,args);
    }
    __sto(_cb,timeout);
}

var makeCamImgBlock = function(){
    var $obj = $(this);
    var cam = $obj.attr("id");
    if($.browser.msie){
        var browser = "IE";
    }else{
        var browser = "other"; 
    }
    $.post("/monitor/matchAJAX/", {"submit": "makeCamImgBlock", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "cam": cam, "browser": browser}, function(html){
        $.post("/monitor/matchAJAX/", {"submit": "getLogin", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "cam": cam}, function(json){
            if(json["status"]){
            }else{
                alert("無法登入攝影機，請稍候再試！");
                return false;
            }
        }, "json");
        window.setTimeout(reBolck, 2000, html);
    }, "html")
}

var reBolck = function(html){
    $("#map_canvas").hide();
    $("#img_canvas").html(html);
    $("#preset").change(runPreset);
    $("#preset").click(runPreset);
}

var returnToCamMap = function(){
    location.reload();
}

var sendPTZCmd = function(cmd){
    var speed = "0C"
    var cam = $("#film").attr("cam");
    $.post("/monitor/matchAJAX/", {"submit": "runCamCmd", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "cam": cam, "cmd": cmd, "speed": speed}, function(json){}, "json");
}

var runPreset = function(){
    var cam = $("#film").attr("cam");
    var preset = $("#preset option:selected");
    if(preset.val()!=""){
        $.post("/monitor/matchAJAX/", {"submit": "runPreset", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "cam": cam, "preset": preset.val()}, function(json){
            if(!json["status"]){
                alert("與攝影機聯繫錯誤，請稍候再試!");
            }
        }, "json");
        $("#selected_preser_name").attr("value", preset.html().replace(/^[0-9]+\.\s+/, ''));
    }else{
        $("#selected_preser_name").val("")
    }
}

var ctlSetCamPreset = function(cmd){
    var $obj = $(this);
    var sub = $("#"+cmd+"CamPreset");
    if(sub.attr("state")=="hide"){
        sub.fadeIn();
        sub.attr("state", "show");
    }else{
        sub.fadeOut();
        sub.attr("state", "hide");
    }
}

var setCamPreset = function(cmd){
    var cam = $("#film").attr("cam");
    if(cmd=="Add"){
        var name = $("#new_preser_name").val();
        if(name==""){
            alert("請輸入域設場景名稱!");
            return false;
        }
        $.post("/monitor/matchAJAX/", {"submit": "cCamPreset", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "cam": cam, "name": name}, function(json){
            if(json["status"]){
                $("#PresetBolck").html(json["content"]);
                $("#preset").change(runPreset);
            }else{
                alert("無法與攝影機連繫，請稍候再試!");
            }
        }, "json");
    }else if(cmd=="Edit"){
        var preset = $("#preset option:selected");
        if(preset.val()==""){
            alert("未選擇域設場景!");
            return false;
        }else{
            var message='將會更新此場景的名稱並更新鏡頭設定，確定重設?'
            if (confirm(message)){
                var name = $("#selected_preser_name").val();
                if(name==""){
                    alert("請輸入域設場景名稱!");
                    return false;
                }
                $.post("/monitor/matchAJAX/", {"submit": "uCamPreset", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "cam": cam, "name": name, "preset": preset.val()}, function(json){
                    if(json["status"]){
                        $("#PresetBolck").html(json["content"]);
                        $("#preset").change(runPreset);
                    }else{
                        alert("無法與攝影機連繫，請稍候再試!");
                    }
                }, "json");
                $dialog.dialog('close');
            }else{
                return false;
            }
        }
    }else if(cmd=="Remove"){
        var preset = $("#preset option:selected").val();
        if(preset==""){
            alert("未選擇域設場景!");
            return false;
        }else{
            var message='確定刪除"'+$("#preset option:selected").html()+'"場景?'
            if (confirm(message)){
                $.post("/monitor/matchAJAX/", {"submit": "dCamPreset", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "cam": cam, "preset": preset}, function(json){
                    if(json["status"]){
                        $("#PresetBolck").html(json["content"]);
                        $("#preset").change(runPreset);
                        ("#selected_preser_name").val("")
                        alert("刪除成功!");
                    }else{
                        alert("無法與攝影機連繫，請稍候再試!");
                    }
                }, "json");
            }else{
                return false;
            }
        }
    }
}


var makeCamEditBlock = function(){
    $.post("/monitor/matchAJAX/", {submit: "makeCamEditBlock", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN}, function(html){
        $("#EditCamBlock").html(html);
        $("#place_for_edit").change(getFishingPortForEdit);
    }, "html")
}

var getFishingPortForEdit = function(){
    var $obj = $(this);
    if($obj.val()){
        var place = $obj.val();
        $.post("/monitor/matchAJAX/", {"submit": "getFishingPort", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "place": place, "state": "Edit"}, function(json){
            if (json["status"]){
                $("#FishingPort_for_edit").html(json["contents"]);
                $("#port_for_edit").change(focusMap);
                focusMap();
            }
        }, "json")
    } else {
        var contents = ""
        contents += '<select id="port" class="form-control">'
        contents += '<option value="">請選擇縣市</option>'
        contents += '</select>'
        $("#FishingPort_for_edit").html(contents)
        initialize();
    }
    return false;
}

var focusMap = function(){
    var port = $("#port_for_edit option:selected");
    if(port.val()==""){
        initialize();
    }else{
        
        $.post("/monitor/matchAJAX/", {"submit": "makeCamMapBlock", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "area": port.val()}, function(json){
            if(json["status"]){
                resetMap(json["lat"], json["lng"], json["monitor_list"]);
            }else{
                //pass;
            }
            
        }, "json")
    }
    return false;
}

var renewSelectedCamCoord = function(marker){
    var lat = marker.position.lat().toString();
    var lng = marker.position.lng().toString();
    $("#coord").html("("+lat+", "+lng+")");
}


var editSelectedCam = function(marker){
    var id = marker.id;
    var name = marker.name;
    var location = marker.location;
    var machine_no = marker.machine_no;
    var video_url = marker.video_url;
    var ip = marker.ip;
    var lat = marker.position.lat().toString();
    var lng = marker.position.lng().toString();
    $("#coord").html("("+lat+", "+lng+")");
    $("#lat").val(lat);
    $("#lng").val(lng);
    $("#selected_cam").val(id);
    $("#name").val(name);
    $("#machine_no").val(machine_no);
    $("#note").val(location);
    $("#IP").val(ip);
    $("#video_url").val(video_url);
}

var updateSelectedCam = function(){
    var cam = $("#selected_cam").val();
    if(cam==""){
        alert("請選擇攝影機！");
    }else{
        var name = $("#name").val();
        var machine_no = $("#machine_no").val();
        var note = $("#note").val();
        var ip = $("#IP").val();
        var lat = $("#lat").val();
        var lng = $("#lng").val();
        var video_url = $("#video_url").val();
        $.post("/monitor/matchAJAX/", {submit: "uCamInfo", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, cam: cam,
            name: name, machine_no: machine_no, lat: lat, lng: lng,
            ip: ip, location: note, video_url: video_url}, function(json){
            if (json["status"]){
                alert("修改成功！");
                location.reload();
            }
        }, "json")
    }
}

var removeSelectedCam = function(){
    var cam = $("#selected_cam").val();
    if(cam==""){
        alert("請選擇攝影機！");
    }else{
        var name = $("#name").val();
        var ip = $("#IP").val();
        var message = "您確定要刪除"+name+"("+ip+")嗎?";
        if (confirm(message)){
            $.post("/monitor/matchAJAX/", {"submit": "dCam", "csrfmiddlewaretoken": CSRFMIDDLEWARETOKEN, "cam": cam}, function(json){
                if (json["status"]){
                    alert("刪除成功！");
                    location.reload();
                }
            }, "json")
        }
    }
}

$(document).ready(function(){
    $("#place").change(getFishingPortOptions);
    $("#port").change(relocateMap);
    $("#passwd_check").blur(checkPasswd);
    $("#passwd").blur(checkPasswd);
    $(".cam_need").change(checkComplete);
    $("#cam_submit").click(addCam);
    $(".makeCamImgBlock").click(makeCamImgBlock);
    $("#returnToCamMap").click(returnToCamMap);
    $("#preset").change(runPreset);
    $("#place_for_edit").change(getFishingPortForEdit);
    $("#port_for_edit").change(focusMap);
    $("#cam_update").click(updateSelectedCam);
    $("#cam_remove").click(removeSelectedCam);


//<--- For activate cammapblock, which can be plug-in by use {% include 'monitor/cammapblock.html' %}
    if($("#ViewCamBlock").attr("area")){
        makeCamMapBlock();
    };

//<--- For activate cameditblock, which can be plug-in by use {% include 'monitor/cameditblock.html' %}
    if($("#EditCamBlock").attr("state")){
        makeCamEditBlock();
    };

    
});
