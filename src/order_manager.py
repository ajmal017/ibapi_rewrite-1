from objednavky import Objednavka
from datetime import datetime


class OrderManager:
  def __init__(self, tws_client, tws_queue):
    self.client = tws_client
    self.queue = tws_queue
    self.orderlist = []
    self.message = ""

  def printOrders(self):
    timestamp = '{0:%H:%M:%S}'.format(datetime.now())
    message = " _______________\n Stav objednavek: "
    for order in self.orderlist:
      message = message + "\n " + order.__str__()
    message = message + "\n _______________\n"
    if message != self.message:
      print("\n ", timestamp)
      print(message)
      self.message = message

  def updateOrders(self):
    queue = self.queue
    while not queue.empty():
      message_raw = queue.get()
      message = message_raw['message']
      print("     [RAW_MSG]:", message_raw) # TODO: send to some logger
      if 'id' in message:
        for order in self.orderlist:
          if order.order_id == message['id']:
            order.updateStatus(message)
      elif 'orderId' in message:
        for order in self.orderlist:
          if order.order_id == message['orderId']:
            order.updateStatus(message)
    self.cleanUp()

  def cleanUp(self):
    for order in self.orderlist:
      if order.status == "Cancelled" or order.status == "Filled" or order.status == "ERROR" or order.status == "Inactive":
        print("Odstranuji zpracovanou objednavku: ", order)
        self.orderlist.remove(order)

  def createOrder(self, signal):
    objednavka_new = Objednavka(signal, self.client)
    objednavka_old = self.isOrderPending(objednavka_new)
    if not objednavka_old:
      objednavka_new.execute()
      self.orderlist.append(objednavka_new)
    else:
      print("Konflikt otevrenych objednavek, rusim puvodni objednavku %s" % objednavka_old)
      objednavka_old.cancel()
      print("Ignoruji konfliktni objednavku %s" % objednavka_new)

  def isOrderPending(self, new_order):
    for order in self.orderlist:
      if new_order.compare() == order.compare() and new_order.smer != order.smer:
        return order
    return None
