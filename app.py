import sys,os,datetime,time
from binance.client import Client
from binance.enums import *

from chalicelib import BinanceKeys
# from BinanceKeys import BinanceKey1

from chalicelib import precision,price_precision_dict,quantity_precision_dict

percent_of_marginbal=0.1 # Order size as 10% of Margin Balance 

api_key = BinanceKeys.BinanceKey1['api_key']
api_secret = BinanceKeys.BinanceKey1['api_secret']

client = Client(api_key, api_secret)

# Chalice is a serverless microframework for Python.
# Serverless Apps can be deployed on AWS Lambda using AWS Chalice as serverless back-end

from chalice import Chalice

app = Chalice(app_name='tradingview-binance-alert')

# Defining precision for Price and Qty, Min Ticks and Ticks For Coins - Add coins when required 
price_precision_dict = {"BTCUSDT":2, "BCH":2, "BNBUSDT":2, "DASHUSDT":2, "ETCUSDT":3,"ADAUSDT":5,
                        "EOSUSDT":3, "LINKUSDT":3, "XMRUSDT":2, "XTZUSDT":3}

quantity_precision_dict = {"BTCUSDT":2, "BCH":2, "BNBUSDT":2, "DASHUSDT":3, "ETCUSDT":2,"ADAUSDT":0,
                           "EOSUSDT":1, "LINKUSDT":2, "XMRUSDT":3, "XTZUSDT":1}

mintick_dict = {"BTCUSDT":0.01, "BCH":0.01, "BNBUSDT":0.001, "DASHUSDT":0.01, "ETCUSDT":0.001,"ADAUSDT":0.00001,
                "EOSUSDT":0.001, "LINKUSDT":0.001, "XMRUSDT":0.01, "XTZUSDT":0.001}

ticks_dict = {"BTCUSDT":3195, "BCH":111, "BNBUSDT":73, "DASHUSDT":28, "ETCUSDT":31,"ADAUSDT":35,
              "EOSUSDT":19, "LINKUSDT":18, "XMRUSDT":18, "XTZUSDT":12}


@app.route('/binancebot',methods=['POST','GET'])
def binancebot():
    
    # Parsing the webhook message, which is a Json payload
    webhook_message=app.current_request.json_body
    
    order_spec = {"symbol":webhook_message["symbol"],
                  "price":webhook_message["trigger"],
                  "side": webhook_message["side"]}
    
    # Get Bid-Ask Prices 
    order_book = client.get_order_book(symbol=str(webhook_message["symbol"])[0:-4])
    bid_ask = float(order_book['bids'][0][0])
    ask_ask = float(order_book['asks'][0][0])
    
    price_preci = precision.get_precision(str(webhook_message["symbol"]),
                                          price_precision_dict)
    
    qty_preci = precision.get_precision(str(webhook_message["symbol"]),
                                        quantity_precision_dict)
    
    mintick = precision.get_precision(webhook_message["symbol"], mintick_dict)
    ticks = precision.get_precision(webhook_message["symbol"], ticks_dict)
    
    # Get Initial Position
    position = client.get_asset_balance(asset=str(webhook_message["symbol"])[0:-8])
    
    # Initial USDT Margin balance
#     margin_balance = client.get_asset_balance(asset=webhook_message["symbol"][-8:-4])
    margin_balance = client.futures_account_balance()[0]['balance']
    
    # Position Size
#     position_size = ('%.' + str(qty_preci) + str('f'))%(float(percent_of_marginbal) * float(margin_balance['free'])/bid_ask)
#     position_size = "{:0.0{}f}".format((float(percent_of_marginbal) * float(margin_balance['free'])/bid_ask),qty_preci)
    position_size = round((float(percent_of_marginbal) * float(margin_balance)/bid_ask),
                          int(qty_preci))
    
    # Trigger Price
#     trigger_price = "{:0.0{}f}".format(float(webhook_message["trigger"]),price_preci)
    if webhook_message["side"]=="BUY" and ask_ask >= webhook_message["high"]:
        trigger_price = round(ask_ask + (0.6 * float(mintick) * int(ticks) * ask_ask),int(price_preci))
        
    elif webhook_message["side"]=="BUY" and ask_ask < webhook_message["high"]:#new
        trigger_price = round(float(webhook_message["high"]) + (0.6 * float(mintick) *
                                                                int(ticks)* float(webhook_message["high"])),
                              int(price_preci))

    elif webhook_message["side"]=="SELL" and bid_ask <= webhook_message["low"]:#new
        trigger_price = round(bid_ask - (0.6 * float(mintick) * int(ticks) * bid_ask),int(price_preci))

    elif webhook_message["side"]=="SELL" and bid_ask > webhook_message["low"]:
        trigger_price = round(float(webhook_message["low"]) - (0.6 * float(mintick) *
                                                         int(ticks) * float(webhook_message["low"])),
                              int(price_preci))

#     trigger_price = round(float(webhook_message["trigger"]),int(price_preci))
    
    # Cancel All Open Orders First
    clear_open_orders = client.futures_cancel_all_open_orders(symbol = str(webhook_message["symbol"])[0:-4])
    
   
    if position==0:
#         asset_balance=client.get_asset_balance(asset=symbol[3:0])
#         position_size=%.3f%(percent_of_marginbal * float(asset_balance['free']),6)
        
        response_freshorder=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                        side = webhook_message["side"],type="STOP_MARKET",
                                                        stopPrice = trigger_price,
                                                        quantity = position_size)


    elif position!=0:
        response_closepos=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                      side = webhook_message["side"],
                                                      type = "STOP_MARKET",
                                                      stopPrice = trigger_price,
                                                      closePosition = "true")
        
        response_freshorder=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                        side = webhook_message["side"],
                                                        type = "STOP_MARKET",
                                                        stopPrice = trigger_price,
                                                        quantity = position_size) 
    
    


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

