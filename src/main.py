import time
import datetime
import data
from tws import EjPiPi
from telegram import TgWrapper
import excel
import queue
import threading

# Globalni konstanty
MONTHS = {
  'Jan': "01",
  'Feb': "02",
  'Mar': "03",
  'Apr': "04",
  'May': "05",
  'Jun': "06",
  'Jul': "07",
  'Aug': "08",
  'Sep': "09",
  'Oct': "10",
  'Nov': "11",
  'Dec': "12"
}

# Hodnoty nemenne za chodu programu - konfigurace
tg_config = {
  'chat_id': -1001222852629,
  'api_id': 1281725,
  'api_hash': "6d5593e5f014de19ab29e96dec9c5fec"
}
excel_config = {
  'file': "/home/ktbsh/tmp/orders.xlsx"
}
tws_config = {
  'ip': "127.0.0.1",
  'port': 7497
}


# Custom funkce
def process_order(signal):
  if signal['operace'] == "open":
    print("sending order")
    tws_client.send_order(signal)
    data.db_set_position(signal)
    signal['vysledek'] = "Objednavka odeslana"
    signal['cas_zpracovani'] = datetime.datetime.now()


def transform_expiration(date):
  month = date[:3]
  day, year = date[3:].split("'")
  if int(day) < 10:
    day = "0%d" % int(day)
  return "20%s%s%s" % (year, MONTHS[month], day)


def transform_unixtime(unixdate):
  return unixdate


def parse_signal(signal):
  signal_text = signal['text']
  signal_date = signal['date']
  processed_signal = 0
  try:
    parts = signal_text.split()
    if parts[0] == u"\U0001F34F":  # jablko
      parts[0] = "open"
    elif parts[0] == u"\U0001F347":  # hrozen
      parts[0] = "close"
    processed_signal = {
      'operace': parts[0],  # Open/Close pro otevreni/uzavreni pozice
      'akce': parts[1],  # Go/Close - reserved
      'ticker': parts[2],  # Symbol
      'expirace': transform_expiration(parts[3]),  # Expirace ve formatu YYYYMMDD (String)
      'typ': parts[4].split("-")[0],  # Right (Call/Put)
      'strike': parts[4].split("-")[1],  # Hodnota strike
      'smer': parts[5],  # Action (BUY/SELL)
      'mnozstvi': parts[6],  # Quantity
      'cena': parts[9],  # Aktualni cena - reserved
      'puvodni_zprava': signal_text,
      'cas_zpravy': datetime.datetime.fromtimestamp(signal_date)
    }
  except:
    pass  # TODO: Pridat exception handling
  finally:
    return processed_signal


# Vytvorime pozici a z tws zjistime jeji ID, zapiseme do DB
def tws_position_open(params):
  print("OPENING POSITION")
  tws_client.send_order(params)


# Zkontrolujeme existenci odpovidajici pozice a podle jejiho ID zrusime
def tws_position_close(params):
  print("CLOSING POSITION")


# Fronty pro postupne zpracovani odpovedi serveru
tg_queue = queue.Queue()
ib_queue = queue.Queue()


# Instance klientu knihoven
def init_clients():
  tg_client = TgWrapper(tg_config, tg_queue).session
  tws_client = EjPiPi(tws_config['ip'], tws_config['port'], 0)
  return tg_client, tws_client


# # Hlavni event loop programu
if __name__ == "__main__":
  tg_client, tws_client = init_clients()
  tg_client.start()
  print(tws_client.server_clock())
  print(tws_client.await_id())

  while True:
    time.sleep(1)
    if not tg_queue.empty():
      raw_signal = tg_queue.get(timeout=5)
      signal_dict = parse_signal(raw_signal)
      signal_dict['nasobeni'] = 1
      process_order(signal_dict)
      data.db_append_history(signal_dict)

