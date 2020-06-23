from datetime import datetime


class Objednavka:
  def __init__(self, signal, tws_client):
    self.operace = signal['operace']
    self.ticker = signal['ticker']
    self.expirace = signal['expirace']
    self.typ = signal['typ']
    self.strike = signal['strike']
    self.smer = signal['smer']
    self.mnozstvi = signal['mnozstvi']
    self.cena = signal['cena']
    self.order_type = signal['order_type']
    self.client = tws_client
    self.order_id = 0
    self.time_created = datetime.now()
    self.status = ""

  def execute(self):
    client = self.client
    self.order_id = client.send_order(symbol=self.ticker, expiration=self.expirace, right=self.typ,
                                      strike=self.strike, action=self.smer, quantity=self.mnozstvi,
                                      price=self.cena, order_type=self.order_type)
    print("Order sent, got ID %d" % self.order_id)

  def updateStatus(self, message):
    print("Updating order %d" % self.order_id)
    print(message)
    self.status = message['status']

  def cancel(self):
    self.client.cancelOrder(self.order_id)
    self.status = "Cancelled"
