from objednavky import Objednavka


class OrderManager:
  def __init__(self, tws_client, tws_queue):
    self.client = tws_client
    self.queue = tws_queue
    self.orderlist = []

  def updateOrders(self):
    queue = self.queue
    while not queue.empty():
      message = queue.get()
      print(message)
      if 'id' in message:
        for order in self.orderlist:
          if order['id'] == message['id']:
            order.updateStatus(message['message'])
      elif 'orderId' in message:
        for order in self.orderlist:
          if order['id'] == message['orderId']:
            order.updateStatus(message['message'])
      else:
        print(message)
    self.cleanUp()

  def cleanUp(self):
    for order in self.orderlist:
      if order['status'] == "Cancelled" or "Filled":
        print("Deleting dead order ", order)
        self.orderlist.remove(order)
      else:
        print(order['status'])

  def createOrder(self, signal):
    objednavka = Objednavka(signal, self.client)
    objednavka.execute()
    self.orderlist.append(objednavka)

  def isOrderPending(self, ticker, typ, strike):
    for order in self.orderlist:
      if order['ticker'] == ticker and order['typ'] == typ and order['strike'] == strike:
        return order['remaining']
      else:
        return 0
