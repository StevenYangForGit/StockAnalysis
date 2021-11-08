# -*- coding: utf-8 -*-
"""
Created on Sun Jul  4 14:51:44 2021

@author: user
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
from selenium import webdriver
from bs4 import BeautifulSoup
import numpy as np

"""
datetype = 'm'：產生各股每月檔案路徑['./2330_20210601.csv', './2330_20210501.csv', './2331_20210601.csv']
datetype = 'd'：產生每日(排除假日)檔案路徑['./20210630_ALL.csv', './20210629_ALL.csv', './20210628_ALL.csv']
"""
def CreateFilePath(periods, datetype):
    if datetype == 'm':
        filepath = ['./'+(date.today() + relativedelta(months=-idx)).strftime('%Y%m01')+'_ALL.csv' for idx in range(periods)]    

    if datetype == 'd':
        filepath = ['./'+(date.today() - BDay(idx)).strftime('%Y%m%d')+'_ALL.csv' for idx in range(1,periods+1)]

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
                   
               df['日期']=pd.to_datetime(df['日期'])
               
               df["漲跌價差"] = df.apply(lambda r: 0-r["漲跌價差"] if r["漲跌(+/-)"] =='-' else r["漲跌價差"], axis=1)

               df["漲跌幅"] = round(df["漲跌價差"] / (df["收盤價"] - df["漲跌價差"]), 2) 
    
           df.to_csv(filepathidx,index=False,header=True) 
           
           df = pd.read_csv(filepathidx)
           df_all = df_all.append(df)
           
           time.sleep(random.uniform(5, 25))
           
    return df_all

def GetEPS(url_eps):
    filepath = './eps.csv'
    df_all = pd.DataFrame()
    
    if os.path.isfile(filepath):
        df = pd.read_csv(filepath)
        df_all = df_all.append(df)
    else:    
        head = []
        content = []
    
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"')
        chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('blink-settings=imagesEnabled=false') #不加载图片, 提升速度
        chrome_options.add_argument('--headless') #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(url_eps)
    
        soup = BeautifulSoup(driver.page_source, "html.parser")
    
        season = soup.find('cite',class_ ="tydate").text.strip()[0:6]
    
        for thcontent in soup.find('table',id ="ctl00_ContentPlaceHolder1_GridView1").find_all("th"):   
            head.append(thcontent.text.strip())
        
        for tbcontent in soup.find('table',id ="ctl00_ContentPlaceHolder1_GridView1").find_all("td"):   
            content.append(tbcontent.text.strip())
       
        head[0] = '證券代號'
        head[1] = '證券名稱'
       
        df = pd.DataFrame(np.array(content).reshape(-1,8),columns = np.array(head))
        
        df['年季度'] = season
        numeric_columns = ['營業收入','營業損益','業外收入','稅前損益','稅後損益','每股EPS(元)']
        for idx in numeric_columns:
            df[idx]=df[idx].map(lambda x:x.replace(',', '').replace('--', ''))
            df[idx]=pd.to_numeric(df[idx])
        
        df.to_csv(filepath,index=False,header=True) 
           
        df = pd.read_csv(filepath)
        df_all = df_all.append(df)
        
    return df_all

periods = 5

# 個股日成交資訊
# url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}" 

# 每日收盤行情
url = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={}&type=ALL"  

url_eps = "https://www.cnyes.com/twstock/financial4.aspx" 

datetype = 'd'

df = CheckDailyCSV(CreateFilePath(periods, datetype), url, datetype)

df2 = GetEPS(url_eps)

df_pivot = pd.pivot_table(df, index='日期', columns='證券名稱', values='漲跌價差')
df_summary = pd.DataFrame(df_pivot.sum())
df_summary.columns = ['漲跌價差']

result = pd.merge(df_summary, df2, how='left', on=['證券名稱'])

print(result[result['每股EPS(元)']>=1].nlargest(10, ['漲跌價差']))

# 漲跌幅最大前10名
# print(df.nlargest(10, ['漲跌價差']))

# EPS>=1
# print(df[df['本益比']>=1])

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