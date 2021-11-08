# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 22:58:34 2021

@author: StevenYang
"""

from datetime import date
from dateutil.relativedelta import relativedelta
import os
import requests
import pandas as pd
from pandas.tseries.offsets import BDay
import time
import random
import plotly.graph_objects as go

"""
datetype = 'm'：產生各股每月檔案路徑['./2330_20210601.csv', './2330_20210501.csv', './2331_20210601.csv']
datetype = 'd'：產生每日(排除假日)檔案路徑['./20210630_ALL.csv', './20210629_ALL.csv', './20210628_ALL.csv']
"""
def CreateFilePath(periods, datetype):
    if datetype == 'm':
        filepath = ['./'+(date.today() + relativedelta(months=-idx)).strftime('%Y%m01')+'_ALL.csv' for idx in range(periods)]    

    if datetype == 'd':
        filepath = ['./'+(date.today() - BDay(idx)).strftime('%Y%m%d')+'_ALL.csv' for idx in range(periods)]

    return filepath

# 逐月檢查是否有CSV檔, 否則下載CSV檔    
def CheckDailyCSV(filepath, url, datetype):
    df_all = pd.DataFrame()
    
    for filepathidx in filepath:
        if os.path.isfile(filepathidx):
           df = pd.read_csv(filepathidx)
           df_all = df_all.append(df)
        else:
           if datetype == 'm': 
               stockid = filepathidx[2:6]
               dates = filepathidx[7:15]   
               rqcontent = requests.get(url.format(dates,stockid))
               json_requests = rqcontent.json()
               df = pd.DataFrame(json_requests['data'],columns = json_requests['fields'])
               df['日期'] = df['日期'].apply(lambda x:str(int(x[:3])+1911)+x[3:]) 
               
               numeric_columns = ['成交股數','成交金額','成交筆數']
               for idx in numeric_columns:
                   df[idx]=df[idx].map(lambda x:x.replace(',', '').replace('--', ''))
                   df[idx]=pd.to_numeric(df[idx])
           
           if datetype == 'd':
               dates = filepathidx[2:10]
               rqcontent = requests.get(url.format(dates))
               json_requests = rqcontent.json()
               df = pd.DataFrame(json_requests['data9'],columns = json_requests['fields9'])
               df.insert(loc=0, column='日期', value=[dates[0:4]+'/'+dates[4:6]+'/'+dates[6:8] for cnt in range(df.shape[0])])
               numeric_columns = ['成交股數','成交筆數','成交金額','開盤價','最高價','最低價','收盤價','漲跌價差','最後揭示買價','最後揭示買量','最後揭示賣價','最後揭示賣量','本益比']
               for idx in numeric_columns:
                   df[idx]=df[idx].map(lambda x:x.replace(',', '').replace('--', ''))
                   df[idx]=pd.to_numeric(df[idx])
           
    
           df.to_csv(filepathidx,index=False,header=True) 
           
           df = pd.read_csv(filepathidx)
           df_all = df_all.append(df)
           
           time.sleep(random.uniform(5, 25))
           
    return df_all
       
periods = 5

# 個股日成交資訊
# url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}" 

# 每日收盤行情
url = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={}&type=ALL"  

datetype = 'd'

df = CheckDailyCSV(CreateFilePath(periods, datetype), url, datetype)

#print(df)

# 漲跌幅最大前10名
print(df.nlargest(10, ['漲跌價差']))

# EPS>=1
print(df[df['本益比']>=1])

# K線圖
# fig = go.Figure(data=[go.Candlestick(x=df['日期'],
#                 open=df['開盤價'],
#                 high=df['最高價'],
#                 low=df['最低價'],
#                 close=df['收盤價'])])

# fig.show()    

# 成交均價
# TradedAveragePrice = df['收盤價'].mean()
# print('成交均價：'+str(TradedAveragePrice))

# 標準差
# sd = df['收盤價'].std()
# print('標準差：'+str(sd))

# 最高價
# print(df[df['收盤價']==df['收盤價'].max()])

# 最低價
# print(df[df['收盤價']==df['收盤價'].min()])

# 成交量前三高
# print(df.nlargest(3, ['成交金額']))