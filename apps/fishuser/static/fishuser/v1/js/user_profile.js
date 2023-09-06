//if ($.browser.msie && Number(jQuery.browser.version.substr(0,1)) < 7){
//    window.location = '/media/UpgradeBrowser/index.html';
//}
$(document).ready(function(){
    if ($('#UserProfile').length >= 1) {
        $.getJSON('/u/userprofile/', {}, function(data) {
          var html = '<li title="帳號: '+data['username']+'">'+data['name']+'</li><li>|</li>';
          //TODO 以下網址待教學網站建立後，要修改。
          //html += '<li><a style="font-size: 16px" href="/rcmhelp/?location=' + window.location + '">使用說明</a></li><li>|</li>';
          if (data['name'] == '訪客') {
            html += '<li>訪客</li><li>|</li>';
            html += '<li><a style="font-size: 16px" href="/u/">請登入</a></li>';
          } else {
            html += '<li><a style="font-size: 16px" href="/u/vp/">我的帳戶</a></li><li>|</li>';
            html += '<li><a style="font-size: 16px" href="/help/" target="_blank">線上教學</a></li><li>|</li>';
            html += '<li><a style="font-size: 16px" href="/u/logout/">登出</a></li>';
          }
          $('#UserProfile').empty().append(html).css({
            'list-style-type': 'none',
            'float': 'right',
            'margin-top': '0px',
            'margin-right': '8px'
          }).find('li').css({
            'float': 'left',
            'padding-left': '5px',
            'font-size': '16px'
          });
        });
        $('#MenuBar').css({
            'top': '0px',
            'left': '0px',
            'display': 'block'
        });
    }
});
