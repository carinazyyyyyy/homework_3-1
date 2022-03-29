from datetime import datetime

import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import threading
import time

# If you want different default values, configure it here.
default_hostname = '127.0.0.1'
default_port = 7497
default_client_id = 10645 # can set and use your Master Client ID
timeout_sec = 5

# This is the main app that we'll be using for sync and async functions.
class ibkr_app(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.error_messages = pd.DataFrame(columns=[
            'reqId', 'errorCode', 'errorString'
        ])
        self.next_valid_id = None
        self.current_time = None
        ########################################################################
        # Here, you'll need to change Line 30 to initialize
        # self.historical_data as a dataframe having the column names you
        # want to use. Clearly, you'll want to make sure your colnames match
        # with what you tell the candlestick figure to expect when you create
        # it in your app!
        # I've already done the same general process you need to go through
        # in the self.error_messages instance variable, so you can use that as
        # a guide.
        self.historical_data = pd.DataFrame(columns=["date", "open", "high", "low", "close"])
        self.historical_data_end = ''
        self.contract_details = ''
        self.contract_details_end = ''

        self.order_status = pd.DataFrame(
            columns=['orderId', 'status', 'filled', 'remaining', 'avgFillPrice', 'permId', 'parentId', 'lastFillPrice',
                     'clientId', 'whyHeld', 'mktCapPrice']
        )
    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)
        self.error_messages = pd.concat(
            [self.error_messages, pd.DataFrame({
                "reqId": [reqId],
                "errorCode": [errorCode],
                "errorString": [errorString]
            })])

    def managedAccounts(self, accountsList):
        self.managed_accounts = [i for i in accountsList.split(",") if i]

    def nextValidId(self, orderId: int):
        self.next_valid_id = orderId

    def currentTime(self, time: int):
        self.current_time = datetime.fromtimestamp(time)

    def historicalData(self, reqId, bar):
        # YOUR CODE GOES HERE: Turn "bar" into a pandas dataframe, formatted
        #   so that it's accepted by the plotly candlestick function.
        # Take a look at candlestick_plot.ipynb for some help!
        # assign the dataframe to self.historical_data.
        # print(reqId, bar)
        row = pd.DataFrame(
            {'date': [bar.date],
             'open': [bar.open],
             'high': [bar.high],
             'low': [bar.low],
             'close': [bar.close]
             }
        )
        self.historical_data = pd.concat([self.historical_data, row], ignore_index=True)
        #self.historical_data = bar

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        # super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        self.historical_data_end = reqId

    #def contractDetails(self, reqId: int, contractDetails):
    #    print(type(contractDetails))
    #    print(contractDetails)
    #    self.contract_details = contractDetails

    def contractDetailsEnd(self, reqId: int):
        print("ContractDetailsEnd. ReqId:", reqId)
        self.contract_details_end = reqId

    def orderStatus(self, orderId, status: str, filled: float,
                    remaining: float, avgFillPrice: float, permId: int,
                    parentId: int, lastFillPrice: float, clientId: int,
                    whyHeld: str, mktCapPrice: float):
        print('order status')

        print(self.order_status)
        print(type(self.order_status))
        self.order_status = pd.concat(
            [
                self.order_status,
                pd.DataFrame({
                    'order_id': [orderId],
                    'status': [status],
                    'filled': [filled],
                    'remaining': [remaining],
                    'avg_fill_price': [avgFillPrice],
                    'perm_id': [permId],
                    'parent_id': [parentId],
                    'last_fill_price': [lastFillPrice],
                    'client_id': [clientId],
                    'why_held': [whyHeld],
                    'mkt_cap_price': [mktCapPrice],
                    'timestamp': ['']
                })
            ],
            ignore_index=True
        )
        self.order_status.drop_duplicates(inplace=True)

    def openOrder(self, orderId, contract, order, orderState):
        print('open order')
        print(contract)
        print(order)
        print(orderState)

    def openOrderEnd(self):
        print('open order end')


def fetch_managed_accounts(hostname=default_hostname, port=default_port,
                           client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(0.01)
    def run_loop():
        app.run()
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    while isinstance(app.next_valid_id, type(None)):
        time.sleep(0.01)
    app.disconnect()
    return app.managed_accounts

def fetch_contract_details(contract, hostname=default_hostname,
                          port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(0.01)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    while isinstance(app.next_valid_id, type(None)):
        time.sleep(0.01)
    tickerId = app.next_valid_id
    app.reqContractDetails(tickerId, contract)
    while app.contract_details_end != tickerId:
        time.sleep(0.01)
        if app.error_messages.iloc[-1]['errorCode'] == 200:
            print(app.error_messages)
            app.disconnect()
            return None, app.error_messages.iloc[-1]['errorString']
    app.disconnect()
    return app.contract_details, None


def fetch_current_time(hostname=default_hostname,
                       port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, int(port), int(client_id))
    start_time = datetime.now()
    while not app.isConnected():
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_current_time",
                "timeout",
                "couldn't connect to IBKR"
            )

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    start_time = datetime.now()
    while app.next_valid_id is None:
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_current_time",
                "timeout",
                "next_valid_id not received"
            )

    app.reqCurrentTime()
    start_time = datetime.now()
    while app.current_time is None:
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_current_time",
                "timeout",
                "current_time not received"
            )
    app.disconnect()
    return app.current_time


def fetch_historical_data(contract, endDateTime='', durationStr='30 D',
                          barSizeSetting='1 hour', whatToShow='MIDPOINT',
                          useRTH=True, hostname=default_hostname,
                          port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(0.01)
    def run_loop():
        app.run()
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    while isinstance(app.next_valid_id, type(None)):
        time.sleep(0.01)
    tickerId = app.next_valid_id
    app.reqHistoricalData(
        tickerId, contract, endDateTime, durationStr, barSizeSetting,
        whatToShow, useRTH, formatDate=1, keepUpToDate=False, chartOptions=[])
    while app.historical_data_end != tickerId:
        time.sleep(0.01)
    app.disconnect()
    return app.historical_data

def place_order(contract, order, hostname=default_hostname,
                           port=default_port, client_id=default_client_id):

    app = ibkr_app()
    app.connect(hostname, port, client_id)
    while not app.isConnected():
        time.sleep(0.01)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    while app.next_valid_id is None:
        time.sleep(0.01)

    app.placeOrder(app.next_valid_id, contract, order)
    while not (('Submitted' in set(app.order_status['status']) or ('Filled' in set(app.order_status['status'])))):
        time.sleep(0.25)

    app.disconnect()

    return app.order_status

def fetch_contract_details_new(contract, hostname=default_hostname,
                           port=default_port, client_id=default_client_id):
    app = ibkr_app()
    app.connect(hostname, int(port), int(client_id))
    start_time = datetime.now()
    while not app.isConnected():
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_contract_details",
                "timeout",
                "couldn't connect to IBKR"
            )

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    start_time = datetime.now()
    while app.next_valid_id is None:
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_contract_details",
                "timeout",
                "next_valid_id not received"
            )

    tickerId = app.next_valid_id
    app.reqContractDetails(tickerId, contract)

    start_time = datetime.now()
    while app.contract_details_end != tickerId:
        time.sleep(0.01)
        if (datetime.now() - start_time).seconds > timeout_sec:
            app.disconnect()
            raise Exception(
                "fetch_contract_details",
                "timeout",
                "contract_details not received"
            )

    app.disconnect()

    return app.contract_details


# def fetch_contract_details (contract, hostname=default_hostname,
#                           port=default_port, client_id=default_client_id):
#     app = ibkr_app()
#     app.connect(hostname, port, client_id)
#     while not app.isConnected():
#         time.sleep(0.01)
#
#     def run_loop():
#         app.run()
#
#     api_thread = threading.Thread(target=run_loop, daemon=True)
#     api_thread.start()
#     while isinstance(app.next_valid_id, type(None)):
#         time.sleep(0.01)
#     tickerId = app.next_valid_id
#     app.reqContractDetails(tickerId, contract)
#
#     while app.contract_details_end != tickerId:
#         time.sleep(0.01)
#         if app.error_messages.iloc[-1]['reqId'] == 1:
#             app.disconnect()
#             return "error occurred"
#
#     app.disconnect()
#     return app.contract_details


