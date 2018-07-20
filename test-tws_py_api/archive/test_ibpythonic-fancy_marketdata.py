import sys
sys.path.insert(0,'C:\\TWS API\\source\\pythonclient')




from ibpythonic import ibConnection, message
from ibapi.contract import Contract
from time import sleep

# print all messages from TWS
def watcher(msg):
    print (msg)

# show Bid and Ask quotes
def my_BidAsk(msg):
    if msg.field == 1:
        print ('%s:%s: bid: %s' % (contractTuple[0],
                       contractTuple[6], msg.price))
    elif msg.field == 2:
        print ('%s:%s: ask: %s' % (contractTuple[0], contractTuple[6], msg.price))

def makeStkContract(contractTuple):
    newContract = Contract()
    newContract.symbol = contractTuple[0]
    newContract.secType = contractTuple[1]
    newContract.exchange = contractTuple[2]
    newContract.currency = contractTuple[3]
    #newContract.expiry = contractTuple[4]
    #newContract.strike = contractTuple[5]
    #newContract.right = contractTuple[6]
    print ('Contract Values:%s,%s,%s,%s,%s,%s,%s:' % contractTuple)
    return newContract

if __name__ == '__main__':
    con = ibConnection(port=7497)
    con.registerAll(watcher)
    showBidAskOnly = True  # set False to see the raw messages
    if showBidAskOnly:
        con.unregister(watcher, message.tickSize, message.tickPrice,
                       message.tickString, message.tickOptionComputation)
        con.register(my_BidAsk, message.tickPrice)
    con.connect()
    sleep(1)
    tickId = 1

    # Note: Option quotes will give an error if they aren't shown in TWS
    contractTuple = ('QQQQ', 'STK', 'SMART', 'USD', '', 0.0, '')
    #contractTuple = ('QQQQ', 'OPT', 'SMART', 'USD', '20070921', 47.0, 'CALL')
    #contractTuple = ('ES', 'FUT', 'GLOBEX', 'USD', '200709', 0.0, '')
    #contractTuple = ('ES', 'FOP', 'GLOBEX', 'USD', '20070920', 1460.0, 'CALL')
    #contractTuple = ('EUR', 'CASH', 'IDEALPRO', 'USD', '', 0.0, '')
    stkContract = makeStkContract(contractTuple)
    print ('* * * * REQUESTING MARKET DATA * * * *')
    con.reqMktData(tickId, stkContract, '', False, False, False)
    sleep(15)
    print ('* * * * CANCELING MARKET DATA * * * *')
    con.cancelMktData(tickId)
    sleep(1)
    con.disconnect()
    sleep(1)
