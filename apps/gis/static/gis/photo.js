var GISPhotoENV = {};
GISPhotoENV.UploadingDialogHTML = "<div title=\"上傳照片\">上傳照片中...</div>";
GISPhotoENV.UploadDialogHTML = "<div id=\"uploadPhotoDialog\" title=\"上傳照片\"></div>";
GISPhotoENV.UploadDialogFormHTML = "<div id=\"uploadPhotoForm\" method=\"POST\" action=\"/gis/photoAdd/\" onsubmit=\"return false;\"><div>標題：<input type=\"text\" id=\"imageTitle\" /></div><div><input type=\"file\" id=\"imageFile\" name=\"imageFile\" /></div><div>描述：</div><div style=\"padding-right: 300px\"><textarea id=\"imageDescribe\" rows=\"5\" style=\"width:100%;\"></textarea></div></div>";
GISPhotoENV.UploadErrorMessage = {"image_error":"上傳的照片格式不被伺服器接受。", "user_upload_error":"您沒有權限上傳照片。", "user_delete_error":"您沒有權限刪除照片", "gps_error":"您上傳的照片沒有包含相片的 GPS 座標資訊。"};

var initGISPhoto = function(map) {
    var self = this;
/* Upload Process Part */
    var uploading_dialog = $(GISPhotoENV.UploadingDialogHTML)
        .appendTo($("body"))
        .dialog({autoOpen: false, draggable:false, escape: false});
    var dialog = $(GISPhotoENV.UploadDialogHTML)
        .appendTo($("body"))
        .dialog({autoOpen: false,draggable:false,modal:true,resizable:false,width:700,height:400,buttons:{
            "上傳": function() {
                var url = (self.upload_gis?"/gis/photoAddGMap/":"/gis/photoAddGPS/");
                $.ajaxFileUpload({
                    url:url,
                    secureuri:false,
                    method: "POST",
                    fileElementId:'imageFile',
                    dataType: 'text',
                    data: {title: $("#imageTitle").val(), describe: $("#imageDescribe").val(), lat:$("#imageLat").val(), lng:$("#imageLng").val()},
                    success: function(data, status) {
                        data = eval("data=" + data);
                        if(data.status=="accept") {
                            uploading_dialog.dialog("close");
                            if(self.mgr) {
                                var z = map.getZoom(); // from 1 to 19
                                self.data[z][data.data.id] = data.data;
                                var marker = self.createMarker(data.data);
                                mgr.addMarkers([marker], z, z);
                                mgr.refresh();
                                GEvent.trigger(marker, "click");
                            }
                        } else {
                            uploading_dialog.dialog("close");
                            alert("照片上傳時發生錯誤: " + (GISPhotoENV.UploadErrorMessage[data.status]?GISPhotoENV.UploadErrorMessage[data.status]:data.status));
                        }
                    },
                    error: function(XMLHttpRequest, tp) {
                        uploading_dialog.dialog("close");
                        try {
                            data = eval("data=" + XMLHttpRequest.responseText);
                            if(!(data.status&&data.data&&data.data.id)) throw "."
                            if(data.status=="accept") {
                                uploading_dialog.dialog("close");
                                if(self.mgr) {
                                    var z = map.getZoom(); // from 1 to 19
                                    self.data[z][data.data.id] = data.data;
                                    var marker = self.createMarker(data.data);
                                    mgr.addMarkers([marker], z, z);
                                    mgr.refresh();
                                    GEvent.trigger(marker, "click");
                                }
                            } else {
                                uploading_dialog.dialog("close");
                                alert("照片上傳時發生錯誤: " + (GISPhotoENV.UploadErrorMessage[data.status]?GISPhotoENV.UploadErrorMessage[data.status]:data.status));
                            }
                            alert("已經成功新增相片，但是系統傳回未確認訊息，煩請將訊息回饋給系統工程師: (readyState=" + XMLHttpRequest.readyState + ", status=" + XMLHttpRequest.status + ", statusText=" + XMLHttpRequest.statusText + ")；謝謝。");
                        } catch(e) {
                            alert("照片上傳時發生伺服器錯誤(code=" + XMLHttpRequest.status + "):" + XMLHttpRequest.responseText);
                        }
                    }
                });
                // Close upload form, display uploading dialog.
                dialog.dialog("close");
                uploading_dialog.dialog("open");
            },
            "取消": function() { $(this).dialog("close"); }
            },close:function() {
                $("#imageTitle").val("");
                $("#imageDescribe").val("");
                $("#imageFile").val("");
            }
        });
/* @Upload Process Part */
/* Upload GIS Interface Part */
    var dialog_map = $("<div id=\"image_for_gmap\" style=\"width: 250px;height:250px;float: right;\"></div>").appendTo(dialog);
    var dialog_form = self.form = $(GISPhotoENV.UploadDialogFormHTML).appendTo(dialog);
    var dialog_lat = $("<input type=\"hidden\" id=\"imageLat\" name=\"lat\" />").appendTo(dialog_form);
    var dialog_lng = $("<input type=\"hidden\" id=\"imageLng\" name=\"lng\" />").appendTo(dialog_form);
    $("#upload_image").click(function() {
        dialog_map.show(); self.upload_gis = true;
        $("#plot_image_msg").show(200);
        if(window.uploadingPhoto) return;
        window.uploadingPhoto = true;
        if(!($("#showPhotoUI")[0].checked)) {
            $("#showPhotoUI")[0].checked = true;
            $("#showPhotoUI").trigger("click");
        }
        var uploadImageListenger = GEvent.bind(window.map, "click", this, function(overlay, latlng) {
            dialog_lat.val(latlng.lat());
            dialog_lng.val(latlng.lng());
            if(latlng) {
                dialog.dialog("open");
                if(!self.gmap) {
                    self.gmap = new GMap2(dialog_map[0]);
                    self.gmap_marker = new GMarker(latlng,  {draggable: true});
                }
                self.gmap.setCenter(latlng , 14);
                self.gmap_marker.setLatLng(latlng);
                GEvent.addListener(self.gmap_marker, "dragend", function() {
                    dialog_lat.val(gmap_marker.getLatLng().lat());
                    dialog_lng.val(gmap_marker.getLatLng().lng());
                });

                var overlay = self.gmap.addOverlay(self.gmap_marker);
            }
            $("#imageTitle").focus();
            $("#plot_image_msg").hide(200);
            window.uploadingPhoto = false;
            GEvent.removeListener(uploadImageListenger);
        });
    });
/* @Upload GIS Interface Part */
/* Upload GPS Interface Part */
    $("#upload_image_with_gps").click(function() {
        dialog_map.hide(); self.upload_gis = false;
        dialog.dialog("open");
    });
/* @Upload GIS Interface Part */
/* Plot Photo Icon Part */
    $("#showPhotoUI").bind("click", function() {
        // Step 1: Create Photo Overlay object if not exist.
        if(!self.mgr) {
            self.mgr = new MarkerManager(map);
            self.imageIcon = new GIcon(G_DEFAULT_ICON, "/media/gis/images/image_icon.png");
            self.imageIcon.iconSize = new GSize(50, 50);
            self.imageIcon.shadow = "";
            self.imageIcon.iconAnchor = new GPoint(25, 25); // Offset of image to point
        }

        self.data = {};
        self.boundInfo = {};
        // Step 2A: if enable image function
        if(this.checked&&(!self.photoThread)) {
            self.photoThread = GEvent.addListener(map, "moveend", function() {
                var boundInfo = (self.boundInfo[z])?self.boundInfo[z]:(self.boundInfo[z] = []);
                
                var z = map.getZoom(); // from 1 to 19
                var bounds = map.getBounds();
                var coorStart = bounds.getNorthEast();
                var coorEnd = bounds.getSouthWest();
                
                $.ajax({
                    type:"GET",
                    data:{level: z, right: coorStart.lng(), top: coorStart.lat(), left: coorEnd.lng(), bottom: coorEnd.lat()},
                    url:"/gis/photoSearch/",
                    dataType:"text",
                    success: function(data) {
                        data = eval("data=" + data);
                        var cData = (self.data[z])?self.data[z]:(self.data[z] = {});
                        boundInfo.push({right: coorStart.lng(), top: coorStart.lat(), left: coorEnd.lng(), bottom: coorEnd.lat()});
                        
                        var batch = [];
                        for(photo_id in data) {
                            if(!self.data[z][photo_id]) {
                                cData[photo_id] = data[photo_id];
                                cData[photo_id].id = photo_id;
                                batch.push(self.createMarker(cData[photo_id]));
                            }
                        }
                        mgr.addMarkers(batch, z, z);
                        mgr.refresh();
                    }, error: function(response, error) {
                        alert("ERROR!!(" + error + ")\r\n" + response.responseText);
                    }
                });
            });
            GEvent.trigger(map, "moveend");
        } else {
        // Step 2B: if disable image function
            self.mgr.clearMarkers();
            self.data = {};
            self.boundInfo = {};
            GEvent.removeListener(self.photoThread);
            self.photoThread = undefined;
        }
    });
/* @Plot Photo Icon Part */
/* Photo View Part */
    var photo_view_dialog = $("<div title=\"檢視相片\" id=\"photo_view_dialog\" style=\"position: absolute;display: none;text-align:center; overflow:scroll; width: 90%; height: 90%; top: 5%; left: 5%; z-index: 9999; background-color: #aaa; padding: 10px;\"></div>")
        .appendTo($("body"))
        .bind("show_image", function(dom, photo_id) {
            self.photo_id = photo_id;
            photo_view_img.attr("src", self.data[map.getZoom()][photo_id].src);
            photo_view_dialog.css("display", "block");
        });
    var photo_view_delete = $("<input type=\"button\" value=\"刪除照片\" style=\"float: left\"/>")
        .appendTo(photo_view_dialog)
        .bind("click", function() {
            if(confirm("您確定要刪除這張照片?")) {
                $.ajax({
                    type:"GET",
                    url:"/gis/photoDisable/" + self.photo_id + "/",
                    dataType:"text",
                    success: function(data) {
                        data = eval("data=" + data);
                        if(data.status == "accept") {
                            for(l in self.data) {
                                delete(self.data[l][self.photo_id]);
                            }
                        } else {
                            alert("照片刪除時發生錯誤: " + (GISPhotoENV.UploadErrorMessage[data.status]?GISPhotoENV.UploadErrorMessage[data.status]:data.status));
                        }
                        photo_view_close.trigger("click");
                    }, error: function(response, error) {
                        alert("ERROR!!(" + error + ")\r\n" + response.responseText);
                    }
                });
            }
        });
    var photo_view_close = $("<input type=\"button\" value=\"關閉\" style=\"float: right\"/>")
        .appendTo(photo_view_dialog)
        .bind("click", function() {
            photo_view_dialog.css("display", "none");
        });
    var photo_view_img = $("<img />").appendTo(photo_view_dialog);
/* @Photo View Part */

/* Global Functoin Part */
    self.createMarker = function(image) {
        var laglng = new GLatLng(image.lat, image.lng);
        var marker = new GMarker(new GLatLng(image.lat, image.lng), {icon:self.imageIcon});
        GEvent.addListener(marker, "click", function(){
            map.openInfoWindowHtml(laglng,
                "<div class=\"gis_image\">" + 
                    "<div class=\"title\">標題：" + (image.title?image.title:"(無標題)") + "</div>" + 
                    "<div class=\"port\">" + (image.port_name?image.port_name:"無所屬漁港資料") + "</div>" +
                    "<div class=\"owner\">拍攝時間：" + (image.shoot_time?image.shoot_time:"無拍攝時間") + "</div>" +
                    "<div class=\"owner\">" + (image.time?image.time:"(未知的時間)") + " 由" + (image.owner?image.owner:"未知的使用者") + "上傳</div>" +
                    "<div class=\"describe\">描述：" + (image.describe?image.describe.replace(/\r\n/gi, "<br />"):"(無描述)") + "</div>" + 
                    "<div style=\"width: 320px; height: 240px;\"><img src=\"" + image.thumb + "/\" onclick=\"$('#photo_view_dialog').trigger('show_image', ['" + image.id + "']);\" /></div>" + 
                    "<div class=\"links\"><span onclick=\"$('#photo_view_dialog').trigger('show_image', ['" + image.id + "']);\">檢視圖片</span></div>" +
                "</div>");
        });
        return marker;
    };
/* @Global Functoin Part */
}
