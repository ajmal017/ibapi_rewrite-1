from ibapi.wrapper import *
from ibapi.client import *
from ibapi.contract import *
from ibapi.order import *
from threading import Thread
import queue
import time


# Wrapper class
class Wrapper(EWrapper):

  # Inicializace datovych front pro servertime a error  #TODO: Pridat answers queue
  # noinspection PyMissingConstructor
  def __init__(self):
    error_queue = queue.Queue()
    self.my_errors_queue = error_queue
    time_queue = queue.Queue()
    self.my_time_queue = time_queue
    self.next_id = 0

  # Answers handling    #TODO: Must be rewritten
  def logAnswer(self, fn_name, fn_params):
    if 'self' in fn_params:
      prms = dict(fn_params)
      del prms['self']
    else:
      prms = fn_params
    answer = "[API ANSWER] %s %s" % (fn_name, prms)
    # DEBUG
    print(answer)
    if fn_name == "orderStatus":
      answer = "[ORDER STATUS %d]: " % prms["orderId"], prms["status"]
      self.my_errors_queue.put(answer)

  # Id handling
  def nextValidId(self, order_id: int):
    self.next_id = order_id

  # Error Handling methods

  def is_error(self):
    error_exists = not self.my_errors_queue.empty()
    return error_exists

  def get_error(self, timeout=6):
    if self.is_error():
      try:
        return self.my_errors_queue.get(timeout=timeout)
      except queue.Empty:
        return None
    return None

  def error(self, reqId, errorCode, errorString):
    errormessage = "[API ERROR %d] Error Code: %d Message: %s" % (reqId, errorCode, errorString)
    if reqId == self.next_id:
      print("IMPORTANT" + errormessage)
    self.my_errors_queue.put(errormessage)

  # Time Handling
  def init_time(self):
    return self.my_time_queue

  def currentTime(self, server_time):
    self.my_time_queue.put(server_time)


# Client class below
class ElCliento(EClient):
  # Here we pass our client class and wrapper to the socket constructor
  def __init__(self, wrapper):
    EClient.__init__(self, wrapper)

  def server_clock(self):
    time_storage = self.wrapper.init_time()
    self.reqCurrentTime()
    max_wait_time = 10
    try:
      requested_time = time_storage.get(timeout=max_wait_time)
    except queue.Empty:
      print("Queue empty or request timed out")
      requested_time = None

    while self.wrapper.is_error():
      print(self.wrapper.get_error(timeout=5))

    return requested_time


# Main Application class, automatically starts on init
class EjPiPi(Wrapper, ElCliento):
  # Main classes initialization
  def __init__(self, ipaddress, portid, clientid):
    Wrapper.__init__(self)
    ElCliento.__init__(self, wrapper=self)

    self.connect(ipaddress, portid, clientid)

    # Threading init
    thread = Thread(target=self.run)
    thread.start()
    setattr(self, "_thread", thread)

  @staticmethod
  def contract_create(symbol, expiration, strike, right):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = "OPT"
    contract.currency = "USD"
    contract.exchange = "SMART"
    contract.lastTradeDateOrContractMonth = expiration
    contract.strike = strike
    contract.right = right
    contract.multiplier = "100"
    return contract

  @staticmethod
  def order_create(action: str, quantity: float):
    order = Order()
    order.action = action
    order.orderType = "MKT"
    order.totalQuantity = quantity
    return order

  # Ticker; Expirace; Typ; Strike; Smer; Mnozstvi
  def send_order(self, symbol, expiration, right, strike, action, quantity):
    contract_object = self.contract_create(symbol, expiration, strike, right)
    order_object = self.order_create(action, quantity)
    self.placeOrder(self.next_id, contract_object, order_object)
    self.reqIds(1)

  def await_id(self):
    for i in range(10):
      if i < 10:
        if not self.next_id == 0:
          return "Connection established with ID: %d" % self.next_id
        else:
          print("Connecting to server")
          time.sleep(1)
      else:
        return "Timed out"


# Basically what this retard does is starts the Application class, waits for servertime and ID, then places order, prints queues and returns with a [success] var
def runMe(symbol, expiration, right, strike, action,
          quantity):  # TODO: This nigga goin down - hanging around for organ picking
  orderCompleted = False
  app = EjPiPi("127.0.0.1", 7497, 0)
  print(app.server_clock())
  print(app.await_id())
  app.send_order(symbol, expiration, right, strike, action, quantity)
  time.sleep(3)
  while app.is_error():
    msg = app.get_error()
    if msg[1] == "Submitted" or "Filled":
      orderCompleted = True
      app.disconnect()
      break
  time.sleep(1)
  app.disconnect()
  return orderCompleted

# TODO: Vytvorit funkci pro ruseni pozic
# TODO: Sledovat splnene kontrakty a predavat do main threadu pro odstraneni z DB

