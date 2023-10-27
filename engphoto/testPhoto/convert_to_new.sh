#!/bin/bash
for i in `ls *JPG`;do
    convert -encoding Unicode -fill white -pointsize 48 -font /usr/share/fonts/truetype/arphic/uming.ttc -draw 'text 100,100 "'"`date`"'"' $i new_$i
done
