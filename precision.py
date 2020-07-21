# Defining precision for Price and Qty
price_precision_dict= {"BTCUSDT":2, "BCHUSDT":2, "BNBUSDT":2, "DASHUSDT":2, "ETCUSDT":3,"ADAUSDT":5,
                        "EOSUSDT":3, "LINKUSDT":3, "XMRUSDT":2, "XTZUSDT":3}

quantity_precision_dict = {"BTCUSDT":2, "BCHUSDT":2, "BNBUSDT":2, "DASHUSDT":3, "ETCUSDT":2,"ADAUSDT":0,
                           "EOSUSDT":1, "LINKUSDT":2, "XMRUSDT":3, "XTZUSDT":1}

mintick_dict = {"BTCUSDT":0.01, "BCH":0.01, "BNBUSDT":0.001, "DASHUSDT":0.01, "ETCUSDT":0.001,"ADAUSDT":0.00001,
                "EOSUSDT":0.001, "LINKUSDT":0.001, "XMRUSDT":0.01, "XTZUSDT":0.001}

ticks_dict = {"BTCUSDT":3195, "BCH":111, "BNBUSDT":73, "DASHUSDT":28, "ETCUSDT":31,"ADAUSDT":35,
	      "EOSUSDT":19, "LINKUSDT":18, "XMRUSDT":18, "XTZUSDT":12}

def get_precision(symbol,precision_dict):

    prec = 0.0

    for (key,value) in zip(precision_dict.keys(),precision_dict.values()):
        if symbol[0:-4]==key:
            prec = precision_dict[key]

    return prec
