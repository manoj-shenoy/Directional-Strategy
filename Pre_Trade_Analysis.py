import numpy as np
import pandas as pd

futures_multiplier = 1.2
tick_size_percentile = 80
bar_size_percentile = 80
coins_tick_dict = {'BCH':0.01, 'BTC':0.01, 'ETH':0.01, 'DASH':0.01, 'LTC':0.01, 'XMR':0.01, 'ETC':0.001, 'BNB':0.001, 'ADA':0.00001, 'LINK':0.001, 'XRP':0.0001, 'XTZ':0.001, 'EOS':0.001}

# Read all files in from directory

paths = [i+'-USDT.parquet' for i in list(coins_tick_dict.keys())]
#paths = [i+'-USDT.parquet' for i in coins_list]
dfs = {p: pd.read_parquet(p, engine='fastparquet') for p in paths}

# Geting rid of "-USDT.parquet" from dfs.keys()

kv = list(dfs.items())
dfs.clear()
for k, v in kv :
    ...
    dfs[k[:-13]] = v

# Create new calculated columns for all dfs

for key,item in dfs.items():
    item = item[['open', 'high', 'low', 'close']]
    item.loc[:,'high-low'] = item['high'] - item['low']
    item.loc[:,'range_percentage'] = item['high-low']/item['close']
    item.loc[:,'range_ticks'] = (item['range_percentage'] * item['close'] * futures_multiplier)/coins_tick_dict[key]
    
    dfs[key] = item

# Average range percentage for each coin (high-low movement per minute multiplied by a factor 
# and taken as a percentage of corresponding price, then averaged across all minutes)

for key,item in dfs.items():
    s = str(key)
    key = np.mean(item['range_percentage'])*futures_multiplier*100
    print(s + " average range percentage: " + str(key) + "%")

# Average of each coin's close price across all minute bars

for key,item in dfs.items():
    s = str(key)
    key = np.mean(item['close'])
    print(s + " average price: " + "$" + str(key))

# Average number of ticks movement per minute for each coin

for key,item in dfs.items():
    s = str(key)
    key = np.mean(item['range_ticks'])
    print(s + " average number of ticks per minute: " + str(key))

# Upper bound for slippage in ticks - 80th (tick_size_percentile variable) percentile of range_ticks column for each coin

for key,item in dfs.items():
    s = str(key)
    key = np.percentile(item['range_ticks'].sort_values(), tick_size_percentile)
    print(s + " " + str(tick_size_percentile) + "th percentile tick size: " + str(key))


# Lower bound for bar size - 80th percentile of range_percentage values for each coin
# Bar size should be at least as much as lower bound to absorb enough volatility to avoid whipsaw movement
# Take percentage in output of current price for every coin  - that would be lower bound for bar size

for key,item in dfs.items():
    s = str(key)
    key = np.percentile(item['range_percentage'].sort_values(), bar_size_percentile)*100
    print(s + " " + str(bar_size_percentile) + "th percentile range_percentage: " + str(key) + "%")
