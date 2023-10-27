# -*- coding: utf-8 -*-
'''
本文將整理藍眼(BlueEyes)之監控設備(IP Speed Dome Camera, NVR Server)的操作方式並進行說明。

1. IP Speed Dome Camera：
    IP Speed Dome 本身即整合了攝影設備以及網路伺服器，需要固定 IP 線路，透過 IP 可直接連至其本身的伺服器。

    1.1 取得影像：
        為了不被 ActiveX 侷限，影像的顯示形式我們均設定為 AJAX，因此可以透過 MJPEG(Motion Joint Photographic Experts Group) 格式取得攝影機影像。

        1.1.1 一般瀏覽器：
            在一般支援 MJPEG 的瀏覽器，可以透過以下路徑取得影像：
                http://[帳號]:[密碼]@[攝影機IP]/ipcam/mjpeg.cgi

            透過一般的 img tag，就可以在網頁呈現 MJPEG 影像：
                <img src="http://[帳號]:[密碼]@[攝影機IP]/ipcam/mjpeg.cgi">

        1.1.2 IE：
            由於 IE(8.0 under) 並不支援 MJPEG，因此需要透過額外的 ActiveX 去支援。

            首先我們必須先鑲入一個物件，做為呈現影像的管道：
                <object id="PTZimage" classid="CLSID:F47E687B-551F-4043-89B3-F6E3F5DAD01E" codebase="http://[攝影機IP]/VDControl.CAB"></object>

            再來，需要於當頁執行一段 script，啟動上述的影像物件：
                <script type="text/javascript">
                    var startVDC = function(){
                        var obj = document.getElementById("PTZimage");
                        obj.LiveURL='http://[攝影機IP]/ipcam/mjpeg.cgi';
                        obj.MediaUsername='[帳號]';
                        obj.MediaPassword='[密碼]';
                        obj.IsDrawIcon=0;
                        obj.IsZoomEnable=1;
                        obj.IsShowTitle = 0;
                        obj.Start();
                    }
                    setTimeout('startVDC()',1000);
                </script>


    1.2 傳送命令與伺服器回應：
        透過伺服器的 API，我們可以藉由送出 GET 參數來對伺服器進行操作，形式如：
            http://[攝影機IP]/vb.htm?login=[帳號]:[密碼]&dv840output=[命令]

        其中帳號與密碼可於攝影機伺服器開立，並有三種不同權限的設定：
            * root: 管理員權限，除了可操作、設定攝影機，還有帳號的開設權限。
            * operator: 操作人，可控制攝影機與設定參數。
            * viewer: 觀看人，僅能收到攝影機畫面，無法進行任何操作與設定。

        API 所送出的命令同時也會受帳號權限控制，而部分命令會回傳的網頁資訊，我們可以透過其判斷命令狀況：
            * OK: 命令成功執行。
            * NG: 命令參數錯誤、或該命令當下無法執行。
            * NS: 該攝影機或裝置並不支援該命令功能。
            * UA: 帳號權限不足。


    1.3 命令：
        透過命令，我們可以對攝影機進行一些如鏡頭上下左右等的操作，以下則簡列一些基礎指令：

        1.3.1： 攝影機向左，命令為 A00004##00 , ## 為速度參數，為 16 進制字串，範圍是 00~3F，愈大移動速度愈快。

        1.3.2： 攝影機向右，命令為 A00002##00 ，## 為速度參數，為 16 進制字串，範圍是 00~3F，愈大移動速度愈快。

        1.3.3： 攝影機向上，命令為 A0000800## , ## 為速度參數，為 16 進制字串，範圍是 00~3F，愈大移動速度愈快。

        1.3.4： 攝影機向下，命令為 A0001000## , ## 為速度參數，為 16 進制字串，範圍是 00~3F，愈大移動速度愈快。

        1.3.5： 攝影機向左上，命令為　A0000C0C##　｜　Pan Top-Left, ## 為速度參數，為 16 進制字串，範圍是 00~3F，愈大移動速度愈快。

        1.3.6： 攝影機向右上，命令為 A0000A0C##　｜　Pan Top-Right, ## 為速度參數，為 16 進制字串，範圍是 00~3F，愈大移動速度愈快。

        1.3.7： 攝影機向左下，命令為 A000140C##　｜　Pan Bottom-Left, ## 為速度參數，為 16 進制字串，範圍是 00~3F，愈大移動速度愈快。

        1.3.8： 攝影機向右下，命令為 A000120C##　｜　Pan Bottom-Right, ## 為速度參數，為 16 進制字串，範圍是 00~3F，愈大移動速度愈快。

        1.3.9： 停止攝影機動作，命令為 A000000000　｜　Stop, 攝影機的動作是連續的，當下達上下左右等動作後，攝影機會持續執行直到下一個命令，Stop 可令攝影機停止前一個指令的動作。

        1.3.10： 放大，命令為 A000200000。

        1.3.11： 縮小，命令為 A000400000。

        1.3.12： 近焦，命令為 A001000000。

        1.3.13： 遠焦，命令為 A000800000。

        1.3.14： 關閉光圈，命令為 A004000000。

        1.3.15： 設定預設場景，命令為 A0000300## , ## 表示場景代碼，為 16 進制字串，範圍是 00~80。

        1.3.16： 執行預設場景，命令為 A0000700## , ## 表示場景代碼，為 16 進制字串，範圍是 00~80。

        1.3.17： 刪除預設場景，命令為 A0000500## , ## 表示場景代碼，為 16 進制字串，範圍是 00~80。

        更多其他指令，請參考 'Advance Lancam Development Kit <Advance Lancam Development Kit>'_ 文件。


    1.4 執行：
        API 命令是透過網址以 GET 的方式傳送參數給攝影機伺服器，目前我們嘗試了兩種執行方式。
        一是透過主機伺服器執行 HTTP Connection，二是直接在網頁端以讀取路徑方式執行。

        1.4.1 主機端執行：
            1.4.1.1 方法：
                在 python 中，我們會用到的模組為 httplib，在一般情況下，我們可以用下列方式傳送參數：
                    import httplib  #載入模組
                    act = "/vb.htm?login=[帳號]:[密碼]&dv840output=[命令]"  #將命令寫成 GET 參數
                    conn = httplib.HTTPConnection([攝影機IP])   #以 IP 連接攝影機主機
                    R = conn.request("GET", act)    #傳送 GET 參數

                若系統主機伺服器需要透過 PROXY 外連(如 FES 主機)，則可以以下形式傳送：
                    import httplib  #載入模組
                    act = "http://[帳號]:[密碼]@[攝影機IP]/ipcam/mjpeg.cgi"  #完整的連線路徑，包含主機位址與 GET 參數
                    conn = httplib.HTTPConnection([PROXY IP], [PROXY PORT]) #連接 PROXY 服務主機
                    R = conn.request("GET", "http://"+str(IP)+request)  #傳送連線

                我們可以透過 R.read() 的方式來取得攝影機主機對命令的回應，請參考 1.2。

            1.4.1.2 優缺點：
                由於很多命令中都包含帳密資訊，或需要先進行 login 才會接受命令。
                因此在系統主機伺服器端進行命令傳送相對較安全，比較不易被人得知攝影機伺服器的帳密相關資訊。

                但是透過系統主機伺服器發送命令，需要先從使用者端連至系統主機伺服器，再從系統主機伺服器連至攝影機伺服器。
                多了一道聯繫程序，受到線路影響的程度加劇，由其當系統主機伺服器需要透過 PROXY 對外聯繫時，連線延時將明顯提升。

            
        1.4.2 網頁端執行：
            1.4.2.1 方法：
                利用網頁讀取圖片的特性，讓完整的命令連線成為圖片路徑，讓使用者端的瀏覽器去觸發連線。
                下述即一不顯示的圖片標籤，我們可以透過 AJAX 的方式去替換它的 src 屬性，讓瀏覽器去讀取連線。
                    <img src="" style="display: none;">

                透過 AJAX 替換 src 的 img 如下，當瀏覽器去讀取 src 的路徑時，命令就會被送達至攝影機伺服器。
                    <img src="http://[攝影機IP]/vb.htm?login=[帳號]:[密碼]&dv840output=[命令]" style="display: none;">

            1.4.2.2 優缺點：
                直接由使用者端的瀏覽器傳送命令，連線行為較簡單，反應速度也較快。
                且操作過程可以完全不經由系統主機伺服器，系統主機伺服器的負擔也較小。

                但命令中的帳密資訊會呈現在 html 碼中，相對上就比較容易被使用者取得。
                且對於攝影機伺服器回傳的訊息也較難以處理，若遇到意外狀況較難給使用者適當的回應。


2. NVR Server：
    WebNVR 是藍眼(BlueEyes)提供的 NVR(Network Video Recorders) 系統，主要能進行攝影機的管理、錄影以及影像廣播。
'''