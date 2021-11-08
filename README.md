# StockAnalysis
時間序列分析-股票分析實作 課堂練習
 
HW1 股票簡單分析
下載近半年股價 https://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY.html
EDA
1.均價/標準差、最高價/最低價以及發生的日期(篩選條件，例如df[df[‘Close’] == 650])
2.成交量前三高及日期(https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.nlargest.html)

HW2 股票篩選
下載每日行情表5 天 https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html
分析漲跌幅最大前10名。
再加一篩選條件:
EPS>=1
https://www.cnyes.com/twstock/financial4.aspx

HW3 多資料源合併
下載每日行情表5 天 https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html
合併鉅亨網的EPS https://www.cnyes.com/twstock/financial4.aspx
找出EPS>=1且漲幅最大前10名

HW4 偵測買賣訊號
單一股票
1.找出超買/超賣的日期
2.作圖
多股：以RSI找出超買/超賣的股票。
1.RSI高於80% -> 超買
2.RSI低於20% -> 超賣

HW5 股票預測
選擇一支股票預測30天股價：使用ARIMA演算法。
預測是否準確?請寫出測試心得。

HW6 股票預測
選擇一支股票預測30天股價：使用ARIMA演算法。
預測是否準確?請寫出測試心得。

HW7 回測與標竿比較
選擇一支股票回測，並計算損益

HW8 建構投資組合
建構投資組合，並計算損益
