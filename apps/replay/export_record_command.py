#! /usr/bin/python
#-*- coding: utf8 -*-

# To change this template, choose Tools | Templates
# and open the template in the editor.
"""
#!/bin/bash
# 每次抓 60 秒的 mjpg
# 執行方式：
# $ get_mjpg ${CAMERA_ID}
#
# 登記在 crontab 的方式：
#   * *   * * *   root    /home/hoamon/camera/get_mjpg 4

root=`dirname ${BASH_SOURCE[0]}`
camera_id=$1 #4
username=$2 #fesview
password=$3 #64429429
ip=$4 #211.72.239.7
seconds=$5 #300
type=$6 #BE3204
proxy=$7 #""

if [[ $camera_id != [0-9]* ]];then
    exit
fi

dir=$root/${camera_id}/`date +%Y/%m/%d/%H`
minute=`date +%M`
filename=${dir}/${minute}.mjpg
echo $dir
echo $filename
if ! [ -d $dir ];then
    mkdir -p $dir
fi

case $type in
    "BE3204" )
        if [ $proxy && ${proxy:-1} != "/" ];then
            proxy=${proxy}/
        fi
        `/usr/bin/timeout ${seconds}s /usr/bin/mplayer -dumpstream -dumpfile $filename ${proxy}http://${username}:${password}@${ip}/ipcam/mjpeg.cgi > /dev/null 2>&1 &` ;;
    * )
        exit 1;;
esac
"""

__author__="hoamon"
__date__ ="$2011/10/9 下午 10:09:26$"

if __name__ == "__main__":
    print "Hello World";
