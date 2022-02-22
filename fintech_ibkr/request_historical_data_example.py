# This is an example of a test script.
# When you've correctly coded your 'historicalData' override method in
#  synchronous_functions.py, this script should return a dataframe that's
#  ready to be loaded into the candlestick graph constructor.

# from fintech_ibkr import *
import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time
import plotly.graph_objects as go

# def req_historical_data(contract, endDateTime='', durationStr='30 D',
#                        barSizeSetting='1 hour', whatToShow='MIDPOINT',
#                        useRTH=True):

class ibkr_app(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.error_messages = pd.DataFrame(columns=[
            'reqId', 'errorCode', 'errorString'
        ])
        self.next_valid_id = None
        self.historical_data = pd.DataFrame(columns=["date", "open", "high", "low", "close"])
        self.historical_data_end = ''  # pd.DataFrame()

    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)

    def nextValidId(self, orderId: int):
        self.next_valid_id = orderId

    def historicalData(self, reqId, bar):
        # YOUR CODE GOES HERE: Turn "bar" into a pandas dataframe, formatted
        #   so that it's accepted by the plotly candlestick function.
        # Take a look at candlestick_plot.ipynb for some help!
        # assign the dataframe to self.historical_data.
        row = pd.DataFrame(
            {'date': [bar.date],
             'open': [bar.open],
             'high': [bar.high],
             'low': [bar.low],
             'close': [bar.close]
             }
        )
        self.historical_data = pd.concat([self.historical_data, row], ignore_index=True)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        # super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        self.historical_data_end = reqId

app = ibkr_app()

app.connect('127.0.0.1', 7497, 10645)
while not app.isConnected():
    time.sleep(0.01)

def run_loop():
    app.run()

# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

while isinstance(app.next_valid_id, type(None)):
    time.sleep(0.01)

value = "EUR.USD" # This is what your text input looks like on your app
# Create a contract object
contract = Contract()
contract.symbol = value.split(".")[0]
contract.secType = 'CASH'
contract.exchange = 'IDEALPRO'  # 'IDEALPRO' is the currency exchange.
contract.currency = value.split(".")[1]


tickerId = app.next_valid_id
app.reqHistoricalData(
    tickerId, contract, endDateTime='',           # <-- make a reactive input
    durationStr='30 D',       # <-- make a reactive input
    barSizeSetting='1 hour',  # <-- make a reactive input
    whatToShow='MIDPOINT',    # <-- make a reactive input
    useRTH= 0,                 # <-- make a reactive input
    formatDate=1, keepUpToDate=False, chartOptions=[])

while app.historical_data_end != tickerId:
    time.sleep(0.01)

app.disconnect()

app.historical_data

#value = "EUR.USD" # This is what your text input looks like on your app

# Create a contract object
#contract = Contract()
#contract.symbol = value.split(".")[0]
#contract.secType = 'CASH'
#contract.exchange = 'IDEALPRO'  # 'IDEALPRO' is the currency exchange.
#contract.currency = value.split(".")[1]

# Get your historical data
#historical_data = req_historical_data(contract)

# Print it! This should be a dataframe that's ready to go.
#print(historical_data)

# This script is an excellent place for scratch work as you figure this out.

fig = go.Figure(
    data=[
        go.Candlestick(
            x=app.historical_data['date'],
            open=app.historical_data['open'],
            high=app.historical_data['high'],
            low=app.historical_data['low'],
            close=app.historical_data['close']
        )
    ]
)