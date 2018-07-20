# pipenv install ibpy2

from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order

def make_contract(symbol, sec_type, exch, prim_exch, curr):
    Contract.m_symbol = symbol
    Contract.m_secType = sec_type
    Contract.m_exchange = exch
    Contract.m_primaryExch = prim_exch
    Contract.m_currency = curr
    return Contract

def make_order(action, quantity, price = None):
    if price is not None:
        order = Order()
        order.m_orderType = 'LMT'
        order.m_totalQuantity = quantity
        order.m_action = action
        order.m_lmtprice = price
    else:
        order = Order()
        order.m_orderType = 'MKT'
        order.m_totalQuantity = quantity
        order.m_action = action
    return order

import datetime as dt
def main():
    conn = Connection.create(port=7497, clientId=999)
    connected = conn.connect()
    if not connected:
            raise Exception("Error in connection")

    oid = 3

    cont = make_contract('T', 'STK', 'SMART', 'SMART', 'USD')
    offer = make_order('BUY', 1)#, 1000.00)

    # conn.placeOrder(oid, cont, offer)

    # https://github.com/blampe/IbPy/issues/49
    endtime = dt.datetime.now().strftime('%Y%m%d %H:%M:%S')
    conn.reqHistoricalData('T', cont, endtime,"1 W", "1 day", "BID", 0, 1) # ADJUSTED_LAST
    """
    conn.reqHistoricalData(
            # tickerId=1,
            tickerId = 'T',
            contract=cont,
            endDateTime=endtime,
            durationStr='1 D',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=0,
            formatDate=1)
    """
            

    
    conn.disconnect()

main()

