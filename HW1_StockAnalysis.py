# -*- coding: utf-8 -*-
"""
Created on Sat Jun 26 23:02:00 2021

@author: user
"""

from datetime import date
from dateutil.relativedelta import relativedelta
import os
import requests
import pandas as pd
import time
import random
import plotly.graph_objects as go

# 產生各股每月檔案路徑['./2330_20210601.csv', './2330_20210501.csv', './2331_20210601.csv', './2331_20210501.csv']
def CreateFilePath(periods, stock_list):
    filepath = ['./'+stockno+'_'+(date.today() + relativedelta(months=-idx)).strftime('%Y%m01')+'.csv' for stockno in stock_list for idx in range(periods)]    
    
    return filepath

# 逐月檢查是否有CSV檔, 否則下載CSV檔    
def CheckDailyCSV(filepath, url):
    df_all = pd.DataFrame()
    
    for filepathidx in filepath:
        if os.path.isfile(filepathidx):
           df = pd.read_csv(filepathidx)
           df_all = df_all.append(df)
        else:
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
    
           df.to_csv(filepathidx,index=False,header=True) 
           
           df = pd.read_csv(filepathidx)
           df_all = df_all.append(df)
           
           time.sleep(random.uniform(5, 25))
           
    return df_all
       
periods = 6

stock_list = ['2330']

url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}"  

df = CheckDailyCSV(CreateFilePath(periods, stock_list), url)

print(df)

# K線圖
fig = go.Figure(data=[go.Candlestick(x=df['日期'],
                open=df['開盤價'],
                high=df['最高價'],
                low=df['最低價'],
                close=df['收盤價'])])

fig.show()    

# 成交均價
TradedAveragePrice = df['收盤價'].mean()
print('成交均價：'+str(TradedAveragePrice))

# 標準差
sd = df['收盤價'].std()
print('標準差：'+str(sd))

# 最高價
print(df[df['收盤價']==df['收盤價'].max()])

# 最低價
print(df[df['收盤價']==df['收盤價'].min()])

# 成交量前三高
print(df.nlargest(3, ['成交金額']))