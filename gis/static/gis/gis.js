var cp;
$().ready(function() { // This code will be run after page load
    // Make left search panel as tabs (provide by jQuery)/ by Cerberus
    $("#searchPanel").tabs({ disabled: [1] });

    $("#port_dialog").dialog({ autoOpen: false });

    var num_compare = {"more_than":{text:"大於", type: "text"},"between":{text:"介於", type: "between_text"},"less_than":{text:"小於", type: "text"}};
    var options = {};
    $.ajax({async:false, type:"GET", url:"/gis/option_group", dataType:"json", success:function(data) {options = data;}});
    // cp is a user interface for user to create condition search interface (provide by Hoshi)/ by Cerberus
    cp = new Hoshi.ConditionView({window:"#conditionPanel", conditions:{option:options, type: "selector"}});
    // While user click search button, collect search condition's from cp object and use ajax query it
    $("#searchData").click( function(){
        // Get data from Search Condition Interface Object and transfer from a json object to string
        data = cp.get_search_condition();
        toPost = "[";
        for(i in data) {
            toPost += "[";
            for(j in data[i]) toPost += ("\"" + data[i][j].replace(/\\/gi, "\\").replace(/\"/gi, "\\\"") + "\", ");
            toPost = toPost.substr(0, toPost.length - 2);
            toPost += "], ";
        }
        toPost = toPost.substr(0, toPost.length - 2);
        toPost += "]";
        // Use AJAX send query with data {search:"condition string"}
        $.ajax({type:"GET", url:"/gis/search", data:{search:toPost}, dataType:"json", success:function(data) {
            syncSearchResult(data[0], toPost);
            if(data[0].length == 0) {alert("查無漁港!");
            } else {
                $("#searchPanel").tabs('option', 'disabled', []);
                $("#searchPanel").tabs('option', 'selected', 1);
            }
        }, error:function() {
            // If error
            // alert error message
            alert("系統錯誤，請聯絡管理員。");
        }});
    });

    var banner = $(".banner");
    var content = $(".content");
    var footer = $(".footer");
    
    function fixPosition() {
        content.css('height', $(window).height() - banner.height() - footer.height());
    }
    
    $(window).bind("resize", function(){
        fixPosition();
    })
    
    fixPosition();
    
    
    
    // Run google map initial code for GIS (provide by Google map)/ by Dora
    // google init map code must run after layout setting/ by Cerberus
    initGoogleMap();
    initGISPhoto(window.map);
});

var currentPoint;
function syncSearchResult(R, qString) {
    var resultPanel = $("#searchResult");
    if(currentPoint) {
        for(var i=0;i<currentPoint.length;i++){
            try{if(currentPoint[i].ui[0].marker)gmapDeleteMark(currentPoint[i].ui[0].marker);}    // Call to Dora::GoogleMap
            catch(e){alert("嘗試將點位從 Google Map 上移除時發生錯誤")};
            currentPoint[i].ui.remove();
        }
        if(currentPoint.pad) currentPoint.pad.remove();
    }else{
        resultPanel.html("");
    }

//    gmapCenterView();
    currentPoint = R;

    currentPoint.pad = $("<input type=\"button\" value=\"顯示漁港詳細資料\"></input>").appendTo(resultPanel).click(function() {
        window.open('searchlist?search=' + qString);
    });
    
    for(var i=0;i<R.length;i++) {
        R[i].ui = $("<div class=\"data_row\">" +R[i].name + "</div>").appendTo(resultPanel);
        R[i].ui[0].data = R[i];
        try {R[i].ui[0].marker = gmapAddMarker(R[i]);}
        catch(e) {alert("嘗試把漁港位置放到 Google Map 上時發生錯誤");}
        R[i].ui.click(function() {
            try{
                if(this.marker) {
                    gmapMoveToMarker(this.data);
                } else {
                    var dialog = $("#port_dialog");
                    dialog.dialog("option","title",this.data.name);
                    dialog.html("<div class=\"port_info_err\">很抱歉，目前我們沒有這個漁港的座標位置無法顯示在地圖上。</div>"+  gmapSetMessage(this.data));
                    dialog.dialog("open");
                }
            }
            catch(e){alert("嘗試將 Google Map 移動到 " + this.data.name + " 時發生錯誤");}
        });
    }

    try{
        gmapScreenTo(R); // gmapScreenTo, use center default view instead /by Cerberus
    }
    catch(e) {alert("嘗試調整 Google Map 畫面位置時發生錯誤");}
}

function gisPortInformation(Pid) {
}
