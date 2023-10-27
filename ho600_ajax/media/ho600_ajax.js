/**
 * jQuery MD5 hash algorithm function
 *
 * 	<code>
 * 		Calculate the md5 hash of a String
 * 		String $.md5 ( String str )
 * 	</code>
 *
 * Calculates the MD5 hash of str using the 罈 RSA Data Security, Inc. MD5 Message-Digest Algorithm, and returns that hash.
 * MD5 (Message-Digest algorithm 5) is a widely-used cryptographic hash function with a 128-bit hash value. MD5 has been employed in a wide variety of security applications, and is also commonly used to check the integrity of data. The generated hash is also non-reversable. Data cannot be retrieved from the message digest, the digest uniquely identifies the data.
 * MD5 was developed by Professor Ronald L. Rivest in 1994. Its 128 bit (16 byte) message digest makes it a faster implementation than SHA-1.
 * This script is used to process a variable length message into a fixed-length output of 128 bits using the MD5 algorithm. It is fully compatible with UTF-8 encoding. It is very useful when u want to transfer encrypted passwords over the internet. If you plan using UTF-8 encoding in your project don't forget to set the page encoding to UTF-8 (Content-Type meta tag).
 * This function orginally get from the WebToolkit and rewrite for using as the jQuery plugin.
 *
 * Example
 * 	Code
 * 		<code>
 * 			$.md5("I'm Persian.");
 * 		</code>
 * 	Result
 * 		<code>
 * 			"b8c901d0f02223f9761016cfff9d68df"
 * 		</code>
 *
 * @alias Muhammad Hussein Fattahizadeh < muhammad [AT] semnanweb [DOT] com >
 * @link http://www.semnanweb.com/jquery-plugin/md5.html
 * @see http://www.webtoolkit.info/
 * @license http://www.gnu.org/licenses/gpl.html [GNU General Public License]
 * @param {jQuery} {md5:function(string))
 * @return string
 */

(function($){

    var rotateLeft = function(lValue, iShiftBits) {
        return (lValue << iShiftBits) | (lValue >>> (32 - iShiftBits));
    }

    var addUnsigned = function(lX, lY) {
        var lX4, lY4, lX8, lY8, lResult;
        lX8 = (lX & 0x80000000);
        lY8 = (lY & 0x80000000);
        lX4 = (lX & 0x40000000);
        lY4 = (lY & 0x40000000);
        lResult = (lX & 0x3FFFFFFF) + (lY & 0x3FFFFFFF);
        if (lX4 & lY4) return (lResult ^ 0x80000000 ^ lX8 ^ lY8);
        if (lX4 | lY4) {
            if (lResult & 0x40000000) return (lResult ^ 0xC0000000 ^ lX8 ^ lY8);
            else return (lResult ^ 0x40000000 ^ lX8 ^ lY8);
        } else {
            return (lResult ^ lX8 ^ lY8);
        }
    }

    var F = function(x, y, z) {
        return (x & y) | ((~ x) & z);
    }

    var G = function(x, y, z) {
        return (x & z) | (y & (~ z));
    }

    var H = function(x, y, z) {
        return (x ^ y ^ z);
    }

    var I = function(x, y, z) {
        return (y ^ (x | (~ z)));
    }

    var FF = function(a, b, c, d, x, s, ac) {
        a = addUnsigned(a, addUnsigned(addUnsigned(F(b, c, d), x), ac));
        return addUnsigned(rotateLeft(a, s), b);
    };

    var GG = function(a, b, c, d, x, s, ac) {
        a = addUnsigned(a, addUnsigned(addUnsigned(G(b, c, d), x), ac));
        return addUnsigned(rotateLeft(a, s), b);
    };

    var HH = function(a, b, c, d, x, s, ac) {
        a = addUnsigned(a, addUnsigned(addUnsigned(H(b, c, d), x), ac));
        return addUnsigned(rotateLeft(a, s), b);
    };

    var II = function(a, b, c, d, x, s, ac) {
        a = addUnsigned(a, addUnsigned(addUnsigned(I(b, c, d), x), ac));
        return addUnsigned(rotateLeft(a, s), b);
    };

    var convertToWordArray = function(string) {
        var lWordCount;
        var lMessageLength = string.length;
        var lNumberOfWordsTempOne = lMessageLength + 8;
        var lNumberOfWordsTempTwo = (lNumberOfWordsTempOne - (lNumberOfWordsTempOne % 64)) / 64;
        var lNumberOfWords = (lNumberOfWordsTempTwo + 1) * 16;
        var lWordArray = Array(lNumberOfWords - 1);
        var lBytePosition = 0;
        var lByteCount = 0;
        while (lByteCount < lMessageLength) {
            lWordCount = (lByteCount - (lByteCount % 4)) / 4;
            lBytePosition = (lByteCount % 4) * 8;
            lWordArray[lWordCount] = (lWordArray[lWordCount] | (string.charCodeAt(lByteCount) << lBytePosition));
            lByteCount++;
        }
        lWordCount = (lByteCount - (lByteCount % 4)) / 4;
        lBytePosition = (lByteCount % 4) * 8;
        lWordArray[lWordCount] = lWordArray[lWordCount] | (0x80 << lBytePosition);
        lWordArray[lNumberOfWords - 2] = lMessageLength << 3;
        lWordArray[lNumberOfWords - 1] = lMessageLength >>> 29;
        return lWordArray;
    };

    var wordToHex = function(lValue) {
        var WordToHexValue = "", WordToHexValueTemp = "", lByte, lCount;
        for (lCount = 0; lCount <= 3; lCount++) {
            lByte = (lValue >>> (lCount * 8)) & 255;
            WordToHexValueTemp = "0" + lByte.toString(16);
            WordToHexValue = WordToHexValue + WordToHexValueTemp.substr(WordToHexValueTemp.length - 2, 2);
        }
        return WordToHexValue;
    };

    var uTF8Encode = function(string) {
        string = string.replace(/\x0d\x0a/g, "\x0a");
        var output = "";
        for (var n = 0; n < string.length; n++) {
            var c = string.charCodeAt(n);
            if (c < 128) {
                output += String.fromCharCode(c);
            } else if ((c > 127) && (c < 2048)) {
                output += String.fromCharCode((c >> 6) | 192);
                output += String.fromCharCode((c & 63) | 128);
            } else {
                output += String.fromCharCode((c >> 12) | 224);
                output += String.fromCharCode(((c >> 6) & 63) | 128);
                output += String.fromCharCode((c & 63) | 128);
            }
        }
        return output;
    };

    $.extend({
        md5: function(string) {
            var x = Array();
            var k, AA, BB, CC, DD, a, b, c, d;
            var S11=7, S12=12, S13=17, S14=22;
            var S21=5, S22=9 , S23=14, S24=20;
            var S31=4, S32=11, S33=16, S34=23;
            var S41=6, S42=10, S43=15, S44=21;
            string = uTF8Encode(string);
            x = convertToWordArray(string);
            a = 0x67452301; b = 0xEFCDAB89; c = 0x98BADCFE; d = 0x10325476;
            for (k = 0; k < x.length; k += 16) {
                AA = a; BB = b; CC = c; DD = d;
                a = FF(a, b, c, d, x[k+0],  S11, 0xD76AA478);
                d = FF(d, a, b, c, x[k+1],  S12, 0xE8C7B756);
                c = FF(c, d, a, b, x[k+2],  S13, 0x242070DB);
                b = FF(b, c, d, a, x[k+3],  S14, 0xC1BDCEEE);
                a = FF(a, b, c, d, x[k+4],  S11, 0xF57C0FAF);
                d = FF(d, a, b, c, x[k+5],  S12, 0x4787C62A);
                c = FF(c, d, a, b, x[k+6],  S13, 0xA8304613);
                b = FF(b, c, d, a, x[k+7],  S14, 0xFD469501);
                a = FF(a, b, c, d, x[k+8],  S11, 0x698098D8);
                d = FF(d, a, b, c, x[k+9],  S12, 0x8B44F7AF);
                c = FF(c, d, a, b, x[k+10], S13, 0xFFFF5BB1);
                b = FF(b, c, d, a, x[k+11], S14, 0x895CD7BE);
                a = FF(a, b, c, d, x[k+12], S11, 0x6B901122);
                d = FF(d, a, b, c, x[k+13], S12, 0xFD987193);
                c = FF(c, d, a, b, x[k+14], S13, 0xA679438E);
                b = FF(b, c, d, a, x[k+15], S14, 0x49B40821);
                a = GG(a, b, c, d, x[k+1],  S21, 0xF61E2562);
                d = GG(d, a, b, c, x[k+6],  S22, 0xC040B340);
                c = GG(c, d, a, b, x[k+11], S23, 0x265E5A51);
                b = GG(b, c, d, a, x[k+0],  S24, 0xE9B6C7AA);
                a = GG(a, b, c, d, x[k+5],  S21, 0xD62F105D);
                d = GG(d, a, b, c, x[k+10], S22, 0x2441453);
                c = GG(c, d, a, b, x[k+15], S23, 0xD8A1E681);
                b = GG(b, c, d, a, x[k+4],  S24, 0xE7D3FBC8);
                a = GG(a, b, c, d, x[k+9],  S21, 0x21E1CDE6);
                d = GG(d, a, b, c, x[k+14], S22, 0xC33707D6);
                c = GG(c, d, a, b, x[k+3],  S23, 0xF4D50D87);
                b = GG(b, c, d, a, x[k+8],  S24, 0x455A14ED);
                a = GG(a, b, c, d, x[k+13], S21, 0xA9E3E905);
                d = GG(d, a, b, c, x[k+2],  S22, 0xFCEFA3F8);
                c = GG(c, d, a, b, x[k+7],  S23, 0x676F02D9);
                b = GG(b, c, d, a, x[k+12], S24, 0x8D2A4C8A);
                a = HH(a, b, c, d, x[k+5],  S31, 0xFFFA3942);
                d = HH(d, a, b, c, x[k+8],  S32, 0x8771F681);
                c = HH(c, d, a, b, x[k+11], S33, 0x6D9D6122);
                b = HH(b, c, d, a, x[k+14], S34, 0xFDE5380C);
                a = HH(a, b, c, d, x[k+1],  S31, 0xA4BEEA44);
                d = HH(d, a, b, c, x[k+4],  S32, 0x4BDECFA9);
                c = HH(c, d, a, b, x[k+7],  S33, 0xF6BB4B60);
                b = HH(b, c, d, a, x[k+10], S34, 0xBEBFBC70);
                a = HH(a, b, c, d, x[k+13], S31, 0x289B7EC6);
                d = HH(d, a, b, c, x[k+0],  S32, 0xEAA127FA);
                c = HH(c, d, a, b, x[k+3],  S33, 0xD4EF3085);
                b = HH(b, c, d, a, x[k+6],  S34, 0x4881D05);
                a = HH(a, b, c, d, x[k+9],  S31, 0xD9D4D039);
                d = HH(d, a, b, c, x[k+12], S32, 0xE6DB99E5);
                c = HH(c, d, a, b, x[k+15], S33, 0x1FA27CF8);
                b = HH(b, c, d, a, x[k+2],  S34, 0xC4AC5665);
                a = II(a, b, c, d, x[k+0],  S41, 0xF4292244);
                d = II(d, a, b, c, x[k+7],  S42, 0x432AFF97);
                c = II(c, d, a, b, x[k+14], S43, 0xAB9423A7);
                b = II(b, c, d, a, x[k+5],  S44, 0xFC93A039);
                a = II(a, b, c, d, x[k+12], S41, 0x655B59C3);
                d = II(d, a, b, c, x[k+3],  S42, 0x8F0CCC92);
                c = II(c, d, a, b, x[k+10], S43, 0xFFEFF47D);
                b = II(b, c, d, a, x[k+1],  S44, 0x85845DD1);
                a = II(a, b, c, d, x[k+8],  S41, 0x6FA87E4F);
                d = II(d, a, b, c, x[k+15], S42, 0xFE2CE6E0);
                c = II(c, d, a, b, x[k+6],  S43, 0xA3014314);
                b = II(b, c, d, a, x[k+13], S44, 0x4E0811A1);
                a = II(a, b, c, d, x[k+4],  S41, 0xF7537E82);
                d = II(d, a, b, c, x[k+11], S42, 0xBD3AF235);
                c = II(c, d, a, b, x[k+2],  S43, 0x2AD7D2BB);
                b = II(b, c, d, a, x[k+9],  S44, 0xEB86D391);
                a = addUnsigned(a, AA);
                b = addUnsigned(b, BB);
                c = addUnsigned(c, CC);
                d = addUnsigned(d, DD);
            }
            var tempValue = wordToHex(a) + wordToHex(b) + wordToHex(c) + wordToHex(d);
            return tempValue.toLowerCase();
        }
    });
})(jQuery);
/* $.md5 function end */

jQuery.needExist = function(id_tag, name) {
    // input 欄位驗證
    var value = $('#'+id_tag).val();
    if (value == '') {
        alert('未填寫 '+ name + ' 欄位');
        return false;
    } else {
        return value;
    }
}

jQuery.fromDateObjtoString = function (dateObj){
    var year = dateObj.getFullYear();
    var month = dateObj.getMonth()+1;
    if (month <= 9){
        month = '0' + month;
    }
    var date = dateObj.getDate();
    if (date <= 9){
        date = '0' + date;
    }
    return year + '-' + month + '-' + date;
}

jQuery.fromStringtoDateObj = function (date){
    var array = date.split('-');
    var d = new Date(array[0], Number(array[1])-1, array[2]);
    return d;
}

jQuery.needTheSame = function(id_tag1, id_tag2, message) {
    // 驗證input 欄位是否相同
    var value1 = $('#'+id_tag1).val();
    var value2 = $('#'+id_tag2).val();
    if (value1 != value2){
        alert(message);
        return false;
    } else {
        return value1;
    }
}

jQuery.checkDateFormat = function(id_tag, message){
    var value = $('#'+id_tag).val();
    var match = /^((19|20)[0-9][0-9])[-\/]([012][0-9])[-\/]([0-3][0-9])$/.exec(value);
    if (match){
        var d = new Date();
        d.setFullYear(match[1]);
        d.setMonth(Number(match[3])-1);
        d.setDate(match[4]);
        d.setHours(0);
        d.setMinutes(0);
        d.setSeconds(0);
        return d;
    } else {
        alert(message);
        return false;
    }
}

jQuery.checkPositiveIntegerFormat = function(id_tag, message){
    var value = $('#'+id_tag).val();
    var match = /^[0-9]+$/.exec(value);
    if (match){
        return value;
    } else {
        alert(message);
        return false;
    }
}

jQuery.checkPasswordFormat = function(id_tag, message, digit_limit) {
    // input 欄位驗證
    var value = $('#'+id_tag).val();
    var digit_limit = digit_limit ? digit_limit : 6;
    if (value.length < digit_limit) {
        alert('密碼長度少於 '+digit_limit+' 個');
        return false;
    } else if (/^\d+$/.exec(value)) {
        alert('不可以全部設數字');
        return false;
    } else if (/^[a-zA-Z]+$/.exec(value)) {
        alert('不可以全部設英文字母');
        return false;
    } else if (/^[a-zA-Z0-9`~\!@#\$%\^\&\*)(\-_\+=\]\[}{\\|;:'",><\.\?\/]+$/.exec(value)) {
        return value;
    } else {
        alert(message);
        return false;
    }
}

jQuery.md5Password = function(username, password) {
    return $.md5(username+password.substr(password.length-2, 2)+password+password.substr(1, 2));
}

jQuery.checkUsernameFormat = function(id_tag, message) {
    // input 欄位驗證
    var value = $('#'+id_tag).val();
    if (/^\d{8,10}$/.exec(value)) {
        return value;
    } else if (/^\d{9,10}#\d+$/.exec(value)) {
        return value;
    } else {
        alert(message);
        return false;
    }
}

var TAIWAN_ID_ORDER = 'ABCDEFGHJKLMNPQRSTUVXYWZIO';
jQuery.checkTaiwanIDFormat = function(id_tag, message) {
    // input 欄位驗證
    var value = $('#'+id_tag).val();
    value = value.replace(/\ /g, '').toUpperCase();
    if (/^[A-Z][12][0-9]{8}$/.exec(value)) {
        var index = 0;
        for(var i=0; i<TAIWAN_ID_ORDER.length; i++){
            if (TAIWAN_ID_ORDER[i] == value[0]){
                var index = String(i + 10);
                break;
            }
        }
        if (index == 0) {
            alert('身份證的英文不正確');
            return false;
        }
        if((Number(index[0]) + 9*Number(index[1]) + 8*Number(value[1]) + 7*Number(value[2])
            + 6*Number(value[3]) + 5*Number(value[4])
            + 4*Number(value[5]) + 3*Number(value[6]) + 2*Number(value[7])
            + 1*Number(value[8]) + Number(value[9])) % 10 == 0){
            return value;
        } else {
            alert('身份證號不合格');
            return false;
        }
    } else {
        alert(message);
        return false;
    }
}

jQuery.checkEmailFormat = function(id_tag, message) {
    // input 欄位驗證
    var value = $('#'+id_tag).val();
    value = value.replace(/\ /gi, '');
    if (/^[a-z0-9][-a-z0-9_\.\+]*@([a-z0-9-]+\.)+[a-z]{2,4}$/i.exec(value)) {
        return value.toLowerCase();
    } else {
        alert(message);
        return false;
    }
}

jQuery.checkCompanyNoFormat = function(id) {
    var value = $('#'+id).val();
    function valid(n) {
       return (n%10 == 0)?true:false;
    }
    function cal(n) {
       var sum=0;
       while (n!=0) {
          sum += (n % 10);
          n = (n - n%10) / 10;  // 取整數
         }
       return sum;
    }
    function nochk(novalue) {
       var tmp = new String("12121241");
       var sum = 0;
       for (i=0; i< 8; i++) {
         s1 = parseInt(novalue.substr(i,1));
         s2 = parseInt(tmp.substr(i,1));
         sum += cal(s1*s2);
       }
       if (!valid(sum)) {
          if (novalue.substr(6,1)=="7") return(valid(sum+1));
       }
       return(valid(sum));
    }
    var no = /^[0-9]{8}$/.exec(value);
    if (no == null){
        alert('統一編號須為 8 碼數字，您所填寫的則是「'+value+'」');
        return false;
    } else if (nochk(value) == false) {
        alert(no + ' 此為不合法的統一編號，請確認!');
        return false;
    }
    return value
}

$(document).ready(function(){
    $('.no_js_message').hide();
    $('.show_with_js').show();

    $('img#loading').ajaxStop(function(){
        var $img = $(this);
        if($img.attr('status') != 'disable'){
            $('body').css('opacity', 1);
            $img.hide();
        }
    });
    $('img#loading').ajaxStart(function(){
        var $img = $(this);
        if($img.attr('status') != 'disable'){
            $('body').css('opacity', 0.25);
            $img.css('z-index', 10000).show();
        }
    });
});

function writeI18nMessage () {
    document.write(gettext('This is a message from javascript'));
}

$(document).ajaxError(function(envent, response, settings){
    var response_status = String(response['status']);
    if ($('#id_ajaxErrorDialog').length == 0){
        $('img#loading').after($('<div id="id_ajaxErrorDialog"></div>'));
    }
    var $ajaxErrorDialog = $('#id_ajaxErrorDialog');
    if (response_status == '0'){
        var title = '連線錯誤訊息';
        var message = '<p>十分抱歉，目前無法連線。可能是本網站發生問題，也有可能是您個人使用的網路出現問題，請稍候測試。</p><p>並請注意!! 您在本網頁所作的更改有可能未完整傳至主機，請待下次網路連線正常時，再次檢查資料的正確性。</p><p>可連上<a href="http://www.google.com/" target="_blank">Google</a>，檢測您的網路連線。<br>請稍候或隔天測試</p>';
    } else {
        var title = '執行錯誤訊息';
        if (response_status == '500') {
            var code = response['responseText'];
            var link = '<a href="/ho600_bugrecord/bugpage/'+code+'/" target="_blank">'+code+'</a>';;
            var message = '網頁程式出現問題[錯誤碼: '+link+']<br>已將錯誤回報給工程師了<br>請稍候或隔天測試';
        } else if (response_status == '404') {
            var list = response['responseText'].split('<>');
            var path = list[0];
            var code = list[1];
            var message = '無法連結 ' + path + ' [錯誤碼: '+code+']<br>已將錯誤回報給工程師了<br>請稍候或隔天測試';
        } else if (response_status == '403') {
            var code = response['responseText'];
            var message = '系統拒絕您的請求，理由為<span class="notice">[ '+code+' ]</span>';
        } else if (response_status == '200') {
            var message = response['responseText'];
        } else {
            var code = response['responseText'];
            var message = '網頁程式出現問題[狀態碼: '+response_status+','+code+']<br>已將錯誤回報給工程師了<br>請稍候或隔天測試';
        }
    }
    if($.browser.mozilla){
        if($('img#loading').attr('status') != 'disable'){
            $('body').css('opacity', 1);
            $('img#loading').hide();
        }
    }
    $ajaxErrorDialog.html(message).dialog({
        title: title,
        modal: true,
        overlay: {opacity: 0.8, background: "black"},
        buttons: {
            '關閉本視窗': function(){
                $ajaxErrorDialog.dialog('close');
            }
        },
        width: 500
    });
});
