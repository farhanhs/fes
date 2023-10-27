#舊有的更新error方式為下commands指令updateerrorcontent，但內容寫死在py檔案裡面，這個檔案的功能就是取代原本的方式請往後漁業署用匯出csv的方式重新更新
#所有的缺失表單，減少我們的作業時間跟錯誤機會。後續須繼續更新觸發的方式讓其自動執行，只要把檔案放進去或者主動從主頁匯入2023/10/04sean

import csv
import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from supervise.models import ErrorContent


class Command(BaseCommand):
    help = 'create data of errorcontent from csv file'
    with open("errorcontent.csv",newline='',encoding="utf-8") as csv_file:
        # 讀取 CSV 檔案內容
      rows = csv.DictReader(csv_file)
      # 以迴圈輸出每一列
      for row in rows:
        print( row['no'],row['introduction'])

      for row in rows:
        try:
          ec = ErrorContent.objects.get(no=row["no"])
        except:
          ec = ErrorContent(row=e["no"])
          ec.introduction = row["introduction"]
          ec.save()