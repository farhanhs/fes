/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
var geo;
var map;
var glatCenterPoint;

function initGoogleMap() {
    glatCenterPoint = new GLatLng(23.694835, 120.882568);
    if (GBrowserIsCompatible()) {
        map = window.map = new GMap2(document.getElementById("map_canvas"));
        map.addControl(new GLargeMapControl());
        map.addControl(new GMapTypeControl());
        map.enableScrollWheelZoom();

        map.clearOverlays()
        map.setCenter(glatCenterPoint ,7);
    }
    else {
        alert("Google Map 啟動失敗。");
    }
}



function gmapAddMarker(P){
    try {
        if((!parseFloat(P.X))||(!parseFloat(P.Y))) {
            return undefined; // Point not exist
        }
        if((P.Y>30||P.Y<15)&&P.X<115||P.X>125) {
            return undefined; // Point is out of range (taiwan)
        }
        var FishIcon = new GIcon(G_DEFAULT_ICON);
        FishIcon.image = "/media/gis/fishicon.png";
        FishIcon.iconSize = new GSize(28, 30);
        markerOptions = { icon:FishIcon };

        var point = new GLatLng(P.Y,P.X);
        var marker = new GMarker(point,markerOptions);
        map.addOverlay(marker);
        var html = gmapSetMessage(P);
        GEvent.addListener(marker,"click",function(){
            map.openInfoWindowHtml(point,html);
        });
        return marker;
    }
    catch(e) {
        return undefined; // err
    }
}

function gmapSetMessage(P){
        var x = parseFloat(P.X);
        var y = parseFloat(P.Y);
        var corString = (x*y!=0)?(
                        "E " + parseInt(x) + "°" + parseInt((x*60)%60) + "'"+ Math.round((x*3600)%60*100)/100 + '", ' + 
                        "N " + parseInt(y) + "°" + parseInt((y*60)%60) + "'"+ Math.round((y*3600)%60*100)/100 + '"'):"沒有座標";
        var html =
            '<img src="/'+P.img_url+'"width="180" height="130" align="top"/>'+
            "<div class=\"port_info_prop\">港名: "+P.name+"</div>" + 
            "<div class=\"port_info_prop\">類型: "+(P.type?(P.type):"")+"</div>" + 
            "<div class=\"port_info_prop\">所在縣市: "+P.place+"</div>" +
            "<div class=\"port_info_prop\">座標: "+corString+"</div>" +
            "<div class=\"port_info_link\"><a onclick=\"window.open('/harbor/port_profile/" + P.id + "/');\">顯示漁港詳細資料</a></div>";
        return html;
    }


var tem = [];
function gmapShowAllMark(R){
//    map.clearOverlay();
    gmapScreenTo(R);
    for (i=0;i< R.length;i=i+1){
        if(R[i].X && R[i].Y != 0){
            gmapAddMarker(R[i]);
            };
        };
    }

/*利用區塊定出方位*/
function gmapScreenTo(R){
    if(R.length != 0){
        var point =[];
        for(i=0;i<R.length; i =i+1){
            if(parseFloat(R[i].X)&&parseFloat(R[i].Y)){
                point[i] = new GLatLng(R[i].Y,R[i].X);
            }
        }
        var polyShape = new  GPolygon(point);
        var bounds =  polyShape.getBounds();
        map.setCenter(bounds.getCenter());
        var level =  map.getBoundsZoomLevel(bounds);
        if(level >= 11){level = 11};
        map.setZoom(level);
    };}


function gmapDeleteMark(marker){
    map.removeOverlay(marker);
}


function gmapMoveToMarker(P){
    if(parseFloat(P.X)&&parseFloat(P.Y)){
        point = new GLatLng(P.Y, P.X);
        var html = gmapSetMessage(P);
        map.setCenter(point,15);
        map.openInfoWindowHtml(point,html,maxWidth=1000);
    }
    else{
        alert("Fail to point to the map!")
    }
}

function getLatlng(){
    initGoogleMap();
    var marker = new GMarker(glatCenterPoint, {draggable: true});
    map.addOverlay(marker);
    GEvent.addListener(marker, "dragend", function() {
        var point = marker.getLatLng();
        map.setCenter(point,11);
        map.openInfoWindowHtml(point,''+point+'');
        $("#temp").value = point.lat().toFixed(6);
	 });
}

function searchAddress(){
        var address = $('#addr').attr("value");
        geo.getLatLng(address,function(point){$("#temp".value = point);
        });
        alert($("#temp".attr("value")));
}