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
      if 'id' in message:
        for order in self.orderlist:
          if order['id'] == message['id']:
            order.update(message)
      elif 'orderId' in message:
        for order in self.orderlist:
          if order['id'] == message['orderId']:
            order.update(message)
      else:
        print(message)

  def createOrder(self, signal):
    self.orderlist.append(Objednavka(signal, self.client))

  def isOrderPending(self, ticker, typ, strike):
    for order in self.orderlist:
      if order['ticker'] == ticker and order['typ'] == typ and order['strike'] == strike:
        return order['remaining']
      else:
        return 0
