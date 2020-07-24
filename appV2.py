import sys,os,datetime,time
from binance.client import Client
from binance.enums import *

from chalicelib import BinanceKeys
# from BinanceKeys import BinanceKey1

from chalicelib import precision #, precision.price_precision_dict, precision.quantity_precision_dict, precision.mintick_dict, precision.ticks_dict

percent_of_marginbal=0.1 # Order size as 10% of Margin Balance 

api_key = BinanceKeys.BinanceKey1['api_key']
api_secret = BinanceKeys.BinanceKey1['api_secret']

client = Client(api_key, api_secret)

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
    
    '''
    # Chalice is a serverless microframework for Python.

    # Serverless Apps can be deployed on AWS Lambda using AWS Chalice as serverless back-end

    # Chalice App for Cloud deployment using Tradingview Webhooks for Alert Messages
    '''
    
    # Parsing the webhook message, which is a Json payload
    webhook_message=app.current_request.json_body
    
    order_spec = {"symbol":webhook_message["symbol"],
                  "price":webhook_message["trigger"],
                  "side": webhook_message["side"]}
    
    # Get Bid-Ask Prices 
    order_book = client.get_order_book(symbol=str(webhook_message["symbol"])[0:-4])
    bid_ask = float(order_book['bids'][0][0]) # Current Market price when selling
    ask_ask = float(order_book['asks'][0][0]) # Current Market price wwhen buying
    
    # Get Price Precision for the symbol
    price_preci = precision.get_precision(str(webhook_message["symbol"]),
                                          price_precision_dict)
    
    # Get Quantity Precision for the symbol
    qty_preci = precision.get_precision(str(webhook_message["symbol"]),
                                        quantity_precision_dict)
    
    # Get Minimum Tick Size for the symbol
    mintick = precision.get_precision(webhook_message["symbol"], mintick_dict)
    
    # Get Ticks as defined from Research on Ticks Slippage
    ticks = precision.get_precision(webhook_message["symbol"], ticks_dict)
    
    # Get Position
#     position = client.get_asset_balance(asset=str(webhook_message["symbol"])[0:-8])
    position = round(abs(float(precision.get_positions(symbol = str(webhook_message["symbol"])[0:-4],
                                       all_pos_info= client.futures_position_information()))),
                     int(qty_preci))
    
    # Initial USDT Margin balance
#     margin_balance = client.get_asset_balance(asset=webhook_message["symbol"][-8:-4])
    margin_balance = client.futures_account_balance()[0]['balance']
    
    # Position Size
#     position_size = ('%.' + str(qty_preci) + str('f'))%(float(percent_of_marginbal) * float(margin_balance['free'])/bid_ask)
#     position_size = "{:0.0{}f}".format((float(percent_of_marginbal) * float(margin_balance['free'])/bid_ask),qty_preci)
    position_size = round((float(percent_of_marginbal) * float(margin_balance)/bid_ask),
                          int(qty_preci))
    
    # Buy & Sell Trigger Prices
    buy_trigger_price = round(float(webhook_message["high"]) + (0.6 * float(mintick) * int(ticks)),
                              int(price_preci))
    
    sell_trigger_price = round(float(webhook_message["low"]) - (0.6 * float(mintick) * int(ticks)),
                              int(price_preci))

#     trigger_price = "{:0.0{}f}".format(float(webhook_message["trigger"]),price_preci)
#     if webhook_message["side"]=="BUY" and ask_ask >= webhook_message["high"]:
#         trigger_price = round(ask_ask + (0.6 * float(mintick) * int(ticks)),int(price_preci))
        
#     elif webhook_message["side"]=="BUY" and ask_ask < webhook_message["high"]:#new
#         trigger_price = round(float(webhook_message["high"]) + (0.6 * float(mintick) * int(ticks)),
#                               int(price_preci))

#     elif webhook_message["side"]=="SELL" and bid_ask <= webhook_message["low"]:#new
#         trigger_price = round(bid_ask - (0.6 * float(mintick) * int(ticks)),int(price_preci))

#     elif webhook_message["side"]=="SELL" and bid_ask > webhook_message["low"]:
#         trigger_price = round(float(webhook_message["low"]) - (0.6 * float(mintick) * int(ticks)),
#                               int(price_preci))

#     trigger_price = round(float(webhook_message["trigger"]),int(price_preci))
    
    # Cancel All Open Orders First
    clear_open_orders = client.futures_cancel_all_open_orders(symbol = str(webhook_message["symbol"])[0:-4])
    
    # -----------------------------------------------------------------------------------
    # ***************************////   OMS Logic   \\\\*********************************  
    # -----------------------------------------------------------------------------------
    '''
    Pseudo-Code: (Incomplete)
    
    No Existing Position:
    -----------------------
          On a Buy Signal, If Current Price >= Buy Trigger Price, then buy at market
    else if Current Price < Buy Trigger Price, then place stop mkt order to buy above Buy Trigger Price
    
          On a Sell Signal, if Current Price <= Sell Trigger Price, then sell at market
    else if Current Price > Sell_Trigger_Price, then place stop mkt order to sell
    
    Existing Sell Position:
    ------------------------
     
    
    Existing Buy Position:
    ------------------------
    
    
    '''
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # ---------------- OMS Logic For No Prior Position ------------------
    
    # No Position and Buy signal and Current Price >= Buy Trigger Price, place a Buy Market Order
    if position==0 and webhook_message["side"]=="BUY" and ask_ask >= buy_trigger_price:

        response_freshorder=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                        side = webhook_message["side"],type="MARKET",
                                                        quantity = position_size)
    
    # No Position and Buy Signal and Current Price < Buy Trigger Price,place Buy Stop Market order above Buy Trigger Price
    elif position==0 and webhook_message["side"]=="BUY" and ask_ask < buy_trigger_price: 
    
        response_freshorder=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                        side = webhook_message["side"],type="STOP_MARKET",
                                                        stopPrice = buy_trigger_price,
                                                        quantity = position_size)
    
    # No Position and Sell Signal and Current Price <= Sell Trigger Price,place a Sell Market Order
    elif position==0 and webhook_message["side"]=="SELL" and bid_ask <= sell_trigger_price: 
    
        response_freshorder=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                        side = webhook_message["side"],type="MARKET",
                                                        quantity = position_size)
    
    # No Position and Sell Signal and Current Price > Sell Trigger Price,place Sell Stop Market order below Sell Trigger Price
    elif position==0 and webhook_message["side"]=="SELL" and bid_ask > sell_trigger_price: 
    
        response_freshorder=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                        side = webhook_message["side"],type="STOP_MARKET",
                                                        stopPrice = sell_trigger_price,
                                                        quantity = position_size)
    
    
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # ---------------- OMS Logic For Existing Sell Position ------------------
    
    # Existing Sell Position and Buy Signal and Current Price >= Buy Trigger Price,
    #  Close Position First at Market Price
    # Place Fresh Buy Order at Market Price
    elif position < 0 and webhook_message["side"]=="BUY" and ask_ask >= buy_trigger_price:
        
        response_closepos=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                      side = webhook_message["side"],
                                                      type = "MARKET",
                                                      quantity = position)
#                                                       closePosition = "true")
        
        response_freshorder=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                        side = webhook_message["side"],
                                                        type = "MARKET",
                                                        quantity = position_size) 

    # Existing Sell Position and Buy Signal and Current Price < Buy Trigger Price, 
    # Place Stop Market Order to Close Position abv Buy Trigger Price
    # Place Fresh Buy Stop Market Order above Buy Trigger Price
    elif position < 0 and webhook_message["side"]=="BUY" and ask_ask < buy_trigger_price:
        
        response_closepos=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                      side = webhook_message["side"],
                                                      type = "STOP_MARKET",
                                                      stopPrice = buy_trigger_price)
#                                                       closePosition = "true")
        
        response_freshorder=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                        side = webhook_message["side"],
                                                        type = "STOP_MARKET",
                                                        stopPrice = buy_trigger_price,
                                                        quantity = position_size) 
    
    
    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    # ---------------- OMS Logic For Existing Buy Position ------------------
    
    # Existing Buy Position and Sell Signal and Current Price <= Sell Trigger price,
    # Close Position by placing a Sell Market Order
    # Place a Fresh Sell Order at Market price
    elif position > 0 and webhook_message["side"]=="SELL" and bid_ask <= sell_trigger_price:
        
        response_closepos=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                      side = webhook_message["side"],
                                                      type = "MARKET",
#                                                       closePosition = "true",
                                                      quantity = position)
        
        response_freshorder=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                        side = webhook_message["side"],
                                                        type = "MARKET",
                                                        quantity = position_size) 

    
    # Existing Buy Position and Sell Signal and Current Price > Sell Trigger price,
    # Close Position by placing a Sell Stop Market Order below Sell Trigger Price
    # Place a Fresh Sell Stop Market Order below Sell Trigger Price
    elif position > 0 and webhook_message["side"]=="SELL" and bid_ask > sell_trigger_price:
        
        response_closepos=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                      side = webhook_message["side"],
                                                      type = "STOP_MARKET",
                                                      stopPrice = sell_trigger_price)
#                                                       closePosition = "true")
        
        response_freshorder=client.futures_create_order(symbol = str(webhook_message["symbol"])[0:-4],
                                                        side = webhook_message["side"],
                                                        type = "STOP_MARKET",
                                                        stopPrice = sell_trigger_price,
                                                        quantity = position_size) 
    
    # Existing Buy or sell Position and Same Side Signal, Do nothing!
    elif (position > 0 and webhook_message["side"]=="BUY") or (position < 0 and webhook_message["side"]=="SELL"):
        
        print ("Same Side Position already exists")
