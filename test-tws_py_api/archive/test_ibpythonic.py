import sys
sys.path.insert(0,'C:\\TWS API\\source\\pythonclient')


from ibpythonic import ibConnection, message
from ibapi.contract import Contract

def contractDetailsHandler(msg):
    print("Contract deatils:")
    print(msg.contractDetails)
    # do something with contractDetails msg

def errorHandler(msg):
    print("Error:")
    print(msg)


def mktDataHandler(msg):
    print("mkt data:")
    print(msg)


print("connection")
# conn = ibConnection(port=4001, clientId=100)
conn = ibConnection(port=7497, clientId=999)

print("register")
conn.register(contractDetailsHandler, message.contractDetails)
conn.register(errorHandler, message.error)

conn.register(mktDataHandler, message.mktData)
conn.register(errorHandler, message.error)


print("contract")
contract = Contract()
contract.symbol = "AAPL"
contract.exchange = "SMART"
contract.secType = "STK"
contract.currency = "USD"

#import pdb
#pdb.set_trace()
print("connect")
connected = conn.connect()

if not connected:
    raise Exception("Failed to connect")
else:
    print("succeeded in connect")

print("req contract details")
conn.reqContractDetails(1, contract)

print("unregister")
conn.unregister(contractDetailsHandler, message.contractDetails)
conn.unregister(errorHandler, message.error)

print("disconnect")
conn.disconnect()
