import sys,os,datetime,time,progressbar
import numpy as np
import pandas as pd
from binance.client import Client
from binance.enums import *

# import site
# site.addsitedir(r'C:\\Users\\Admin\\python-binance-master\\examples')
from chalicelib import BinanceKeys
# from BinanceKeys import BinanceKey1
# import technical_indicators
percent_of_marginbal=0.1 # Order size as 10% of Margin Balance 
# watch_list=['BTCUSDT','ETHUSDT','LTCUSDT','XTZUSDT','DASHUSDT','EOSUSDT'] # Add more

api_key = BinanceKeys.BinanceKey1['api_key']
api_secret = BinanceKeys.BinanceKey1['api_secret']

client = Client(api_key, api_secret)

asset_balance=client.get_asset_balance(asset=symbol[3:0]) # Initial Margin balance
position_size=%.3f%(percent_of_marginbal * float(asset_balance['free']),6)

# Chalice is a serverless microframework for Python.
# Serverless Apps can be deployed on AWS Lambda using AWS Chalice as serverless back-end

from chalice import Chalice

app = Chalice(app_name='tradingview-binance-alert')


@app.route('/binancebot/',methods=['POST'])
def binancebot():
    
    # Parsing the webhook message, which is a Json payload
    webhook_message=app.current_request.json_body
    
    order_spec = {"symbol":webhook_message["symbol"],
                  "price":webhook_message["trigger"],
                  "side": webhook_message["side"]}
    
    # Get Initial Margin Balance
    position=client.get_asset_balance(asset=webhook_message["symbol"][0:-8])
    
    # Cancel All Open Orders First
    clear_open_orders=futures_cancel_all_open_orders(symbol=webhook_message["symbol"][0:-4])

    if position==0:
#         asset_balance=client.get_asset_balance(asset=symbol[3:0])
#         position_size=%.3f%(percent_of_marginbal * float(asset_balance['free']),6)
        response_freshorder=client.futures_create_order(symbol=webhook_message["symbol"][0:-4],
                                                        side=webhook_message["side"],type="STOP_MARKET",
                                                        stopPrice=webhook_message["trigger"],
                                                        quantity=position_size)


    elif position!=0:
        response_closepos=client.futures_create_order(symbol=webhook_message["symbol"][0:-4],
                                                      side=webhook_message["side"],
                                                      type="STOP_MARKET",stopPrice=webhook_message["trigger"],
                                                      closePosition= true)
        
        response_freshorder=client.futures_create_order(symbol=webhook_message["symbol"][0:-4],
                                                        side=webhook_message["side"],
                                                        type="STOP_MARKET",stopPrice=webhook_message["trigger"],
                                                        stopPrice=webhook_message["trigger"],
                                                        quantity=position_size)
   
    
    return response_closepos.json(),response_freshorder.json()


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
