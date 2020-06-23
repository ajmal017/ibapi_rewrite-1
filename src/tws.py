from ibapi.wrapper import *
from ibapi.client import *
from ibapi.contract import *
from ibapi.order import *
from threading import Thread
import queue
import time
import inspect


# Wrapper class
def log(prefix, message):
  print(prefix, message)


class Wrapper(EWrapper):

  # Inicializace datovych front pro servertime, answers a error
  # noinspection PyMissingConstructor
  def __init__(self, kveve):
    error_queue = kveve
    self.my_errors_queue = error_queue

    time_queue = queue.Queue()
    self.my_time_queue = time_queue

    answers_queue = queue.Queue()
    self.my_answers_queue = answers_queue
    self.next_id = 0

  # Answers handling    #TODO: Must be rewritten
  def logAnswer(self, fn_name, fn_params):
    if 'self' in fn_params:
      prms = dict(fn_params)
      del prms['self']
    else:
      prms = fn_params
    answer = {'type': "answer", 'function': fn_name, 'message': prms}
    self.my_errors_queue.put(answer)
    # log("[PUSH ANSWERS:]", answer)

  # Id reciever
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
    errormessage = {
      'id': reqId,
      'code': errorCode,
      'message': errorString
    }
    answer = {'type': "none", 'message': errormessage}
    if errormessage['id'] == -1:
      answer['type'] = "info"
    else:
      answer['type'] = "order_error"
    # log("[PUSH ERROR:]", answer)
    self.my_errors_queue.put(answer)

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
      log("[SERVER CLOCK:]", "Queue empty or request timed out")
      requested_time = None

    while self.wrapper.is_error():
      log("[SERVER CLOCK:]", self.wrapper.get_error(timeout=5))

    return requested_time


# Main Application class, automatically starts on init
class EjPiPi(Wrapper, ElCliento):
  # Main classes initialization
  # TODO: Nespoustet start() implicitne
  def __init__(self, ipaddress, portid, clientid, kveve):
    Wrapper.__init__(self, kveve)
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
  def order_create(action: str, quantity: float, order_type: str, aux_price: float):
    order = Order()
    order.action = action
    order.orderType = order_type
    order.auxPrice = aux_price
    order.totalQuantity = quantity
    return order

  # Ticker; Expirace; Typ; Strike; Smer; Mnozstvi
  def send_order(self, symbol, expiration, right, strike, action, quantity, price, order_type):
    counter = 0
    self.refresh_next_id()
    contract_object = self.contract_create(symbol, expiration, strike, right)
    order_object = self.order_create(action, quantity, order_type, price)
    self.placeOrder(self.next_id, contract_object, order_object)
    return self.next_id

  def refresh_next_id(self):
    self.next_id = 0
    self.reqIds(1)
    for i in range(10):
      if i < 10:
        if not self.next_id == 0:
          print("ID %d prirazeno" % self.next_id)
          return
        else:
          print("Ziskavam identifikator pro odeslani objednavky")
          time.sleep(1)
    raise TimeoutError("Nepodarilo se ziskat validni identifikator pro odeslani objednavky")
