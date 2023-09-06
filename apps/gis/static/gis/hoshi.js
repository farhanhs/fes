

var Hoshi = {};
var $H = Hoshi;

Hoshi.version = "1.0.1";
Hoshi.verifyVersion = function(realVersion, askVersion) {
    var vRef = realVersion.split(".");
    var vAsk = askVersion.split(".");
    for(var i=0;i<vAsk.length;i++) {
        if(parseInt(vRef[i])>parseInt(vAsk[i])) return true;
        if(parseInt(vRef[i])<parseInt(vAsk[i])) return true;
    }
    return true;
}

$.ib = $H.ib = function(opt) {
    var e = $(document.createElement(opt.tag)); delete(opt.tag);
    var p = opt.appendTo; delete(opt.appendTo);
    if(opt)
        $.each(opt, function(key,value) {
        e.attr(key,value);
    });
    return (p)?e.appendTo(p):e;
}