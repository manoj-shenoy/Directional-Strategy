import pandas as pd
import numpy as np
import datetime
import quantopian.research as res

stocks_list = ['MU', 'T', 'FB', 'CSCO', 'BAC', 'JPM']
tick_size = 0.01
tick_size_percentile = 90
bar_size_percentile = 90
start_date = '2015-01-01'
end_date = '2020-07-18'

# Defining data to retrieve for every desired symbol
# Also removing all NaN rows to avoid errors in averages calculations

def retrieve_data(symbol):
    df_data = pd.DataFrame({'open': res.prices(assets=symbols(symbol), frequency='minute', 
           start=start_date, end=end_date,  price_field=('open')), 
                   'high': res.prices(assets=symbols(symbol), frequency='minute', 
           start=start_date, end=end_date,  price_field=('high')),
                  'low': res.prices(assets=symbols(symbol), frequency='minute', 
           start=start_date, end=end_date,  price_field=('low')),
                  'close': res.prices(assets=symbols(symbol), frequency='minute', 
           start=start_date, end=end_date,  price_field=('close'))})
    
    df_data = df_data[['open','high','low','close']]
    df_data = df_data.dropna(how='all')
    df_data = df_data.tz_convert('US/Eastern')
    
    return df_data
    
# Retrieving data from quantopian.research and saving a dataframe for each symbol

dfs = {stock: retrieve_data(stock) for stock in stocks_list}

# Checking for null values count in OHLC bars of each stock

for key,item in dfs.items():
    s = str(key)
    key = dfs[key]['close'].isnull().sum()
    print(s + " number of null rows: " + str(key))

# Create new calculated columns for all dfs

for key,item in dfs.items():
    item = item[['open', 'high', 'low', 'close']]
    item.loc[:,'high-low'] = item['high'] - item['low']
    item.loc[:,'range_percentage'] = item['high-low']/item['close']
    item.loc[:,'range_ticks'] = (item['range_percentage'] * item['close'])/tick_size
    
    dfs[key] = item

# Average range percentage for each stock (high-low movement per minute 
# taken as a percentage of corresponding price, then averaged across all minutes)

for key,item in dfs.items():
    s = str(key)
    key = np.mean(item['range_percentage'])*100
    print(s + " average range percentage: " + str(key) + "%")
    
# Average of each stock's close price across all minute bars

for key,item in dfs.items():
    s = str(key)
    key = np.mean(item['close'])
    print(s + " average price: " + "$" + str(key))
    
# Average number of ticks movement per minute for each stock

for key,item in dfs.items():
    s = str(key)
    key = np.mean(item['range_ticks'])
    print(s + " average number of ticks per minute: " + str(key))
    
# Upper bound for slippage in ticks - nth (tick_size_percentile variable) percentile of range_ticks column for each stock

for key,item in dfs.items():
    s = str(key)
    key = np.percentile(item['range_ticks'].sort_values(), tick_size_percentile)
    print(s + " " + str(tick_size_percentile) + "th percentile tick size: " + str(key))
    
# Lower bound for bar size - nth percentile of range_percentage values for each stock
# Bar size should be at least as much as lower bound to absorb enough volatility to avoid whipsaw movement
# Take percentage in output of current price for every stock  - that would be lower bound for bar size

for key,item in dfs.items():
    s = str(key)
    key = np.percentile(item['range_percentage'].sort_values(), bar_size_percentile)*100
    print(s + " " + str(bar_size_percentile) + "th percentile range_percentage: " + str(key) + "%")
