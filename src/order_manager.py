from objednavky import Objednavka


class OrderManager:
  def __init__(self, tws_client, tws_queue):
    self.client = tws_client
    self.queue = tws_queue
    self.orderlist = []

  def updateOrders(self):
    queue = self.queue
    while not queue.empty():
      message_raw = queue.get()
      message = message_raw['message']
      print("     [RAW_MSG]:", message_raw)
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
      if order.status == "Cancelled" or order.status == "Filled" or order.status == "ERROR":
        print("Deleting dead order ", order)
        self.orderlist.remove(order)
      else:
        print(order)

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
