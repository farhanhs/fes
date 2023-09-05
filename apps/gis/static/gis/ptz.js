$().ready(function() {
    var mgr = new MarkerManager(window.map);
    var imageIcon = new GIcon(G_DEFAULT_ICON, "/media/gis/images/camera_icon.png");
    imageIcon.iconSize = new GSize(30, 30);
    imageIcon.shadow = "";
    imageIcon.iconAnchor = new GPoint(15, 15);
    
    $("#showPTZUI").bind("change", function() {
        if(this.checked) {
            $.ajax({url:"/monitor/matchAJAX/", dataType:"json", type:"POST", data:{submit: "gis_dump"}, success:function(data) {
                var points = data.camera; //[{'lat':25.151058185918, 'lng':121.765977778785, 'url':'/gis/', 'title':'XX射淫機'}];
                
                var batchs = [];
                for(i in points) {
                    batchs.push( (function(point) {
                            var laglng = new GLatLng(point.lat, point.lng);
                            var marker = new GMarker(new GLatLng(point.lat, point.lng), {icon:imageIcon});
                            
                            GEvent.addListener(marker, "click", function(){
                                window.map.openInfoWindowHtml(laglng, "<div>名稱:" + point.title + "</div><div><a href=\"" + point.url + "\">觀看攝影機</a></div>");
                            });
                            return marker;
                        })(points[i])
                    );
                }
                mgr.addMarkers(batchs, 1, 17);
                mgr.refresh();
                }
            });
        } else {
            mgr.clearMarkers();
        }
    })
});