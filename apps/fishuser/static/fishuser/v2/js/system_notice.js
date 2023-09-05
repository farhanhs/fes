// $(document).ready(function(){
//     if (!$.cookie('ssh_update_notice')){
//         Lobibox.confirm({
//             closeOnEsc: false,
//             iconClass       : 'glyphicon glyphicon-info-sign',
//             title: '<span style="font-size: 2em;">網站憑證更新中。</span>',
//             msg: '目前漁業署網站HTTPS憑證更新申請中，若您的頁面顯示異常，請開啟<a target="_blank" href="https://support.google.com/chromebook/answer/95464?co=GENIE.Platform%3DDesktop&hl=zh-Hant">[Chrome無痕模式]</a>來使用系統。',
//             buttons: {
//                 accept: {
//                     'class': 'lobibox-btn lobibox-btn-yes',
//                     text: '我知道了，不再提醒我',
//                     closeOnClick: true
//                 }
//             },
//             callback: function ($this, type, ev) {
//                 if(type=="accept"){
//                     $.cookie('ssh_update_notice', true, { expires: 7, path: '/'});
//                 }
//             }
//         })
//     }
// })
